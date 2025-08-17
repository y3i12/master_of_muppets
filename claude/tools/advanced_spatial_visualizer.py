#!/usr/bin/env python3
"""
Advanced Spatial Visualizer v1.0 - Physics + CircuitJS1 inspired precision
Combines 2D physics simulation with electrical circuit layout principles
"""

import json
import math
import sys
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

# Import our spatial intelligence brain
sys.path.append(str(Path(__file__).parent.parent / "brain_systems"))
from spatial_intelligence import SpatialNode, SpatialConnection, SpatialPhysicsEngine, GraphLayoutAlgorithms

@dataclass
class ElectricalNode:
    """Represents an electrical component with circuit-specific properties"""
    id: str
    component_type: str  # "resistor", "capacitor", "ic", "connector", etc.
    value: str = ""
    x: float = 0.0
    y: float = 0.0
    width: float = 20.0
    height: float = 10.0
    rotation: float = 0.0  # degrees
    posts: List[Tuple[float, float]] = None  # Connection points
    grid_aligned: bool = True
    voltage_level: Optional[float] = None
    current_flow: Optional[float] = None
    
    def __post_init__(self):
        if self.posts is None:
            self.posts = self._generate_default_posts()
    
    def _generate_default_posts(self) -> List[Tuple[float, float]]:
        """Generate default connection posts based on component type"""
        if self.component_type in ["resistor", "capacitor", "inductor"]:
            # Two-terminal components
            return [(0, self.height/2), (self.width, self.height/2)]
        elif self.component_type == "ic":
            # Multi-pin IC - simplified to 4 corners
            return [(0, 0), (self.width, 0), (0, self.height), (self.width, self.height)]
        elif self.component_type == "connector":
            # Single post connector
            return [(self.width/2, self.height/2)]
        else:
            # Default: center post
            return [(self.width/2, self.height/2)]
    
    def get_absolute_posts(self) -> List[Tuple[float, float]]:
        """Get post positions in absolute coordinates"""
        absolute_posts = []
        for rel_x, rel_y in self.posts:
            # Apply rotation and translation
            cos_r = math.cos(math.radians(self.rotation))
            sin_r = math.sin(math.radians(self.rotation))
            
            rotated_x = rel_x * cos_r - rel_y * sin_r
            rotated_y = rel_x * sin_r + rel_y * cos_r
            
            abs_x = self.x + rotated_x
            abs_y = self.y + rotated_y
            absolute_posts.append((abs_x, abs_y))
        
        return absolute_posts

@dataclass
class ElectricalConnection:
    """Connection between electrical nodes with routing information"""
    from_node: str
    to_node: str
    from_post: int = 0  # Which post on from_node
    to_post: int = 0    # Which post on to_node
    net_name: str = ""
    signal_type: str = "digital"  # "digital", "analog", "power", "ground"
    route_points: List[Tuple[float, float]] = None  # Manual routing points
    auto_route: bool = True
    
    def __post_init__(self):
        if self.route_points is None:
            self.route_points = []

class GridSystem:
    """Grid-based positioning system inspired by CircuitJS1"""
    
    def __init__(self, grid_size: float = 10.0):
        self.grid_size = grid_size
        
    def snap_to_grid(self, x: float, y: float) -> Tuple[float, float]:
        """Snap coordinates to grid"""
        snapped_x = round(x / self.grid_size) * self.grid_size
        snapped_y = round(y / self.grid_size) * self.grid_size
        return (snapped_x, snapped_y)
        
    def snap_node_to_grid(self, node: ElectricalNode) -> None:
        """Snap electrical node to grid"""
        if node.grid_aligned:
            node.x, node.y = self.snap_to_grid(node.x, node.y)

class ConnectionRouter:
    """Intelligent connection routing system"""
    
    def __init__(self, grid_system: GridSystem):
        self.grid = grid_system
        self.routing_margin = 5.0
        
    def route_connection(self, connection: ElectricalConnection, 
                        nodes: Dict[str, ElectricalNode]) -> List[Tuple[float, float]]:
        """Route a connection between two nodes"""
        
        if not connection.auto_route:
            return connection.route_points
        
        from_node = nodes[connection.from_node]
        to_node = nodes[connection.to_node]
        
        from_posts = from_node.get_absolute_posts()
        to_posts = to_node.get_absolute_posts()
        
        if connection.from_post >= len(from_posts) or connection.to_post >= len(to_posts):
            return []
        
        start_point = from_posts[connection.from_post]
        end_point = to_posts[connection.to_post]
        
        # Choose routing strategy based on signal type
        if connection.signal_type == "power":
            return self._route_power_connection(start_point, end_point)
        elif connection.signal_type == "analog":
            return self._route_analog_connection(start_point, end_point)
        else:
            return self._route_digital_connection(start_point, end_point)
    
    def _route_digital_connection(self, start: Tuple[float, float], 
                                 end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Route digital connection with Manhattan routing"""
        sx, sy = start
        ex, ey = end
        
        # Simple Manhattan routing
        if abs(ex - sx) > abs(ey - sy):
            # Route horizontally first
            midpoint = (ex, sy)
        else:
            # Route vertically first  
            midpoint = (sx, ey)
        
        return [start, midpoint, end]
    
    def _route_analog_connection(self, start: Tuple[float, float], 
                                end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Route analog connection with minimal crossings"""
        # For analog signals, prefer direct routing when possible
        sx, sy = start
        ex, ey = end
        
        distance = math.sqrt((ex-sx)**2 + (ey-sy)**2)
        
        if distance < 50:  # Direct routing for short connections
            return [start, end]
        else:
            # Use gentle curve for longer analog connections
            mid_x = (sx + ex) / 2
            mid_y = (sy + ey) / 2
            offset = min(20, distance / 4)
            
            # Add slight offset for curved appearance
            if abs(ex - sx) > abs(ey - sy):
                curve_point = (mid_x, mid_y + offset)
            else:
                curve_point = (mid_x + offset, mid_y)
            
            return [start, curve_point, end]
    
    def _route_power_connection(self, start: Tuple[float, float], 
                               end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """Route power connection with star topology preference"""
        # Power connections prefer star routing to minimize voltage drop
        return [start, end]  # Direct routing for power

class AdvancedSpatialVisualizer:
    """Advanced visualization combining physics simulation with electrical precision"""
    
    def __init__(self, canvas_width: float = 1200, canvas_height: float = 800):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.grid_system = GridSystem(grid_size=10.0)
        self.router = ConnectionRouter(self.grid_system)
        self.nodes: Dict[str, ElectricalNode] = {}
        self.connections: List[ElectricalConnection] = []
        self.physics_engine = SpatialPhysicsEngine(canvas_width, canvas_height)
        
    def add_electrical_node(self, node: ElectricalNode) -> None:
        """Add an electrical node to the visualization"""
        self.nodes[node.id] = node
        self.grid_system.snap_node_to_grid(node)
        
        # Convert to spatial node for physics simulation
        spatial_node = SpatialNode(
            id=node.id,
            x=node.x,
            y=node.y, 
            width=node.width,
            height=node.height,
            mass=1.0,
            group=node.component_type
        )
        self.physics_engine.add_node(spatial_node)
        
    def add_electrical_connection(self, connection: ElectricalConnection) -> None:
        """Add an electrical connection"""
        self.connections.append(connection)
        
        # Convert to spatial connection for physics
        spatial_conn = SpatialConnection(
            from_id=connection.from_node,
            to_id=connection.to_node,
            strength=1.0,
            ideal_length=100.0,
            connection_type=connection.signal_type
        )
        self.physics_engine.add_connection(spatial_conn)
    
    def optimize_layout(self, use_physics: bool = True, iterations: int = 100) -> None:
        """Optimize the spatial layout"""
        if use_physics:
            print("[VISUALIZER] Running physics-based layout optimization...")
            steps = self.physics_engine.simulate(steps=iterations, convergence_threshold=0.5)
            
            # Update electrical nodes with physics results
            for node_id, spatial_node in self.physics_engine.nodes.items():
                if node_id in self.nodes:
                    electrical_node = self.nodes[node_id]
                    electrical_node.x = spatial_node.x
                    electrical_node.y = spatial_node.y
                    self.grid_system.snap_node_to_grid(electrical_node)
            
            print(f"[VISUALIZER] Physics optimization completed in {steps} steps")
        else:
            print("[VISUALIZER] Using grid-only layout optimization...")
            for node in self.nodes.values():
                self.grid_system.snap_node_to_grid(node)
    
    def generate_advanced_svg(self, title: str = "Advanced Circuit Layout") -> str:
        """Generate advanced SVG with physics-optimized layout"""
        
        # SVG header with styles
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{self.canvas_width}" height="{self.canvas_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .grid {{ stroke: #f0f0f0; stroke-width: 0.5; fill: none; }}
      .resistor {{ fill: #8B4513; stroke: #654321; stroke-width: 1; }}
      .capacitor {{ fill: #4169E1; stroke: #1E90FF; stroke-width: 1; }}
      .ic {{ fill: #2F4F4F; stroke: #000000; stroke-width: 2; }}
      .connector {{ fill: #FFD700; stroke: #FFA500; stroke-width: 2; }}
      .connection-digital {{ stroke: #000000; stroke-width: 2; fill: none; }}
      .connection-analog {{ stroke: #FF6347; stroke-width: 2; fill: none; }}
      .connection-power {{ stroke: #DC143C; stroke-width: 3; fill: none; }}
      .connection-ground {{ stroke: #006400; stroke-width: 2; fill: none; }}
      .post {{ fill: #C0C0C0; stroke: #808080; stroke-width: 1; }}
      .node-label {{ font: 10px Arial; fill: #000000; text-anchor: middle; }}
      .value-label {{ font: 8px Arial; fill: #666666; text-anchor: middle; }}
      .title {{ font: bold 18px Arial; fill: #2c3e50; text-anchor: middle; }}
    </style>
  </defs>
  
  <title>{title}</title>
  
  <!-- Grid -->
'''
        
        # Add grid
        grid_size = self.grid_system.grid_size
        for x in range(0, int(self.canvas_width), int(grid_size)):
            svg_content += f'  <line x1="{x}" y1="0" x2="{x}" y2="{self.canvas_height}" class="grid" />\n'
        for y in range(0, int(self.canvas_height), int(grid_size)):
            svg_content += f'  <line x1="0" y1="{y}" x2="{self.canvas_width}" y2="{y}" class="grid" />\n'
        
        svg_content += '\n  <!-- Connections -->\n'
        
        # Render connections with intelligent routing
        for connection in self.connections:
            route_points = self.router.route_connection(connection, self.nodes)
            
            if len(route_points) >= 2:
                path_data = f"M {route_points[0][0]:.1f} {route_points[0][1]:.1f}"
                
                for point in route_points[1:]:
                    path_data += f" L {point[0]:.1f} {point[1]:.1f}"
                
                svg_content += f'  <path d="{path_data}" class="connection-{connection.signal_type}" '
                svg_content += f'data-net="{connection.net_name}" />\n'
        
        svg_content += '\n  <!-- Components -->\n'
        
        # Render electrical components
        for node in self.nodes.values():
            # Component body
            svg_content += f'  <g id="{node.id}" class="component-{node.component_type}">\n'
            
            # Rotate if needed
            if node.rotation != 0:
                center_x = node.x + node.width / 2
                center_y = node.y + node.height / 2
                svg_content += f'    <g transform="rotate({node.rotation} {center_x} {center_y})">\n'
            
            # Component rectangle
            svg_content += f'      <rect x="{node.x:.1f}" y="{node.y:.1f}" '
            svg_content += f'width="{node.width:.1f}" height="{node.height:.1f}" '
            svg_content += f'class="{node.component_type}" rx="2" />\n'
            
            # Component label
            label_x = node.x + node.width / 2
            label_y = node.y + node.height / 2 - 5
            svg_content += f'      <text x="{label_x:.1f}" y="{label_y:.1f}" '
            svg_content += f'class="node-label">{node.id}</text>\n'
            
            # Component value
            if node.value:
                value_y = node.y + node.height / 2 + 8
                svg_content += f'      <text x="{label_x:.1f}" y="{value_y:.1f}" '
                svg_content += f'class="value-label">{node.value}</text>\n'
            
            # Connection posts
            for i, (post_x, post_y) in enumerate(node.get_absolute_posts()):
                svg_content += f'      <circle cx="{post_x:.1f}" cy="{post_y:.1f}" '
                svg_content += f'r="2" class="post" data-post="{i}" />\n'
            
            if node.rotation != 0:
                svg_content += '    </g>\n'
            
            svg_content += '  </g>\n'
        
        # Title
        svg_content += f'\n  <text x="{self.canvas_width/2}" y="20" class="title">{title}</text>\n'
        
        svg_content += '</svg>'
        
        return svg_content
    
    def create_master_of_muppets_topology(self) -> str:
        """Create the Master of Muppets topology visualization with advanced spatial layout"""
        
        print("[VISUALIZER] Creating Master of Muppets topology with advanced spatial layout...")
        
        # Add main components
        teensy = ElectricalNode("T1", "ic", "Teensy4.1", 50, 100, 80, 40)
        self.add_electrical_node(teensy)
        
        dac1 = ElectricalNode("DAC1", "ic", "AD5593R", 200, 80, 60, 30)
        self.add_electrical_node(dac1)
        
        dac2 = ElectricalNode("DAC2", "ic", "AD5593R", 200, 140, 60, 30)
        self.add_electrical_node(dac2)
        
        # OpAmps
        opamp_positions = [(400, 60), (400, 100), (400, 140), (400, 180)]
        for i, (x, y) in enumerate(opamp_positions, 1):
            opamp = ElectricalNode(f"OpAmp{i}", "ic", "TL074", x, y, 50, 25)
            self.add_electrical_node(opamp)
        
        # Jacks
        jack_y_positions = range(50, 200, 20)
        for i, y in enumerate(jack_y_positions[:8], 2):
            jack = ElectricalNode(f"J{i}", "connector", "3.5mm", 600, y, 30, 15)
            self.add_electrical_node(jack)
        
        # Add some key connections
        connections = [
            ElectricalConnection("T1", "DAC1", signal_type="digital", net_name="I2C_SDA"),
            ElectricalConnection("T1", "DAC2", signal_type="digital", net_name="I2C_SCL"),
            ElectricalConnection("DAC1", "OpAmp1", signal_type="analog", net_name="CV_OUT1"),
            ElectricalConnection("DAC1", "OpAmp2", signal_type="analog", net_name="CV_OUT2"),
            ElectricalConnection("DAC2", "OpAmp3", signal_type="analog", net_name="CV_OUT3"),
            ElectricalConnection("DAC2", "OpAmp4", signal_type="analog", net_name="CV_OUT4"),
            ElectricalConnection("OpAmp1", "J2", signal_type="analog", net_name="OUTPUT1"),
            ElectricalConnection("OpAmp2", "J3", signal_type="analog", net_name="OUTPUT2"),
            ElectricalConnection("OpAmp3", "J4", signal_type="analog", net_name="OUTPUT3"),
            ElectricalConnection("OpAmp4", "J5", signal_type="analog", net_name="OUTPUT4"),
        ]
        
        for connection in connections:
            self.add_electrical_connection(connection)
        
        # Optimize layout with physics
        self.optimize_layout(use_physics=True, iterations=150)
        
        # Generate SVG
        return self.generate_advanced_svg("Master of Muppets: Physics-Optimized Circuit Topology")

# CLI interface
if __name__ == "__main__":
    visualizer = AdvancedSpatialVisualizer()
    
    # Create Master of Muppets visualization
    svg_content = visualizer.create_master_of_muppets_topology()
    
    # Save to file
    output_file = "master_of_muppets_advanced_topology.svg"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"[VISUALIZER] Advanced topology visualization saved to: {output_file}")
    
    # Also create a test spatial layout
    test_visualizer = AdvancedSpatialVisualizer()
    
    # Add some test components (use ASCII instead of Unicode)
    for i in range(5):
        node = ElectricalNode(f"R{i+1}", "resistor", f"{(i+1)*100}ohm", 
                            i*80 + 50, 200, 40, 15)
        test_visualizer.add_electrical_node(node)
    
    # Connect them in series
    for i in range(4):
        conn = ElectricalConnection(f"R{i+1}", f"R{i+2}", signal_type="analog")
        test_visualizer.add_electrical_connection(conn)
    
    test_visualizer.optimize_layout(use_physics=True)
    test_svg = test_visualizer.generate_advanced_svg("Physics Test Layout")
    
    with open("physics_test_layout.svg", 'w', encoding='utf-8') as f:
        f.write(test_svg)
    
    print("[VISUALIZER] Test layout saved to: physics_test_layout.svg")