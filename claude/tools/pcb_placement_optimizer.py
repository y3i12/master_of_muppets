#!/usr/bin/env python3
"""
PCB Placement Optimizer v1.0 - Intelligent component placement for Master of Muppets
Uses constraint-based optimization for optimal PCB layout
"""

import math
import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from kicad_pcb_parser import KiCadPCBParser, ComponentPlacement

@dataclass
class PlacementConstraint:
    """Define placement constraints between components"""
    component1: str
    component2: str
    min_distance: float
    max_distance: float
    constraint_type: str  # 'spacing', 'proximity', 'alignment'
    priority: int  # 1-10, higher = more important
    reason: str

@dataclass
class PlacementZone:
    """Define placement zones on the board"""
    name: str
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    allowed_components: List[str]  # Component types or references
    priority: int

class PCBPlacementOptimizer:
    """Optimize component placement using constraint-based approach"""
    
    def __init__(self, pcb_parser: KiCadPCBParser):
        self.parser = pcb_parser
        self.constraints: List[PlacementConstraint] = []
        self.zones: List[PlacementZone] = []
        self.optimized_positions: Dict[str, ComponentPlacement] = {}
        
        self._setup_master_of_muppets_constraints()
        self._setup_placement_zones()
    
    def _setup_master_of_muppets_constraints(self):
        """Set up constraints specific to Master of Muppets"""
        
        # Jack spacing constraints (critical for mechanical fit)
        self.constraints.extend([
            PlacementConstraint("J*", "J*", 19.05, 25.0, "spacing", 10, 
                               "Jack minimum spacing for panel mount"),
            PlacementConstraint("J*", "board_edge", 0.0, 5.0, "proximity", 9,
                               "Jacks must be at board edge"),
        ])
        
        # Microcontroller proximity constraints
        self.constraints.extend([
            PlacementConstraint("T1", "DAC*", 0.0, 50.0, "proximity", 8,
                               "Keep DACs close to microcontroller for I2C"),
            PlacementConstraint("T1", "board_edge", 10.0, 999.0, "spacing", 7,
                               "Keep microcontroller away from edges for connector access"),
        ])
        
        # DAC to OpAmp constraints (signal integrity)
        self.constraints.extend([
            PlacementConstraint("DAC1", "U1", 0.0, 15.0, "proximity", 8,
                               "DAC1 outputs to U1 OpAmps"),
            PlacementConstraint("DAC1", "U2", 0.0, 15.0, "proximity", 8,
                               "DAC1 outputs to U2 OpAmps"),
            PlacementConstraint("DAC2", "U3", 0.0, 15.0, "proximity", 8,
                               "DAC2 outputs to U3 OpAmps"),
            PlacementConstraint("DAC2", "U4", 0.0, 15.0, "proximity", 8,
                               "DAC2 outputs to U4 OpAmps"),
        ])
        
        # OpAmp to Jack constraints (minimize analog traces)
        for i in range(1, 17):  # 16 CV outputs
            opamp_num = ((i - 1) // 4) + 1
            jack_ref = f"J{i + 1}"  # J2-J17 (J1 is USB)
            opamp_ref = f"U{opamp_num}"
            
            self.constraints.append(
                PlacementConstraint(opamp_ref, jack_ref, 0.0, 30.0, "proximity", 7,
                                  f"OpAmp {opamp_ref} to output jack {jack_ref}")
            )
        
        # Decoupling capacitor constraints
        for dac_ref in ["DAC1", "DAC2"]:
            self.constraints.append(
                PlacementConstraint(dac_ref, f"C*_{dac_ref}", 0.0, 3.0, "proximity", 9,
                                  f"Decoupling caps close to {dac_ref}")
            )
        
        # Power distribution constraints
        self.constraints.extend([
            PlacementConstraint("power_input", "regulator", 0.0, 20.0, "proximity", 8,
                               "Power input close to regulator"),
            PlacementConstraint("regulator", "power_caps", 0.0, 10.0, "proximity", 8,
                               "Power filtering caps close to regulator"),
        ])
    
    def _setup_placement_zones(self):
        """Define placement zones for different component types"""
        
        # Assume 100x160mm board (Eurocard format)
        board_width = 100.0
        board_height = 160.0
        
        # Jack zone - right edge for panel mounting
        self.zones.append(PlacementZone(
            name="jack_zone",
            x_min=board_width - 20.0, y_min=10.0,
            x_max=board_width - 5.0, y_max=board_height - 10.0,
            allowed_components=["jack"],
            priority=10
        ))
        
        # Power zone - top left
        self.zones.append(PlacementZone(
            name="power_zone", 
            x_min=0.0, y_min=0.0,
            x_max=30.0, y_max=30.0,
            allowed_components=["regulator", "power_input", "power_caps"],
            priority=8
        ))
        
        # Digital zone - left side for microcontroller
        self.zones.append(PlacementZone(
            name="digital_zone",
            x_min=5.0, y_min=40.0,
            x_max=40.0, y_max=120.0,
            allowed_components=["microcontroller", "digital_caps"],
            priority=9
        ))
        
        # Analog zone - center for DACs and OpAmps
        self.zones.append(PlacementZone(
            name="analog_zone",
            x_min=30.0, y_min=20.0,
            x_max=75.0, y_max=140.0,
            allowed_components=["dac", "opamp", "analog_caps", "resistor"],
            priority=8
        ))
    
    def categorize_component(self, comp: ComponentPlacement) -> str:
        """Categorize component for zone assignment"""
        ref = comp.reference.lower()
        footprint = comp.footprint.lower()
        
        if ref.startswith('j') and 'jack' in footprint:
            return 'jack'
        elif ref == 't1' or 'teensy' in footprint:
            return 'microcontroller'
        elif ref.startswith('dac') or 'tssop' in footprint:
            return 'dac'
        elif ref.startswith('u') and 'soic' in footprint:
            return 'opamp'
        elif ref.startswith('c'):
            return 'analog_caps'
        elif ref.startswith('r'):
            return 'resistor'
        else:
            return 'other'
    
    def calculate_placement_score(self, positions: Dict[str, ComponentPlacement]) -> float:
        """Calculate placement quality score based on constraints"""
        
        total_score = 0.0
        total_weight = 0.0
        
        for constraint in self.constraints:
            score, weight = self._evaluate_constraint(constraint, positions)
            total_score += score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _evaluate_constraint(self, constraint: PlacementConstraint, 
                           positions: Dict[str, ComponentPlacement]) -> Tuple[float, float]:
        """Evaluate a single constraint and return (score, weight)"""
        
        # Find matching components for constraint
        comp1_matches = self._find_matching_components(constraint.component1, positions)
        comp2_matches = self._find_matching_components(constraint.component2, positions)
        
        if not comp1_matches or not comp2_matches:
            return (0.0, 0.0)  # Cannot evaluate
        
        scores = []
        for comp1_ref in comp1_matches:
            for comp2_ref in comp2_matches:
                if comp1_ref == comp2_ref:
                    continue
                
                comp1 = positions[comp1_ref]
                comp2 = positions[comp2_ref]
                distance = comp1.distance_to(comp2)
                
                # Score based on constraint type
                if constraint.constraint_type == "proximity":
                    if distance <= constraint.max_distance:
                        scores.append(1.0)
                    else:
                        scores.append(max(0.0, 1.0 - (distance - constraint.max_distance) / 50.0))
                
                elif constraint.constraint_type == "spacing":
                    if distance >= constraint.min_distance:
                        scores.append(1.0)
                    else:
                        scores.append(max(0.0, distance / constraint.min_distance))
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        weight = constraint.priority
        
        return (avg_score, weight)
    
    def _find_matching_components(self, pattern: str, 
                                positions: Dict[str, ComponentPlacement]) -> List[str]:
        """Find components matching a pattern (supports wildcards)"""
        
        if pattern == "board_edge":
            return []  # Special case, handled separately
        
        matches = []
        for ref in positions.keys():
            if pattern.endswith('*'):
                if ref.startswith(pattern[:-1]):
                    matches.append(ref)
            elif pattern.startswith('*'):
                if ref.endswith(pattern[1:]):
                    matches.append(ref)
            elif pattern == ref:
                matches.append(ref)
        
        return matches
    
    def optimize_placement(self, iterations: int = 100) -> Dict[str, ComponentPlacement]:
        """Run placement optimization algorithm"""
        
        print(f"[OPT] Starting placement optimization ({iterations} iterations)...")
        
        # Start with current positions
        current_positions = dict(self.parser.components)
        best_positions = dict(current_positions)
        best_score = self.calculate_placement_score(current_positions)
        
        print(f"[OPT] Initial score: {best_score:.3f}")
        
        # Simple iterative improvement
        for iteration in range(iterations):
            # Try moving a random component
            test_positions = dict(current_positions)
            
            # Select component to move (prefer components with violations)
            component_refs = list(test_positions.keys())
            if component_refs:
                ref_to_move = component_refs[iteration % len(component_refs)]
                comp = test_positions[ref_to_move]
                
                # Try new position based on zone preferences
                category = self.categorize_component(comp)
                preferred_zones = [z for z in self.zones if category in z.allowed_components]
                
                if preferred_zones:
                    zone = preferred_zones[0]  # Use highest priority zone
                    # Random position within zone
                    import random
                    new_x = random.uniform(zone.x_min, zone.x_max)
                    new_y = random.uniform(zone.y_min, zone.y_max)
                    
                    test_positions[ref_to_move] = ComponentPlacement(
                        reference=comp.reference,
                        footprint=comp.footprint,
                        x=new_x,
                        y=new_y,
                        rotation=comp.rotation,
                        layer=comp.layer,
                        locked=comp.locked
                    )
                    
                    # Evaluate new score
                    new_score = self.calculate_placement_score(test_positions)
                    
                    if new_score > best_score:
                        best_positions = dict(test_positions)
                        best_score = new_score
                        current_positions = dict(test_positions)
                        print(f"[OPT] Iteration {iteration}: New best score {best_score:.3f}")
        
        print(f"[OPT] Final score: {best_score:.3f}")
        self.optimized_positions = best_positions
        return best_positions
    
    def generate_placement_commands(self) -> List[str]:
        """Generate KiCad placement commands for optimized positions"""
        
        commands = []
        commands.append("# Optimized component placement commands")
        commands.append("# Apply these in KiCad PCB editor")
        commands.append("")
        
        for ref, comp in self.optimized_positions.items():
            original = self.parser.components.get(ref)
            if original and (abs(comp.x - original.x) > 0.1 or abs(comp.y - original.y) > 0.1):
                commands.append(f"# Move {ref} from ({original.x:.1f}, {original.y:.1f}) to ({comp.x:.1f}, {comp.y:.1f})")
                commands.append(f"select {ref}")
                commands.append(f"move {comp.x:.3f} {comp.y:.3f}")
                if comp.rotation != original.rotation:
                    commands.append(f"rotate {comp.rotation:.1f}")
                commands.append("")
        
        return commands
    
    def export_optimization_report(self, output_file: str):
        """Export detailed optimization report"""
        
        original_score = self.calculate_placement_score(self.parser.components)
        optimized_score = self.calculate_placement_score(self.optimized_positions)
        
        report_data = {
            'optimization_summary': {
                'original_score': original_score,
                'optimized_score': optimized_score,
                'improvement': optimized_score - original_score,
                'improvement_percent': ((optimized_score - original_score) / original_score * 100) if original_score > 0 else 0
            },
            'constraints': [asdict(c) for c in self.constraints],
            'zones': [asdict(z) for z in self.zones],
            'component_moves': []
        }
        
        # Document component moves
        for ref, comp in self.optimized_positions.items():
            original = self.parser.components.get(ref)
            if original and (abs(comp.x - original.x) > 0.1 or abs(comp.y - original.y) > 0.1):
                report_data['component_moves'].append({
                    'reference': ref,
                    'original_position': (original.x, original.y),
                    'optimized_position': (comp.x, comp.y),
                    'distance_moved': original.distance_to(comp),
                    'category': self.categorize_component(comp)
                })
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"[OPT] Optimization report exported to {output_file}")

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python pcb_placement_optimizer.py <pcb_file>")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    parser = KiCadPCBParser(pcb_file)
    optimizer = PCBPlacementOptimizer(parser)
    
    # Run optimization
    optimized = optimizer.optimize_placement(iterations=50)
    
    # Generate outputs
    commands = optimizer.generate_placement_commands()
    
    print("\n=== PLACEMENT OPTIMIZATION COMMANDS ===")
    for cmd in commands[:20]:  # Show first 20 commands
        print(cmd)
    
    if len(commands) > 20:
        print(f"... and {len(commands) - 20} more commands")
    
    # Export detailed report
    base_name = Path(pcb_file).stem
    optimizer.export_optimization_report(f"{base_name}_optimization_report.json")