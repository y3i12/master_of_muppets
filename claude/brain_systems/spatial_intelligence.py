#!/usr/bin/env python3
"""
Spatial Intelligence Brain System v1.0 - Physics-aware layout and visualization
Integrates 2D physics simulation, graph theory, and spatial reasoning for precise layouts
"""

import json
import math
import random
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class SpatialNode:
    """Represents an object in 2D space with physics properties"""
    id: str
    x: float
    y: float
    width: float
    height: float
    mass: float = 1.0
    velocity_x: float = 0.0
    velocity_y: float = 0.0
    fixed: bool = False
    group: str = "default"
    
    def area(self) -> float:
        return self.width * self.height
    
    def center(self) -> Tuple[float, float]:
        return (self.x + self.width/2, self.y + self.height/2)
    
    def bounds(self) -> Tuple[float, float, float, float]:
        """Returns (min_x, min_y, max_x, max_y)"""
        return (self.x, self.y, self.x + self.width, self.y + self.height)

@dataclass 
class SpatialConnection:
    """Connection between two spatial nodes"""
    from_id: str
    to_id: str
    strength: float = 1.0
    ideal_length: float = 100.0
    connection_type: str = "default"  # "electrical", "logical", "hierarchical"

class SpatialPhysicsEngine:
    """Lightweight 2D physics engine for layout optimization"""
    
    def __init__(self, canvas_width: float = 1200, canvas_height: float = 800):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.nodes: Dict[str, SpatialNode] = {}
        self.connections: List[SpatialConnection] = []
        self.gravity = 0.1
        self.damping = 0.95
        self.repulsion_force = 1000.0
        self.attraction_force = 0.01
        self.collision_enabled = True
        
    def add_node(self, node: SpatialNode) -> None:
        """Add a node to the physics simulation"""
        self.nodes[node.id] = node
        
    def add_connection(self, connection: SpatialConnection) -> None:
        """Add a connection between nodes"""
        self.connections.append(connection)
        
    def check_collision(self, node1: SpatialNode, node2: SpatialNode) -> bool:
        """Check if two nodes overlap"""
        b1 = node1.bounds()
        b2 = node2.bounds()
        
        return not (b1[2] < b2[0] or  # node1 right < node2 left
                   b1[0] > b2[2] or   # node1 left > node2 right
                   b1[3] < b2[1] or   # node1 bottom < node2 top
                   b1[1] > b2[3])     # node1 top > node2 bottom
    
    def calculate_repulsion_force(self, node1: SpatialNode, node2: SpatialNode) -> Tuple[float, float]:
        """Calculate repulsion force between two nodes"""
        c1 = node1.center()
        c2 = node2.center()
        
        dx = c1[0] - c2[0]
        dy = c1[1] - c2[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 0.1:  # Avoid division by zero
            distance = 0.1
            dx = random.uniform(-1, 1)
            dy = random.uniform(-1, 1)
        
        # Force inversely proportional to distance squared
        force_magnitude = self.repulsion_force / (distance * distance)
        
        # Normalize direction
        fx = (dx / distance) * force_magnitude
        fy = (dy / distance) * force_magnitude
        
        return (fx, fy)
    
    def calculate_spring_force(self, connection: SpatialConnection) -> Tuple[float, float, float, float]:
        """Calculate spring force for a connection (returns fx1, fy1, fx2, fy2)"""
        node1 = self.nodes[connection.from_id]
        node2 = self.nodes[connection.to_id]
        
        c1 = node1.center()
        c2 = node2.center()
        
        dx = c2[0] - c1[0]
        dy = c2[1] - c1[1]
        current_length = math.sqrt(dx*dx + dy*dy)
        
        if current_length < 0.1:
            return (0, 0, 0, 0)
        
        # Spring force proportional to displacement from ideal length
        displacement = current_length - connection.ideal_length
        force_magnitude = self.attraction_force * displacement * connection.strength
        
        # Normalize direction
        fx = (dx / current_length) * force_magnitude
        fy = (dy / current_length) * force_magnitude
        
        return (fx, fy, -fx, -fy)
    
    def resolve_collisions(self) -> None:
        """Resolve overlapping nodes by pushing them apart"""
        if not self.collision_enabled:
            return
            
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                node1, node2 = node_list[i], node_list[j]
                
                if self.check_collision(node1, node2):
                    # Calculate separation vector
                    c1 = node1.center()
                    c2 = node2.center()
                    
                    dx = c2[0] - c1[0]
                    dy = c2[1] - c1[1]
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    if distance < 0.1:
                        dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
                        distance = 1.0
                    
                    # Minimum separation distance
                    min_distance = (node1.width + node2.width) / 2 + (node1.height + node2.height) / 2
                    overlap = min_distance - distance
                    
                    if overlap > 0:
                        # Push nodes apart proportionally to their masses
                        total_mass = node1.mass + node2.mass
                        ratio1 = node2.mass / total_mass
                        ratio2 = node1.mass / total_mass
                        
                        separation = overlap * 0.6  # Gentle separation
                        
                        if not node1.fixed:
                            node1.x -= (dx / distance) * separation * ratio1
                            node1.y -= (dy / distance) * separation * ratio1
                        
                        if not node2.fixed:
                            node2.x += (dx / distance) * separation * ratio2
                            node2.y += (dy / distance) * separation * ratio2
    
    def apply_forces(self) -> None:
        """Apply all physics forces to nodes"""
        # Reset forces
        forces = {node_id: [0.0, 0.0] for node_id in self.nodes.keys()}
        
        # Repulsion forces between all nodes
        node_list = list(self.nodes.values())
        for i in range(len(node_list)):
            for j in range(i + 1, len(node_list)):
                node1, node2 = node_list[i], node_list[j]
                
                fx, fy = self.calculate_repulsion_force(node1, node2)
                
                forces[node1.id][0] += fx
                forces[node1.id][1] += fy
                forces[node2.id][0] -= fx
                forces[node2.id][1] -= fy
        
        # Spring forces from connections
        for connection in self.connections:
            fx1, fy1, fx2, fy2 = self.calculate_spring_force(connection)
            
            forces[connection.from_id][0] += fx1
            forces[connection.from_id][1] += fy1
            forces[connection.to_id][0] += fx2
            forces[connection.to_id][1] += fy2
        
        # Apply forces to velocities
        for node_id, node in self.nodes.items():
            if not node.fixed:
                node.velocity_x += forces[node_id][0] / node.mass
                node.velocity_y += forces[node_id][1] / node.mass
                
                # Apply damping
                node.velocity_x *= self.damping
                node.velocity_y *= self.damping
    
    def update_positions(self) -> None:
        """Update node positions based on velocities"""
        for node in self.nodes.values():
            if not node.fixed:
                node.x += node.velocity_x
                node.y += node.velocity_y
                
                # Keep nodes within canvas bounds
                node.x = max(0, min(self.canvas_width - node.width, node.x))
                node.y = max(0, min(self.canvas_height - node.height, node.y))
    
    def simulate_step(self) -> None:
        """Run one simulation step"""
        self.apply_forces()
        self.update_positions()
        self.resolve_collisions()
    
    def simulate(self, steps: int = 100, convergence_threshold: float = 0.1) -> int:
        """Run physics simulation until convergence or max steps"""
        for step in range(steps):
            prev_positions = {node_id: (node.x, node.y) for node_id, node in self.nodes.items()}
            
            self.simulate_step()
            
            # Check convergence
            max_movement = 0.0
            for node_id, node in self.nodes.items():
                prev_x, prev_y = prev_positions[node_id]
                movement = math.sqrt((node.x - prev_x)**2 + (node.y - prev_y)**2)
                max_movement = max(max_movement, movement)
            
            if max_movement < convergence_threshold:
                print(f"[SPATIAL] Converged after {step + 1} steps (max movement: {max_movement:.3f})")
                return step + 1
        
        print(f"[SPATIAL] Simulation completed {steps} steps without full convergence")
        return steps

class GraphLayoutAlgorithms:
    """Graph theory algorithms for spatial layout"""
    
    @staticmethod
    def force_directed_layout(nodes: List[SpatialNode], connections: List[SpatialConnection], 
                            canvas_width: float = 1200, canvas_height: float = 800) -> Dict[str, SpatialNode]:
        """Force-directed graph layout algorithm"""
        engine = SpatialPhysicsEngine(canvas_width, canvas_height)
        
        # Add all nodes
        for node in nodes:
            engine.add_node(node)
        
        # Add all connections
        for connection in connections:
            engine.add_connection(connection)
        
        # Run simulation
        steps_taken = engine.simulate(steps=200, convergence_threshold=0.5)
        
        return engine.nodes
    
    @staticmethod
    def hierarchical_layout(nodes: List[SpatialNode], connections: List[SpatialConnection],
                          canvas_width: float = 1200, canvas_height: float = 800) -> Dict[str, SpatialNode]:
        """Hierarchical layout for tree-like structures"""
        # Group nodes by hierarchy level
        levels = {}
        root_nodes = []
        
        # Find nodes with no incoming connections
        incoming_counts = {node.id: 0 for node in nodes}
        for conn in connections:
            incoming_counts[conn.to_id] += 1
        
        # Roots have no incoming connections
        for node in nodes:
            if incoming_counts[node.id] == 0:
                root_nodes.append(node)
        
        if not root_nodes:
            # Fallback to force-directed if no clear hierarchy
            return GraphLayoutAlgorithms.force_directed_layout(nodes, connections, canvas_width, canvas_height)
        
        # Assign levels using BFS
        current_level = 0
        current_nodes = root_nodes[:]
        levels[current_level] = current_nodes
        processed = set(node.id for node in root_nodes)
        
        while current_nodes:
            next_nodes = []
            for node in current_nodes:
                # Find children
                for conn in connections:
                    if conn.from_id == node.id and conn.to_id not in processed:
                        child_node = next(n for n in nodes if n.id == conn.to_id)
                        next_nodes.append(child_node)
                        processed.add(child_node.id)
            
            if next_nodes:
                current_level += 1
                levels[current_level] = next_nodes
                current_nodes = next_nodes
            else:
                break
        
        # Position nodes by level
        level_height = canvas_height / (len(levels) + 1)
        
        positioned_nodes = {}
        for level, level_nodes in levels.items():
            y_pos = level_height * (level + 1)
            node_spacing = canvas_width / (len(level_nodes) + 1)
            
            for i, node in enumerate(level_nodes):
                x_pos = node_spacing * (i + 1) - node.width / 2
                node.x = max(0, min(canvas_width - node.width, x_pos))
                node.y = y_pos - node.height / 2
                positioned_nodes[node.id] = node
        
        return positioned_nodes
    
    @staticmethod
    def circular_layout(nodes: List[SpatialNode], canvas_width: float = 1200, canvas_height: float = 800) -> Dict[str, SpatialNode]:
        """Arrange nodes in a circle"""
        center_x = canvas_width / 2
        center_y = canvas_height / 2
        radius = min(canvas_width, canvas_height) * 0.3
        
        positioned_nodes = {}
        angle_step = 2 * math.pi / len(nodes)
        
        for i, node in enumerate(nodes):
            angle = i * angle_step
            node.x = center_x + radius * math.cos(angle) - node.width / 2
            node.y = center_y + radius * math.sin(angle) - node.height / 2
            
            # Keep within bounds
            node.x = max(0, min(canvas_width - node.width, node.x))
            node.y = max(0, min(canvas_height - node.height, node.y))
            
            positioned_nodes[node.id] = node
        
        return positioned_nodes

class SpatialSVGGenerator:
    """Physics-aware SVG generation with precise spatial layouts"""
    
    def __init__(self, width: float = 1200, height: float = 800):
        self.width = width
        self.height = height
        self.nodes: Dict[str, SpatialNode] = {}
        self.connections: List[SpatialConnection] = []
        self.style_definitions = {}
        
    def add_node(self, node: SpatialNode) -> None:
        """Add a spatial node for rendering"""
        self.nodes[node.id] = node
        
    def add_connection(self, connection: SpatialConnection) -> None:
        """Add a connection for rendering"""
        self.connections.append(connection)
        
    def define_style(self, class_name: str, styles: Dict[str, str]) -> None:
        """Define CSS styles for SVG elements"""
        self.style_definitions[class_name] = styles
        
    def optimize_layout(self, algorithm: str = "force_directed") -> None:
        """Optimize spatial layout using specified algorithm"""
        nodes_list = list(self.nodes.values())
        
        if algorithm == "force_directed":
            self.nodes = GraphLayoutAlgorithms.force_directed_layout(
                nodes_list, self.connections, self.width, self.height)
        elif algorithm == "hierarchical":
            self.nodes = GraphLayoutAlgorithms.hierarchical_layout(
                nodes_list, self.connections, self.width, self.height)
        elif algorithm == "circular":
            self.nodes = GraphLayoutAlgorithms.circular_layout(
                nodes_list, self.width, self.height)
        
        print(f"[SPATIAL] Layout optimized using {algorithm} algorithm")
    
    def generate_svg(self, title: str = "Spatial Layout") -> str:
        """Generate physics-optimized SVG"""
        
        # Build CSS styles
        css_styles = []
        for class_name, styles in self.style_definitions.items():
            style_str = f".{class_name} {{ "
            style_str += "; ".join(f"{prop}: {value}" for prop, value in styles.items())
            style_str += "; }"
            css_styles.append(style_str)
        
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.width}" height="{self.height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      {chr(10).join(css_styles)}
    </style>
  </defs>
  
  <title>{title}</title>
  
  <!-- Connections -->
'''
        
        # Render connections first (so they appear behind nodes)
        for connection in self.connections:
            if connection.from_id in self.nodes and connection.to_id in self.nodes:
                from_node = self.nodes[connection.from_id]
                to_node = self.nodes[connection.to_id]
                
                from_center = from_node.center()
                to_center = to_node.center()
                
                svg_content += f'  <line x1="{from_center[0]:.1f}" y1="{from_center[1]:.1f}" '
                svg_content += f'x2="{to_center[0]:.1f}" y2="{to_center[1]:.1f}" '
                svg_content += f'class="connection-{connection.connection_type}" '
                svg_content += f'stroke-width="{connection.strength * 2}" />\n'
        
        svg_content += '\n  <!-- Nodes -->\n'
        
        # Render nodes
        for node in self.nodes.values():
            svg_content += f'  <g id="{node.id}" class="node-{node.group}">\n'
            svg_content += f'    <rect x="{node.x:.1f}" y="{node.y:.1f}" '
            svg_content += f'width="{node.width:.1f}" height="{node.height:.1f}" '
            svg_content += f'class="node-rect-{node.group}" rx="5" />\n'
            
            # Add text label
            center = node.center()
            svg_content += f'    <text x="{center[0]:.1f}" y="{center[1]:.1f}" '
            svg_content += f'class="node-text-{node.group}" text-anchor="middle" '
            svg_content += f'dominant-baseline="middle">{node.id}</text>\n'
            svg_content += '  </g>\n'
        
        svg_content += '</svg>'
        
        return svg_content

class SpatialIntelligenceBrain:
    """Main spatial intelligence coordination system"""
    
    def __init__(self):
        self.physics_engine = SpatialPhysicsEngine()
        self.svg_generator = SpatialSVGGenerator()
        self.layout_cache = {}
        self.spatial_patterns = {}
        
    def learn_spatial_pattern(self, pattern_name: str, nodes: List[SpatialNode], 
                            connections: List[SpatialConnection]) -> None:
        """Learn and cache a spatial layout pattern"""
        self.spatial_patterns[pattern_name] = {
            'nodes': [asdict(node) for node in nodes],
            'connections': [asdict(conn) for conn in connections]
        }
        print(f"[SPATIAL] Learned pattern: {pattern_name}")
    
    def apply_spatial_pattern(self, pattern_name: str) -> Tuple[List[SpatialNode], List[SpatialConnection]]:
        """Apply a learned spatial pattern"""
        if pattern_name not in self.spatial_patterns:
            return [], []
        
        pattern = self.spatial_patterns[pattern_name]
        nodes = [SpatialNode(**node_data) for node_data in pattern['nodes']]
        connections = [SpatialConnection(**conn_data) for conn_data in pattern['connections']]
        
        return nodes, connections
    
    def create_schematic_topology_layout(self, component_data: Dict) -> str:
        """Create a physics-optimized schematic topology visualization"""
        
        # Define styles
        self.svg_generator.define_style("schematic-node", {
            "fill": "#3498db",
            "stroke": "#2980b9", 
            "stroke-width": "2"
        })
        
        self.svg_generator.define_style("pcb-node", {
            "fill": "#e67e22",
            "stroke": "#d35400",
            "stroke-width": "2"
        })
        
        self.svg_generator.define_style("connection-hierarchy", {
            "stroke": "#34495e",
            "stroke-width": "2",
            "fill": "none"
        })
        
        self.svg_generator.define_style("connection-mismatch", {
            "stroke": "#e74c3c",
            "stroke-width": "3",
            "stroke-dasharray": "5,5",
            "fill": "none"
        })
        
        # Create nodes with proper physics properties
        nodes = []
        
        # Main schematic node
        main_sch = SpatialNode("MasterOfMuppets", 300, 100, 200, 60, mass=5.0, fixed=True, group="schematic")
        nodes.append(main_sch)
        
        # Hierarchical sheet nodes
        hierarchical_sheets = [
            ("amp_module", 25, 2, 120, 80),
            ("dac_module", 4, 1, 120, 80), 
            ("jack_sheet", 8, 1, 120, 80),
            ("teensy_module", 1, 1, 120, 80),
            ("unripple_module", 2, 6, 120, 80)
        ]
        
        connections = []
        
        for i, (name, components, instances, width, height) in enumerate(hierarchical_sheets):
            node = SpatialNode(name, 100 + i*150, 250, width, height, 
                             mass=components*instances/10, group="schematic")
            nodes.append(node)
            
            # Connect to main schematic
            connections.append(SpatialConnection("MasterOfMuppets", name, 
                                               strength=instances, ideal_length=150,
                                               connection_type="hierarchy"))
        
        # PCB node
        pcb_node = SpatialNode("PCB_Reality", 700, 100, 250, 100, mass=10.0, fixed=True, group="pcb")
        nodes.append(pcb_node)
        
        # Connect PCB to main schematic (mismatch)
        connections.append(SpatialConnection("MasterOfMuppets", "PCB_Reality",
                                           strength=0.5, ideal_length=300,
                                           connection_type="mismatch"))
        
        # Add nodes and connections to generator
        for node in nodes:
            self.svg_generator.add_node(node)
        
        for connection in connections:
            self.svg_generator.add_connection(connection)
        
        # Optimize layout
        self.svg_generator.optimize_layout("force_directed")
        
        # Generate final SVG
        return self.svg_generator.generate_svg("Master of Muppets: Physics-Optimized Topology")

# CLI interface and testing
if __name__ == "__main__":
    brain = SpatialIntelligenceBrain()
    
    # Test with sample data
    sample_data = {
        "schematic_components": 75,
        "pcb_components": 147,
        "hierarchical_sheets": 6
    }
    
    svg_output = brain.create_schematic_topology_layout(sample_data)
    
    # Save to file
    output_path = Path("spatial_topology_test.svg")
    with open(output_path, 'w') as f:
        f.write(svg_output)
    
    print(f"[SPATIAL] Physics-optimized SVG generated: {output_path}")