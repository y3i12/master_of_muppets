#!/usr/bin/env python3
"""
Integrated Spatial Brain v1.0 - Complete spatial intelligence system
Combines physics simulation, graph theory, electrical awareness, and cross-system intelligence
"""

import json
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Import all spatial components
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent / "tools"))

from spatial_intelligence import SpatialIntelligenceBrain, SpatialNode, SpatialConnection
from advanced_spatial_visualizer import AdvancedSpatialVisualizer, ElectricalNode, ElectricalConnection
from cross_system_synthesizer import CrossSystemSynthesizer

class IntegratedSpatialBrain:
    """Master spatial intelligence system integrating all capabilities"""
    
    def __init__(self):
        self.spatial_intelligence = SpatialIntelligenceBrain()
        self.visualizer = AdvancedSpatialVisualizer()
        self.synthesizer = CrossSystemSynthesizer()
        self.knowledge_cache = {}
        self.layout_patterns = {}
        self.performance_metrics = {
            'layouts_generated': 0,
            'physics_simulations': 0,
            'cross_system_queries': 0,
            'efficiency_improvements': []
        }
        
    def learn_pcb_layout_patterns(self, pcb_file_path: str) -> Dict[str, Any]:
        """Learn spatial patterns from existing PCB layout"""
        
        print("[INTEGRATED] Learning PCB layout patterns...")
        
        # Import PCB parser
        from kicad_pcb_parser import KiCadPCBParser
        
        parser = KiCadPCBParser(pcb_file_path)
        
        # Analyze spatial patterns
        patterns = {
            'component_clustering': self._analyze_component_clustering(parser.components),
            'spacing_patterns': self._analyze_spacing_patterns(parser.components),
            'orientation_patterns': self._analyze_orientation_patterns(parser.components),
            'zone_utilization': self._analyze_zone_utilization(parser.components)
        }
        
        # Store learned patterns
        self.layout_patterns['pcb_analysis'] = patterns
        
        print(f"[INTEGRATED] Learned {len(patterns)} spatial patterns from PCB")
        return patterns
    
    def _analyze_component_clustering(self, components: Dict) -> Dict[str, List]:
        """Analyze how components cluster together"""
        clusters = {
            'power_cluster': [],
            'analog_cluster': [], 
            'digital_cluster': [],
            'connector_cluster': []
        }
        
        for ref, comp in components.items():
            if ref.startswith('J'):
                clusters['connector_cluster'].append(ref)
            elif ref.startswith('T') or 'MCU' in ref:
                clusters['digital_cluster'].append(ref)
            elif 'DAC' in ref or 'OpAmp' in ref:
                clusters['analog_cluster'].append(ref)
            elif 'V_REG' in ref or 'PWR' in ref:
                clusters['power_cluster'].append(ref)
        
        return clusters
    
    def _analyze_spacing_patterns(self, components: Dict) -> Dict[str, float]:
        """Analyze typical spacing between components"""
        spacings = {
            'ic_to_ic': [],
            'ic_to_passive': [],
            'jack_spacing': [],
            'general_spacing': []
        }
        
        component_list = list(components.items())
        
        for i, (ref1, comp1) in enumerate(component_list):
            for j, (ref2, comp2) in enumerate(component_list[i+1:], i+1):
                distance = comp1.distance_to(comp2)
                
                # Categorize spacing
                if self._is_ic(ref1) and self._is_ic(ref2):
                    spacings['ic_to_ic'].append(distance)
                elif self._is_ic(ref1) != self._is_ic(ref2):
                    spacings['ic_to_passive'].append(distance)
                elif ref1.startswith('J') and ref2.startswith('J'):
                    spacings['jack_spacing'].append(distance)
                else:
                    spacings['general_spacing'].append(distance)
        
        # Calculate averages
        avg_spacings = {}
        for category, distances in spacings.items():
            if distances:
                avg_spacings[f'{category}_avg'] = sum(distances) / len(distances)
                avg_spacings[f'{category}_min'] = min(distances)
                avg_spacings[f'{category}_max'] = max(distances)
        
        return avg_spacings
    
    def _analyze_orientation_patterns(self, components: Dict) -> Dict[str, int]:
        """Analyze component orientation preferences"""
        orientations = {'0': 0, '90': 0, '180': 0, '270': 0}
        
        for ref, comp in components.items():
            rotation = str(int(comp.rotation))
            if rotation in orientations:
                orientations[rotation] += 1
        
        return orientations
    
    def _analyze_zone_utilization(self, components: Dict) -> Dict[str, Any]:
        """Analyze how board space is utilized"""
        if not components:
            return {}
        
        # Find bounds
        x_coords = [comp.x for comp in components.values()]
        y_coords = [comp.y for comp in components.values()]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Calculate utilization
        board_width = max_x - min_x
        board_height = max_y - min_y
        
        return {
            'board_bounds': (min_x, min_y, max_x, max_y),
            'board_dimensions': (board_width, board_height),
            'component_density': len(components) / (board_width * board_height) if board_width * board_height > 0 else 0,
            'utilization_efficiency': self._calculate_utilization_efficiency(components)
        }
    
    def _is_ic(self, ref: str) -> bool:
        """Check if component is an IC"""
        return ref.startswith(('U', 'T', 'DAC', 'OpAmp'))
    
    def _calculate_utilization_efficiency(self, components: Dict) -> float:
        """Calculate how efficiently the board space is used"""
        if len(components) < 2:
            return 0.0
        
        # Simple efficiency metric based on component clustering
        total_distance = 0
        count = 0
        
        component_list = list(components.values())
        for i, comp1 in enumerate(component_list):
            for comp2 in component_list[i+1:]:
                total_distance += comp1.distance_to(comp2)
                count += 1
        
        avg_distance = total_distance / count if count > 0 else 0
        
        # Lower average distance = higher efficiency (components are closer together)
        return 1.0 / (1.0 + avg_distance / 100.0)
    
    def create_intelligent_pcb_layout(self, pcb_file_path: str, 
                                    optimization_goals: List[str] = None) -> str:
        """Create an intelligent PCB layout visualization using all spatial intelligence"""
        
        if optimization_goals is None:
            optimization_goals = ['minimize_trace_length', 'respect_signal_integrity', 'thermal_distribution']
        
        print("[INTEGRATED] Creating intelligent PCB layout...")
        
        # Step 1: Learn from existing PCB
        patterns = self.learn_pcb_layout_patterns(pcb_file_path)
        
        # Step 2: Get cross-system intelligence
        synthesis = self.synthesizer.synthesize_placement_intelligence(pcb_file_path)
        
        # Step 3: Create electrical representation
        electrical_nodes = self._convert_pcb_to_electrical_nodes(pcb_file_path)
        node_ids = [node.id for node in electrical_nodes]
        electrical_connections = self._infer_electrical_connections(synthesis, node_ids)
        
        # Step 4: Add nodes to visualizer
        visualizer = AdvancedSpatialVisualizer(canvas_width=1400, canvas_height=1000)
        
        for node in electrical_nodes:
            visualizer.add_electrical_node(node)
        
        for connection in electrical_connections:
            visualizer.add_electrical_connection(connection)
        
        # Step 5: Apply optimization goals
        self._apply_optimization_goals(visualizer, optimization_goals, patterns)
        
        # Step 6: Run physics optimization
        visualizer.optimize_layout(use_physics=True, iterations=200)
        
        # Step 7: Generate intelligent SVG
        svg_content = visualizer.generate_advanced_svg("Master of Muppets: Intelligent PCB Layout")
        
        # Step 8: Update performance metrics
        self.performance_metrics['layouts_generated'] += 1
        self.performance_metrics['physics_simulations'] += 1
        self.performance_metrics['cross_system_queries'] += 1
        
        print("[INTEGRATED] Intelligent PCB layout created successfully!")
        
        return svg_content
    
    def _convert_pcb_to_electrical_nodes(self, pcb_file_path: str) -> List[ElectricalNode]:
        """Convert PCB components to electrical nodes"""
        from kicad_pcb_parser import KiCadPCBParser
        
        parser = KiCadPCBParser(pcb_file_path)
        electrical_nodes = []
        
        for ref, comp in parser.components.items():
            # Determine component type and properties
            if ref.startswith('R'):
                comp_type = "resistor"
                width, height = 30, 10
            elif ref.startswith('C'):
                comp_type = "capacitor" 
                width, height = 20, 10
            elif ref.startswith('U') or ref.startswith('OpAmp'):
                comp_type = "ic"
                width, height = 40, 20
            elif ref.startswith('J'):
                comp_type = "connector"
                width, height = 25, 15
            elif ref.startswith('T'):
                comp_type = "ic"
                width, height = 60, 30
            elif ref.startswith('DAC'):
                comp_type = "ic"
                width, height = 35, 18
            else:
                comp_type = "other"
                width, height = 20, 10
            
            node = ElectricalNode(
                id=ref,
                component_type=comp_type,
                value="",  # Could extract from footprint data
                x=comp.x,
                y=comp.y,
                width=width,
                height=height,
                rotation=comp.rotation
            )
            
            electrical_nodes.append(node)
        
        return electrical_nodes
    
    def _infer_electrical_connections(self, synthesis: Dict, available_nodes: List[str]) -> List[ElectricalConnection]:
        """Infer electrical connections from cross-system analysis"""
        connections = []
        available_set = set(available_nodes)
        
        # Extract signal flow analysis
        signal_flow = synthesis.get('signal_flow_analysis', {})
        critical_paths = signal_flow.get('critical_paths', [])
        
        for path in critical_paths:
            components = path.get('components', [])
            signal_type = "analog" if "CV" in path.get('name', '') else "digital"
            
            # Filter components to only those that exist
            valid_components = [comp for comp in components if comp in available_set]
            
            # Create chain connections
            for i in range(len(valid_components) - 1):
                connection = ElectricalConnection(
                    from_node=valid_components[i],
                    to_node=valid_components[i + 1],
                    signal_type=signal_type,
                    net_name=path.get('name', f'NET_{i}')
                )
                connections.append(connection)
        
        # Add some basic connections based on component names
        if 'T1' in available_set and 'DAC2' in available_set:
            connections.append(ElectricalConnection('T1', 'DAC2', signal_type='digital', net_name='I2C_BUS'))
        
        return connections
    
    def _apply_optimization_goals(self, visualizer: AdvancedSpatialVisualizer, 
                                goals: List[str], patterns: Dict) -> None:
        """Apply optimization goals to the layout"""
        
        for goal in goals:
            if goal == 'minimize_trace_length':
                # Adjust spring forces for shorter connections
                visualizer.physics_engine.attraction_force *= 1.5
                
            elif goal == 'respect_signal_integrity':
                # Increase spacing for analog signals
                for connection in visualizer.connections:
                    if connection.signal_type == 'analog':
                        # Find spatial connection and adjust
                        for spatial_conn in visualizer.physics_engine.connections:
                            if (spatial_conn.from_id == connection.from_node and 
                                spatial_conn.to_id == connection.to_node):
                                spatial_conn.ideal_length *= 0.8  # Shorter for better integrity
                                
            elif goal == 'thermal_distribution':
                # Spread high-power components
                high_power_components = ['T1', 'V_REG1', 'DAC1', 'DAC2']
                for comp_id in high_power_components:
                    if comp_id in visualizer.physics_engine.nodes:
                        node = visualizer.physics_engine.nodes[comp_id]
                        node.mass *= 2.0  # Higher mass = more separation force
    
    def generate_spatial_intelligence_report(self, pcb_file_path: str) -> str:
        """Generate comprehensive spatial intelligence report"""
        
        # Gather intelligence from all systems
        patterns = self.learn_pcb_layout_patterns(pcb_file_path)
        synthesis = self.synthesizer.synthesize_placement_intelligence(pcb_file_path)
        
        report = f"""# Spatial Intelligence Report - Master of Muppets
Generated: {datetime.now().isoformat()}

## Performance Metrics
- Layouts Generated: {self.performance_metrics['layouts_generated']}
- Physics Simulations: {self.performance_metrics['physics_simulations']}
- Cross-System Queries: {self.performance_metrics['cross_system_queries']}

## Learned Spatial Patterns
"""
        
        # Component clustering analysis
        clustering = patterns.get('component_clustering', {})
        for cluster_type, components in clustering.items():
            if components:
                report += f"- **{cluster_type}**: {len(components)} components ({', '.join(components[:5])}{'...' if len(components) > 5 else ''})\n"
        
        # Spacing analysis
        report += "\n## Spacing Analysis\n"
        spacing = patterns.get('spacing_patterns', {})
        for metric, value in spacing.items():
            if isinstance(value, float):
                report += f"- {metric}: {value:.2f}mm\n"
        
        # Zone utilization
        report += "\n## Board Utilization\n"
        utilization = patterns.get('zone_utilization', {})
        if 'component_density' in utilization:
            report += f"- Component Density: {utilization['component_density']:.4f} components/mm²\n"
        if 'utilization_efficiency' in utilization:
            report += f"- Utilization Efficiency: {utilization['utilization_efficiency']:.3f}\n"
        
        # Cross-system insights
        report += "\n## Cross-System Intelligence\n"
        insights = synthesis.get('cognitive_insights', [])
        for insight in insights[:5]:
            report += f"- {insight}\n"
        
        # Integrated suggestions
        report += "\n## Spatial Optimization Suggestions\n"
        suggestions = synthesis.get('integrated_suggestions', [])
        for i, suggestion in enumerate(suggestions[:10], 1):
            report += f"{i}. **{suggestion.get('type', 'General')}** (Priority {suggestion.get('priority', 1)})\n"
            report += f"   - {suggestion.get('description', 'No description')}\n"
            report += f"   - Action: {suggestion.get('action', 'No action specified')}\n\n"
        
        return report
    
    def save_spatial_intelligence(self, output_dir: str = "claude/brain_systems") -> None:
        """Save spatial intelligence state to brain systems"""
        
        brain_data = {
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat(),
            'layout_patterns': self.layout_patterns,
            'performance_metrics': self.performance_metrics,
            'knowledge_cache': self.knowledge_cache
        }
        
        output_path = Path(output_dir) / "spatial_intelligence_state.json"
        with open(output_path, 'w') as f:
            json.dump(brain_data, f, indent=2)
        
        print(f"[INTEGRATED] Spatial intelligence saved to: {output_path}")

# CLI interface
if __name__ == "__main__":
    brain = IntegratedSpatialBrain()
    
    if len(sys.argv) > 1:
        pcb_file = sys.argv[1]
        
        # Generate intelligent layout
        svg_content = brain.create_intelligent_pcb_layout(pcb_file)
        
        # Save layout
        with open("intelligent_pcb_layout.svg", 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        # Generate report
        report = brain.generate_spatial_intelligence_report(pcb_file)
        
        with open("spatial_intelligence_report.md", 'w') as f:
            f.write(report)
        
        # Save brain state
        brain.save_spatial_intelligence()
        
        print("[INTEGRATED] Spatial intelligence analysis complete!")
        print("Generated files:")
        print("  - intelligent_pcb_layout.svg")
        print("  - spatial_intelligence_report.md")
        print("  - claude/brain_systems/spatial_intelligence_state.json")
        
    else:
        print("Usage: python integrated_spatial_brain.py <pcb_file>")
        print("Example: python integrated_spatial_brain.py CADfiles/MasterOfMuppets/MasterOfMuppets.kicad_pcb")