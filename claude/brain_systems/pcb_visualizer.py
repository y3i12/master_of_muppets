#!/usr/bin/env python3
"""
PCB Visualizer v1.0 - Iterative component placement visualization
Fast, cheap visual feedback for PCB layout iterations
"""

import json
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass

@dataclass
class Component:
    """Component with position and dimensions"""
    ref: str
    x: float
    y: float
    width: float
    height: float
    package: str
    rotation: int = 0

class PCBVisualizer:
    """Fast PCB layout visualization for iterative design"""
    
    def __init__(self, pcb_width: float = 100, pcb_height: float = 160):
        self.pcb_width = pcb_width  # mm
        self.pcb_height = pcb_height  # mm
        self.components = []
        self.grid_size = 2.54  # 0.1" grid
        
    def add_component(self, ref: str, x: float, y: float, width: float, height: float, package: str = ""):
        """Add component to visualization"""
        self.components.append(Component(ref, x, y, width, height, package))
    
    def ascii_visualization(self, scale: float = 0.5) -> str:
        """Generate ASCII art PCB layout"""
        
        # Scale to character grid
        char_width = int(self.pcb_width * scale)
        char_height = int(self.pcb_height * scale)
        
        # Create empty board
        board = [[' ' for _ in range(char_width)] for _ in range(char_height)]
        
        # Add PCB outline
        for x in range(char_width):
            board[0][x] = '-'
            board[char_height-1][x] = '-'
        for y in range(char_height):
            board[y][0] = '|'
            board[y][char_width-1] = '|'
        
        # Corners
        board[0][0] = '+'
        board[0][char_width-1] = '+'
        board[char_height-1][0] = '+'
        board[char_height-1][char_width-1] = '+'
        
        # Place components
        for comp in self.components:
            comp_x = int(comp.x * scale)
            comp_y = int(comp.y * scale)
            comp_w = max(1, int(comp.width * scale))
            comp_h = max(1, int(comp.height * scale))
            
            # Component symbol based on type
            symbol = self._get_component_symbol(comp.ref)
            
            # Fill component area
            for dy in range(comp_h):
                for dx in range(comp_w):
                    x_pos = min(comp_x + dx, char_width - 1)
                    y_pos = min(comp_y + dy, char_height - 1)
                    if 0 < x_pos < char_width - 1 and 0 < y_pos < char_height - 1:
                        board[y_pos][x_pos] = symbol
        
        # Convert to string
        result = f"PCB Layout ({self.pcb_width}x{self.pcb_height}mm):\n"
        for row in board:
            result += ''.join(row) + '\n'
        
        return result
    
    def _get_component_symbol(self, ref: str) -> str:
        """Get ASCII symbol for component type"""
        if ref.startswith('U') or ref.startswith('T'):
            return '#'  # MCU/DAC
        elif ref.startswith('IC'):
            return 'A'  # OpAmp
        elif ref.startswith('J'):
            return 'O'  # Jack
        elif ref.startswith('C'):
            return 'C'  # Capacitor
        elif ref.startswith('R'):
            return 'R'  # Resistor
        else:
            return '?'
    
    def coordinate_layout(self) -> str:
        """Generate coordinate-based layout description"""
        
        result = f"PCB Coordinate Layout ({self.pcb_width}x{self.pcb_height}mm):\n\n"
        
        # Sort components by position
        sorted_comps = sorted(self.components, key=lambda c: (c.y, c.x))
        
        for comp in sorted_comps:
            result += f"{comp.ref:8} ({comp.package:10}) @ ({comp.x:5.1f}, {comp.y:5.1f}) [{comp.width:4.1f}x{comp.height:4.1f}mm]\n"
        
        return result
    
    def generate_html_visual(self) -> str:
        """Generate HTML/SVG visualization"""
        
        svg_width = 800
        svg_height = int(svg_width * self.pcb_height / self.pcb_width)
        scale_x = svg_width / self.pcb_width
        scale_y = svg_height / self.pcb_height
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>PCB Layout Visualization</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .component {{ cursor: pointer; }}
        .component:hover {{ stroke-width: 2; }}
        .label {{ font-size: 10px; text-anchor: middle; }}
    </style>
</head>
<body>
    <h2>PCB Layout - {self.pcb_width}x{self.pcb_height}mm</h2>
    <svg width="{svg_width}" height="{svg_height}" style="border: 2px solid #333;">
        <!-- PCB outline -->
        <rect x="0" y="0" width="{svg_width}" height="{svg_height}" 
              fill="#2d5016" stroke="#000" stroke-width="2"/>
'''
        
        # Add components
        for comp in self.components:
            x = comp.x * scale_x
            y = comp.y * scale_y
            w = comp.width * scale_x
            h = comp.height * scale_y
            
            color = self._get_component_color(comp.ref)
            
            html += f'''        <g class="component">
            <rect x="{x}" y="{y}" width="{w}" height="{h}" 
                  fill="{color}" stroke="#000" stroke-width="1" opacity="0.8"/>
            <text x="{x + w/2}" y="{y + h/2}" class="label" fill="white">{comp.ref}</text>
        </g>
'''
        
        html += '''    </svg>
    <div style="margin-top: 20px;">
        <h3>Component Legend:</h3>
        <div style="display: flex; gap: 20px;">
            <div>■ MCU/DAC (blue)</div>
            <div>■ OpAmp (red)</div>
            <div>■ Jack (orange)</div>
            <div>■ Capacitor (green)</div>
            <div>■ Resistor (yellow)</div>
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def _get_component_color(self, ref: str) -> str:
        """Get color for component type"""
        if ref.startswith('U') or ref.startswith('T'):
            return '#4a90e2'  # Blue for MCU/DAC
        elif ref.startswith('IC'):
            return '#e24a4a'  # Red for OpAmp
        elif ref.startswith('J'):
            return '#e2a04a'  # Orange for Jack
        elif ref.startswith('C'):
            return '#4ae24a'  # Green for Capacitor
        elif ref.startswith('R'):
            return '#e2e24a'  # Yellow for Resistor
        else:
            return '#666'     # Gray for others

def propose_initial_layout() -> PCBVisualizer:
    """Propose initial component layout based on optimization rules"""
    
    pcb = PCBVisualizer(100, 160)  # 100x160mm Eurocard
    
    # Load footprint data
    footprint_data = {
        'Teensy': (61, 17.78),
        'AD5593R': (4.4, 5.0),
        'TL074': (3.9, 8.7),
        'Jack': (15.8, 15.8),
        'R_0603': (1.6, 0.8),
        'C_0603': (1.6, 0.8)
    }
    
    # Zone-based placement (from optimization rules)
    
    # 1. Teensy in center-left (main controller)
    pcb.add_component('T1', 20, 70, 61, 17.78, 'Teensy4.1')
    
    # 2. DACs near Teensy (I2C critical group)
    pcb.add_component('DAC1', 25, 45, 4.4, 5.0, 'AD5593R')
    pcb.add_component('DAC2', 25, 100, 4.4, 5.0, 'AD5593R')
    
    # 3. OpAmps in analog zone (right side)
    pcb.add_component('U1', 60, 30, 3.9, 8.7, 'TL074')
    pcb.add_component('U2', 70, 30, 3.9, 8.7, 'TL074')
    pcb.add_component('U3', 60, 110, 3.9, 8.7, 'TL074')
    pcb.add_component('U4', 70, 110, 3.9, 8.7, 'TL074')
    
    # 4. Jacks on right edge (user accessible)
    for i in range(16):
        y_pos = 10 + i * 9  # 9mm spacing
        pcb.add_component(f'J{i+2}', 85, y_pos, 15.8, 8, 'Jack_3.5mm')
    
    # 5. Decoupling caps near ICs (within 3mm)
    pcb.add_component('C1', 22, 42, 1.6, 0.8, 'C_0603')  # Near DAC1
    pcb.add_component('C2', 22, 97, 1.6, 0.8, 'C_0603')  # Near DAC2
    pcb.add_component('C3', 57, 27, 1.6, 0.8, 'C_0603')  # Near U1
    pcb.add_component('C4', 57, 107, 1.6, 0.8, 'C_0603') # Near U3
    
    return pcb

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("[VISUAL] PCB Visualizer - Iterative placement tool")
        print("Commands:")
        print("  propose     - Generate initial layout proposal")
        print("  ascii       - Show ASCII visualization")
        print("  html        - Generate HTML visualization")
        print("  coords      - Show coordinate layout")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "propose":
        layout = propose_initial_layout()
        print(layout.coordinate_layout())
        print("\nASCII Preview:")
        print(layout.ascii_visualization())
        
        # Save HTML
        html_file = Path("pcb_layout_proposal.html")
        with open(html_file, 'w') as f:
            f.write(layout.generate_html_visual())
        print(f"\nHTML visualization saved: {html_file}")
        
    else:
        print(f"[ERROR] Unknown command: {cmd}")