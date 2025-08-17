#!/usr/bin/env python3
"""
AI-Enhanced Component Placement Optimizer
Cognitive placement algorithms with learning and optimization
"""

import math
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Component:
    reference: str
    package: str
    value: str
    x: float
    y: float
    rotation: float
    layer: str
    area: float
    thermal_rating: float = 0.0
    critical_timing: bool = False

@dataclass
class Connection:
    from_ref: str
    to_ref: str
    net_name: str
    pin_from: str
    pin_to: str
    weight: float = 1.0  # Routing priority weight
    length_estimate: float = 0.0

@dataclass
class PlacementResult:
    components: List[Component]
    total_wire_length: float
    thermal_score: float
    timing_score: float
    congestion_score: float
    overall_score: float
    improvements: List[str]

class CognitivePlacementEngine:
    """AI-enhanced component placement with learning"""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.learning_cache = {}
        self.placement_patterns = {}
        self.load_placement_knowledge()
    
    def load_placement_knowledge(self):
        """Load learned placement patterns and optimizations"""
        knowledge_file = self.project_path / "claude" / "brain_systems" / "placement_knowledge.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    self.placement_patterns = data.get('patterns', {})
                    self.learning_cache = data.get('cache', {})
            except Exception:
                # Initialize empty knowledge base
                self.placement_patterns = {
                    'power_distribution': {
                        'decoupling_caps_near_ics': 0.95,
                        'power_components_edge': 0.85,
                        'minimize_power_loops': 0.90
                    },
                    'signal_integrity': {
                        'high_speed_short_traces': 0.95,
                        'differential_pairs_matched': 0.90,
                        'analog_digital_separation': 0.85
                    },
                    'thermal_management': {
                        'hot_components_spaced': 0.80,
                        'thermal_vias_under_ics': 0.75,
                        'airflow_consideration': 0.70
                    },
                    'manufacturing': {
                        'component_density_optimal': 0.85,
                        'pick_place_efficiency': 0.80,
                        'test_point_access': 0.75
                    }
                }
    
    def save_placement_knowledge(self):
        """Save learned patterns for future optimization"""
        knowledge_file = self.project_path / "claude" / "brain_systems" / "placement_knowledge.json"
        knowledge_file.parent.mkdir(exist_ok=True, parents=True)
        
        data = {
            'patterns': self.placement_patterns,
            'cache': self.learning_cache,
            'version': '1.0',
            'last_updated': str(Path(__file__).stat().st_mtime)
        }
        
        try:
            with open(knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[PLACEMENT] Knowledge save error: {e}")
    
    def analyze_current_placement(self, components: List[Component], 
                                connections: List[Connection]) -> Dict[str, float]:
        """Analyze current placement for optimization opportunities"""
        analysis = {
            'wire_length_total': 0.0,
            'thermal_hotspots': 0.0,
            'timing_violations': 0.0,
            'congestion_score': 0.0,
            'power_loop_area': 0.0
        }
        
        # Calculate total wire length estimation
        total_length = 0.0
        for conn in connections:
            from_comp = next((c for c in components if c.reference == conn.from_ref), None)
            to_comp = next((c for c in components if c.reference == conn.to_ref), None)
            
            if from_comp and to_comp:
                dx = to_comp.x - from_comp.x
                dy = to_comp.y - from_comp.y
                length = math.sqrt(dx*dx + dy*dy)
                total_length += length * conn.weight
                conn.length_estimate = length
        
        analysis['wire_length_total'] = total_length
        
        # Thermal analysis - components too close
        thermal_violations = 0
        for i, comp1 in enumerate(components):
            if comp1.thermal_rating > 1.0:  # Hot component
                for comp2 in components[i+1:]:
                    dx = comp2.x - comp1.x  
                    dy = comp2.y - comp1.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    min_distance = 5.0 + comp1.thermal_rating * 2.0  # mm
                    if distance < min_distance:
                        thermal_violations += 1
        
        analysis['thermal_hotspots'] = thermal_violations
        
        # Timing analysis - critical paths
        timing_violations = 0
        for conn in connections:
            if conn.length_estimate > 20.0:  # mm - high speed threshold
                # Check if involves critical timing components
                from_comp = next((c for c in components if c.reference == conn.from_ref), None)
                to_comp = next((c for c in components if c.reference == conn.to_ref), None)
                
                if (from_comp and from_comp.critical_timing) or (to_comp and to_comp.critical_timing):
                    timing_violations += 1
        
        analysis['timing_violations'] = timing_violations
        
        return analysis
    
    def optimize_placement(self, components: List[Component], 
                         connections: List[Connection], 
                         board_constraints: Dict[str, Any] = None) -> PlacementResult:
        """AI-enhanced placement optimization with cognitive learning"""
        
        if board_constraints is None:
            board_constraints = {
                'width': 100.0,
                'height': 80.0,
                'keep_out_zones': [],
                'manufacturing_rules': 'aisler_2l_enig'
            }
        
        print("[PLACEMENT] Starting AI-enhanced placement optimization...")
        
        # Phase 1: Analyze current placement
        current_analysis = self.analyze_current_placement(components, connections)
        print(f"[PLACEMENT] Current wire length: {current_analysis['wire_length_total']:.1f}mm")
        print(f"[PLACEMENT] Thermal hotspots: {current_analysis['thermal_hotspots']}")
        print(f"[PLACEMENT] Timing violations: {current_analysis['timing_violations']}")
        
        # Phase 2: Apply cognitive placement patterns
        optimized_components = self._apply_placement_patterns(components, connections, board_constraints)
        
        # Phase 3: Iterative optimization using learned patterns
        optimized_components = self._iterative_optimization(optimized_components, connections, board_constraints)
        
        # Phase 4: Final analysis
        final_analysis = self.analyze_current_placement(optimized_components, connections)
        
        # Calculate improvement scores
        wire_length_improvement = max(0, current_analysis['wire_length_total'] - final_analysis['wire_length_total'])
        thermal_improvement = max(0, current_analysis['thermal_hotspots'] - final_analysis['thermal_hotspots'])
        timing_improvement = max(0, current_analysis['timing_violations'] - final_analysis['timing_violations'])
        
        improvements = []
        if wire_length_improvement > 0:
            improvement_pct = (wire_length_improvement / current_analysis['wire_length_total']) * 100
            improvements.append(f"Wire length reduced by {improvement_pct:.1f}%")
        
        if thermal_improvement > 0:
            improvements.append(f"Thermal hotspots reduced by {thermal_improvement}")
        
        if timing_improvement > 0:
            improvements.append(f"Timing violations reduced by {timing_improvement}")
        
        # Calculate overall score
        wire_score = max(0, 100 - (final_analysis['wire_length_total'] / 10))  # Penalty per 10mm
        thermal_score = max(0, 100 - (final_analysis['thermal_hotspots'] * 10))  # 10 point penalty per hotspot
        timing_score = max(0, 100 - (final_analysis['timing_violations'] * 15))  # 15 point penalty per violation
        
        overall_score = (wire_score + thermal_score + timing_score) / 3
        
        result = PlacementResult(
            components=optimized_components,
            total_wire_length=final_analysis['wire_length_total'],
            thermal_score=thermal_score,
            timing_score=timing_score,
            congestion_score=80.0,  # Placeholder for routing congestion
            overall_score=overall_score,
            improvements=improvements
        )
        
        # Learn from this optimization
        self._learn_from_optimization(current_analysis, final_analysis, improvements)
        
        print(f"[PLACEMENT] Optimization complete. Overall score: {overall_score:.1f}/100")
        return result
    
    def _apply_placement_patterns(self, components: List[Component], 
                                connections: List[Connection],
                                board_constraints: Dict[str, Any]) -> List[Component]:
        """Apply learned placement patterns"""
        optimized = components.copy()
        
        # Pattern 1: Power distribution optimization
        power_components = [c for c in optimized if 'power' in c.value.lower() or 'supply' in c.reference.lower()]
        for comp in power_components:
            # Move power components to board edges for better thermal management
            if comp.x < board_constraints['width'] * 0.3:
                comp.x = 5.0  # Near left edge
            elif comp.x > board_constraints['width'] * 0.7:
                comp.x = board_constraints['width'] - 5.0  # Near right edge
        
        # Pattern 2: Decoupling capacitor placement
        decoupling_caps = [c for c in optimized if c.reference.startswith('C') and '100n' in c.value]
        ics = [c for c in optimized if c.reference.startswith('U') or c.reference.startswith('IC')]
        
        for cap in decoupling_caps:
            # Find nearest IC
            nearest_ic = None
            min_distance = float('inf')
            
            for ic in ics:
                dx = ic.x - cap.x
                dy = ic.y - cap.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < min_distance:
                    min_distance = distance
                    nearest_ic = ic
            
            if nearest_ic:
                # Place decoupling cap close to IC
                offset_x = 3.0 if cap.x < nearest_ic.x else -3.0
                offset_y = 2.0 if cap.y < nearest_ic.y else -2.0
                cap.x = nearest_ic.x + offset_x
                cap.y = nearest_ic.y + offset_y
        
        # Pattern 3: High-speed signal grouping
        critical_components = [c for c in optimized if c.critical_timing]
        if len(critical_components) > 1:
            # Group critical components together
            center_x = sum(c.x for c in critical_components) / len(critical_components)
            center_y = sum(c.y for c in critical_components) / len(critical_components)
            
            for i, comp in enumerate(critical_components):
                angle = (i / len(critical_components)) * 2 * math.pi
                radius = 8.0  # mm - tight grouping
                comp.x = center_x + radius * math.cos(angle)
                comp.y = center_y + radius * math.sin(angle)
        
        return optimized
    
    def _iterative_optimization(self, components: List[Component], 
                              connections: List[Connection],
                              board_constraints: Dict[str, Any],
                              iterations: int = 5) -> List[Component]:
        """Iterative placement optimization using genetic algorithm concepts"""
        current_best = components.copy()
        best_score = self._calculate_placement_score(current_best, connections)
        
        for iteration in range(iterations):
            # Create variations by small movements
            candidate = current_best.copy()
            
            # Select random components to optimize
            import random
            components_to_move = random.sample(candidate, min(len(candidate), 5))
            
            for comp in components_to_move:
                # Small random movement
                comp.x += random.uniform(-2.0, 2.0)
                comp.y += random.uniform(-2.0, 2.0)
                
                # Keep within board bounds
                comp.x = max(5.0, min(board_constraints['width'] - 5.0, comp.x))
                comp.y = max(5.0, min(board_constraints['height'] - 5.0, comp.y))
            
            # Evaluate candidate
            candidate_score = self._calculate_placement_score(candidate, connections)
            
            if candidate_score > best_score:
                current_best = candidate
                best_score = candidate_score
                print(f"[PLACEMENT] Iteration {iteration + 1}: Score improved to {best_score:.1f}")
        
        return current_best
    
    def _calculate_placement_score(self, components: List[Component], 
                                 connections: List[Connection]) -> float:
        """Calculate placement quality score"""
        analysis = self.analyze_current_placement(components, connections)
        
        # Weighted scoring
        wire_penalty = analysis['wire_length_total'] * 0.1
        thermal_penalty = analysis['thermal_hotspots'] * 20
        timing_penalty = analysis['timing_violations'] * 30
        
        base_score = 1000.0
        total_penalty = wire_penalty + thermal_penalty + timing_penalty
        
        return max(0, base_score - total_penalty)
    
    def _learn_from_optimization(self, before: Dict[str, float], 
                               after: Dict[str, float], 
                               improvements: List[str]):
        """Learn from optimization results for future improvements"""
        learning_key = f"opt_{len(self.learning_cache)}"
        
        learning_entry = {
            'before_score': sum(before.values()),
            'after_score': sum(after.values()),
            'improvement_ratio': sum(after.values()) / max(1, sum(before.values())),
            'improvements': improvements,
            'patterns_applied': list(self.placement_patterns.keys())
        }
        
        self.learning_cache[learning_key] = learning_entry
        
        # Update pattern effectiveness
        if learning_entry['improvement_ratio'] > 1.1:  # 10% improvement
            for pattern_category in self.placement_patterns:
                for pattern_name, effectiveness in self.placement_patterns[pattern_category].items():
                    # Slightly increase effectiveness for successful patterns
                    self.placement_patterns[pattern_category][pattern_name] = min(1.0, effectiveness + 0.01)
        
        # Save learned knowledge
        self.save_placement_knowledge()

def create_test_placement_scenario():
    """Create test scenario for placement optimization"""
    components = [
        Component("U1", "QFP-44", "STM32F4", 30, 30, 0, "F.Cu", 100, 2.5, True),
        Component("U2", "SOIC-8", "AD5593R", 60, 20, 0, "F.Cu", 25, 1.5),
        Component("U3", "SOIC-8", "AD5593R", 60, 40, 0, "F.Cu", 25, 1.5),
        Component("C1", "0805", "100nF", 45, 35, 0, "F.Cu", 4),
        Component("C2", "0805", "100nF", 75, 25, 0, "F.Cu", 4),
        Component("C3", "0805", "100nF", 75, 35, 0, "F.Cu", 4),
        Component("R1", "0805", "10k", 20, 20, 0, "F.Cu", 4),
        Component("R2", "0805", "10k", 20, 40, 0, "F.Cu", 4),
    ]
    
    connections = [
        Connection("U1", "C1", "VCC", "VCC", "1", 3.0),
        Connection("U1", "U2", "SDA", "PA9", "SDA", 2.0),
        Connection("U1", "U3", "SCL", "PA8", "SCL", 2.0),
        Connection("U2", "C2", "VCC", "VCC", "1", 3.0),
        Connection("U3", "C3", "VCC", "VCC", "1", 3.0),
        Connection("U1", "R1", "RESET", "NRST", "1", 1.0),
        Connection("U1", "R2", "BOOT", "BOOT0", "1", 1.0),
    ]
    
    return components, connections

if __name__ == "__main__":
    # Test AI placement optimizer
    print("AI-Enhanced Placement Optimizer Test")
    print("=" * 50)
    
    engine = CognitivePlacementEngine()
    components, connections = create_test_placement_scenario()
    
    result = engine.optimize_placement(components, connections)
    
    print(f"\nOptimization Results:")
    print(f"Overall Score: {result.overall_score:.1f}/100")
    print(f"Wire Length: {result.total_wire_length:.1f}mm")
    print(f"Thermal Score: {result.thermal_score:.1f}/100")
    print(f"Timing Score: {result.timing_score:.1f}/100")
    
    if result.improvements:
        print(f"\nImprovements:")
        for improvement in result.improvements:
            print(f"  - {improvement}")
    else:
        print(f"\nNo significant improvements found")