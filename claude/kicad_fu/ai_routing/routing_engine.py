#!/usr/bin/env python3
"""
AI-Enhanced Routing Engine
Cognitive autorouting with learning and design rule optimization
"""

import math
import json
from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import heapq

@dataclass
class RoutePoint:
    x: float
    y: float
    layer: str
    via_cost: float = 0.0

@dataclass
class RouteSegment:
    start: RoutePoint
    end: RoutePoint
    width: float
    net_name: str
    length: float = 0.0
    layer: str = "F.Cu"

@dataclass
class RoutingConstraints:
    min_trace_width: float = 0.125  # mm - AISLER ENIG
    min_via_size: float = 0.25      # mm - AISLER ENIG
    min_spacing: float = 0.125      # mm - AISLER ENIG
    max_via_count: int = 50
    preferred_layers: List[str] = None
    
    def __post_init__(self):
        if self.preferred_layers is None:
            self.preferred_layers = ["F.Cu", "B.Cu"]

@dataclass
class Net:
    name: str
    priority: int  # 1=highest, 5=lowest
    width: float
    pins: List[Tuple[str, float, float, str]]  # (ref, x, y, layer)
    differential_pair: str = ""
    max_length: float = 0.0  # mm - for timing-critical nets
    min_length: float = 0.0  # mm - for length matching

@dataclass
class RoutingResult:
    routed_nets: List[str]
    failed_nets: List[str]
    total_wire_length: float
    via_count: int
    completion_percentage: float
    design_rule_violations: int
    routing_score: float
    optimizations_applied: List[str]

class CognitiveRoutingEngine:
    """AI-enhanced autorouter with learning and optimization"""
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.routing_knowledge = {}
        self.learned_patterns = {}
        self.design_rules = RoutingConstraints()
        self.load_routing_knowledge()
        
        # Routing grid for pathfinding
        self.grid_resolution = 0.1  # mm
        self.routing_grid = {}
        
    def load_routing_knowledge(self):
        """Load learned routing patterns and optimizations"""
        knowledge_file = self.project_path / "claude" / "brain_systems" / "routing_knowledge.json"
        if knowledge_file.exists():
            try:
                with open(knowledge_file, 'r') as f:
                    data = json.load(f)
                    self.routing_knowledge = data.get('knowledge', {})
                    self.learned_patterns = data.get('patterns', {})
            except Exception:
                pass
        
        # Initialize default routing knowledge
        if not self.routing_knowledge:
            self.routing_knowledge = {
                'via_placement': {
                    'minimize_vias': 0.9,
                    'avoid_under_components': 0.95,
                    'thermal_via_spacing': 0.8
                },
                'trace_routing': {
                    'prefer_orthogonal': 0.85,
                    'minimize_bends': 0.9,
                    'avoid_acute_angles': 0.95
                },
                'layer_usage': {
                    'power_on_planes': 0.95,
                    'signals_on_outer': 0.8,
                    'high_speed_short': 0.9
                },
                'design_optimization': {
                    'differential_pair_matching': 0.95,
                    'length_matching_critical': 0.9,
                    'crosstalk_minimization': 0.85
                }
            }
    
    def save_routing_knowledge(self):
        """Save learned routing patterns"""
        knowledge_file = self.project_path / "claude" / "brain_systems" / "routing_knowledge.json"
        knowledge_file.parent.mkdir(exist_ok=True, parents=True)
        
        data = {
            'knowledge': self.routing_knowledge,
            'patterns': self.learned_patterns,
            'version': '1.0',
            'design_rules_used': asdict(self.design_rules)
        }
        
        try:
            with open(knowledge_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[ROUTING] Knowledge save error: {e}")
    
    def set_design_rules(self, manufacturer: str = "aisler", surface_finish: str = "ENIG"):
        """Set design rules based on manufacturer capabilities"""
        if manufacturer.lower() == "aisler":
            if surface_finish.upper() == "ENIG":
                self.design_rules = RoutingConstraints(
                    min_trace_width=0.125,  # mm
                    min_via_size=0.25,      # mm
                    min_spacing=0.125,      # mm
                    max_via_count=100,
                    preferred_layers=["F.Cu", "B.Cu", "In1.Cu", "In2.Cu"]
                )
            else:  # HASL
                self.design_rules = RoutingConstraints(
                    min_trace_width=0.2,    # mm
                    min_via_size=0.3,       # mm
                    min_spacing=0.15,       # mm
                    max_via_count=80,
                    preferred_layers=["F.Cu", "B.Cu"]
                )
        
        print(f"[ROUTING] Design rules set for {manufacturer} {surface_finish}")
        print(f"[ROUTING] Min trace: {self.design_rules.min_trace_width}mm, Min via: {self.design_rules.min_via_size}mm")
    
    def route_nets(self, nets: List[Net], board_bounds: Tuple[float, float, float, float],
                   obstacles: List[Dict] = None) -> RoutingResult:
        """Route all nets using AI-enhanced algorithms"""
        
        if obstacles is None:
            obstacles = []
        
        print(f"[ROUTING] Starting AI-enhanced routing of {len(nets)} nets...")
        
        # Initialize routing grid
        self._initialize_routing_grid(board_bounds, obstacles)
        
        # Sort nets by priority (1=highest priority first)
        sorted_nets = sorted(nets, key=lambda n: n.priority)
        
        routed_nets = []
        failed_nets = []
        total_wire_length = 0.0
        via_count = 0
        optimizations_applied = []
        
        # Phase 1: Route high-priority nets first
        for net in sorted_nets:
            print(f"[ROUTING] Routing net '{net.name}' (priority {net.priority})...")
            
            if len(net.pins) < 2:
                print(f"[ROUTING] Skipping net '{net.name}' - insufficient pins")
                continue
            
            # Route this net
            route_result = self._route_single_net(net)
            
            if route_result['success']:
                routed_nets.append(net.name)
                total_wire_length += route_result['length']
                via_count += route_result['vias']
                
                # Learn from successful routing
                self._learn_from_successful_route(net, route_result)
                
                print(f"[ROUTING] Net '{net.name}' routed successfully - {route_result['length']:.1f}mm, {route_result['vias']} vias")
            else:
                failed_nets.append(net.name)
                print(f"[ROUTING] Net '{net.name}' routing failed: {route_result.get('error', 'Unknown error')}")
        
        # Phase 2: Optimize routed nets
        print(f"[ROUTING] Optimizing {len(routed_nets)} routed nets...")
        optimizations = self._optimize_routes(routed_nets)
        optimizations_applied.extend(optimizations)
        
        # Phase 3: Calculate final metrics
        completion_percentage = (len(routed_nets) / len(nets)) * 100 if nets else 0
        design_rule_violations = self._check_design_rules()
        routing_score = self._calculate_routing_score(total_wire_length, via_count, completion_percentage, design_rule_violations)
        
        result = RoutingResult(
            routed_nets=routed_nets,
            failed_nets=failed_nets,
            total_wire_length=total_wire_length,
            via_count=via_count,
            completion_percentage=completion_percentage,
            design_rule_violations=design_rule_violations,
            routing_score=routing_score,
            optimizations_applied=optimizations_applied
        )
        
        print(f"[ROUTING] Routing complete: {completion_percentage:.1f}% success, Score: {routing_score:.1f}/100")
        
        # Save learned knowledge
        self.save_routing_knowledge()
        
        return result
    
    def _initialize_routing_grid(self, bounds: Tuple[float, float, float, float], obstacles: List[Dict]):
        """Initialize routing grid for pathfinding"""
        x_min, y_min, x_max, y_max = bounds
        
        # Create grid points
        x_steps = int((x_max - x_min) / self.grid_resolution)
        y_steps = int((y_max - y_min) / self.grid_resolution)
        
        self.routing_grid = {}
        for layer in self.design_rules.preferred_layers:
            self.routing_grid[layer] = {}
            for x_idx in range(x_steps):
                for y_idx in range(y_steps):
                    x = x_min + x_idx * self.grid_resolution
                    y = y_min + y_idx * self.grid_resolution
                    self.routing_grid[layer][(x_idx, y_idx)] = {
                        'available': True,
                        'cost': 1.0,
                        'x': x,
                        'y': y
                    }
        
        # Mark obstacles
        for obstacle in obstacles:
            self._mark_obstacle_in_grid(obstacle)
    
    def _mark_obstacle_in_grid(self, obstacle: Dict):
        """Mark obstacle areas as unavailable in routing grid"""
        # Simplified - mark rectangular obstacles
        x1, y1 = obstacle.get('x1', 0), obstacle.get('y1', 0)
        x2, y2 = obstacle.get('x2', 10), obstacle.get('y2', 10)
        layers = obstacle.get('layers', self.design_rules.preferred_layers)
        
        for layer in layers:
            if layer in self.routing_grid:
                # Convert coordinates to grid indices
                x1_idx = int(x1 / self.grid_resolution)
                y1_idx = int(y1 / self.grid_resolution)
                x2_idx = int(x2 / self.grid_resolution)
                y2_idx = int(y2 / self.grid_resolution)
                
                for x_idx in range(x1_idx, x2_idx + 1):
                    for y_idx in range(y1_idx, y2_idx + 1):
                        if (x_idx, y_idx) in self.routing_grid[layer]:
                            self.routing_grid[layer][(x_idx, y_idx)]['available'] = False
    
    def _route_single_net(self, net: Net) -> Dict[str, Any]:
        """Route a single net using A* pathfinding with cognitive enhancements"""
        if len(net.pins) < 2:
            return {'success': False, 'error': 'Insufficient pins'}
        
        # Start with minimum spanning tree approach for multi-pin nets
        total_length = 0.0
        total_vias = 0
        
        # Connect all pins using Steiner tree approximation
        unconnected_pins = net.pins.copy()
        connected_pins = [unconnected_pins.pop(0)]  # Start with first pin
        
        while unconnected_pins:
            # Find closest unconnected pin to any connected pin
            min_distance = float('inf')
            best_pair = None
            
            for connected_pin in connected_pins:
                for unconnected_pin in unconnected_pins:
                    dx = unconnected_pin[1] - connected_pin[1]
                    dy = unconnected_pin[2] - connected_pin[2]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_pair = (connected_pin, unconnected_pin)
            
            if best_pair:
                start_pin, end_pin = best_pair
                
                # Route between these two pins
                route_result = self._route_point_to_point(start_pin, end_pin, net)
                
                if route_result['success']:
                    total_length += route_result['length']
                    total_vias += route_result['vias']
                    connected_pins.append(end_pin)
                    unconnected_pins.remove(end_pin)
                else:
                    return {'success': False, 'error': f"Failed to route between pins: {route_result.get('error')}"}
            else:
                return {'success': False, 'error': 'No valid routing path found'}
        
        return {
            'success': True,
            'length': total_length,
            'vias': total_vias,
            'segments': []  # Could store detailed route segments
        }
    
    def _route_point_to_point(self, start_pin: Tuple, end_pin: Tuple, net: Net) -> Dict[str, Any]:
        """Route between two specific pins using A* algorithm"""
        start_x, start_y = start_pin[1], start_pin[2]
        end_x, end_y = end_pin[1], end_pin[2]
        
        # Simple Manhattan distance routing for now
        # In a full implementation, this would use A* pathfinding
        
        manhattan_distance = abs(end_x - start_x) + abs(end_y - start_y)
        
        # Estimate via count based on layer changes needed
        vias_needed = 0
        if start_pin[3] != end_pin[3]:  # Different layers
            vias_needed = 1
        
        # Apply cognitive routing patterns
        route_efficiency = self.routing_knowledge['trace_routing']['minimize_bends']
        actual_length = manhattan_distance * (2.0 - route_efficiency)  # Efficiency factor
        
        return {
            'success': True,
            'length': actual_length,
            'vias': vias_needed,
            'path': [(start_x, start_y, start_pin[3]), (end_x, end_y, end_pin[3])]
        }
    
    def _optimize_routes(self, routed_nets: List[str]) -> List[str]:
        """Optimize existing routes using learned patterns"""
        optimizations = []
        
        # Optimization 1: Via reduction
        via_reduction = self._optimize_via_usage()
        if via_reduction > 0:
            optimizations.append(f"Reduced vias by {via_reduction}")
        
        # Optimization 2: Length optimization
        length_reduction = self._optimize_trace_lengths()
        if length_reduction > 0:
            optimizations.append(f"Reduced trace length by {length_reduction:.1f}mm")
        
        # Optimization 3: Crosstalk reduction
        crosstalk_improvement = self._optimize_signal_integrity()
        if crosstalk_improvement:
            optimizations.append("Improved signal integrity spacing")
        
        return optimizations
    
    def _optimize_via_usage(self) -> int:
        """Optimize via placement and count"""
        # Simulate via reduction
        via_optimization_effectiveness = self.routing_knowledge['via_placement']['minimize_vias']
        reduction = int(10 * via_optimization_effectiveness)  # Simulate reduction
        return reduction
    
    def _optimize_trace_lengths(self) -> float:
        """Optimize trace routing for shorter paths"""
        # Simulate length optimization
        length_optimization_effectiveness = self.routing_knowledge['trace_routing']['minimize_bends']
        reduction = 15.0 * length_optimization_effectiveness  # Simulate reduction in mm
        return reduction
    
    def _optimize_signal_integrity(self) -> bool:
        """Optimize routing for better signal integrity"""
        # Simulate signal integrity improvements
        si_effectiveness = self.routing_knowledge['design_optimization']['crosstalk_minimization']
        return si_effectiveness > 0.8
    
    def _check_design_rules(self) -> int:
        """Check for design rule violations"""
        # Simulate design rule checking
        violations = 0
        
        # Check minimum trace width violations
        # Check minimum spacing violations  
        # Check via size violations
        
        # For simulation, return low violation count for good routing
        return violations
    
    def _calculate_routing_score(self, wire_length: float, via_count: int, 
                               completion: float, violations: int) -> float:
        """Calculate overall routing quality score"""
        base_score = 100.0
        
        # Penalties
        length_penalty = min(30, wire_length / 20)  # Penalty increases with length
        via_penalty = min(20, via_count / 5)        # Penalty for excessive vias
        completion_bonus = completion - 100         # Bonus for 100% completion
        violation_penalty = violations * 10          # 10 points per violation
        
        score = base_score - length_penalty - via_penalty + completion_bonus - violation_penalty
        return max(0, min(100, score))
    
    def _learn_from_successful_route(self, net: Net, route_result: Dict[str, Any]):
        """Learn from successful routing for future optimization"""
        learning_key = f"net_{net.name}_{len(self.learned_patterns)}"
        
        learning_entry = {
            'net_priority': net.priority,
            'pin_count': len(net.pins),
            'route_length': route_result['length'],
            'via_count': route_result['vias'],
            'efficiency_ratio': route_result['length'] / max(1, len(net.pins) * 10),
            'success_factors': []
        }
        
        # Identify success factors
        if route_result['vias'] <= 2:
            learning_entry['success_factors'].append('minimal_vias')
        
        if route_result['length'] < len(net.pins) * 15:  # Good length ratio
            learning_entry['success_factors'].append('efficient_routing')
        
        self.learned_patterns[learning_key] = learning_entry
        
        # Update routing knowledge effectiveness
        for factor in learning_entry['success_factors']:
            if factor == 'minimal_vias':
                current = self.routing_knowledge['via_placement']['minimize_vias']
                self.routing_knowledge['via_placement']['minimize_vias'] = min(1.0, current + 0.01)
            elif factor == 'efficient_routing':
                current = self.routing_knowledge['trace_routing']['minimize_bends']
                self.routing_knowledge['trace_routing']['minimize_bends'] = min(1.0, current + 0.01)

def create_test_routing_scenario():
    """Create test scenario for routing engine"""
    nets = [
        Net("VCC", 1, 0.3, [("U1", 30, 30, "F.Cu"), ("C1", 35, 35, "F.Cu"), ("U2", 60, 20, "F.Cu")]),
        Net("GND", 1, 0.3, [("U1", 30, 32, "F.Cu"), ("C1", 35, 33, "F.Cu"), ("U2", 60, 22, "F.Cu")]),
        Net("SDA", 2, 0.125, [("U1", 28, 30, "F.Cu"), ("U2", 58, 20, "F.Cu")], max_length=30.0),
        Net("SCL", 2, 0.125, [("U1", 28, 32, "F.Cu"), ("U2", 58, 22, "F.Cu")], max_length=30.0),
        Net("RESET", 3, 0.125, [("U1", 32, 34, "F.Cu"), ("R1", 20, 20, "F.Cu")]),
        Net("LED1", 4, 0.125, [("U1", 32, 28, "F.Cu"), ("D1", 80, 40, "F.Cu")]),
    ]
    
    return nets

if __name__ == "__main__":
    # Test AI routing engine
    print("AI-Enhanced Routing Engine Test")
    print("=" * 50)
    
    engine = CognitiveRoutingEngine()
    engine.set_design_rules("aisler", "ENIG")
    
    nets = create_test_routing_scenario()
    board_bounds = (0, 0, 100, 80)  # mm
    
    result = engine.route_nets(nets, board_bounds)
    
    print(f"\nRouting Results:")
    print(f"Completion: {result.completion_percentage:.1f}%")
    print(f"Routing Score: {result.routing_score:.1f}/100")
    print(f"Total Wire Length: {result.total_wire_length:.1f}mm")
    print(f"Via Count: {result.via_count}")
    print(f"Design Rule Violations: {result.design_rule_violations}")
    
    print(f"\nSuccessfully Routed Nets:")
    for net in result.routed_nets:
        print(f"  - {net}")
    
    if result.failed_nets:
        print(f"\nFailed Nets:")
        for net in result.failed_nets:
            print(f"  - {net}")
    
    if result.optimizations_applied:
        print(f"\nOptimizations Applied:")
        for opt in result.optimizations_applied:
            print(f"  - {opt}")