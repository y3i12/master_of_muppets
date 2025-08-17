#!/usr/bin/env python3
"""
KiCad PCB Parser v1.0 - Advanced PCB file analysis and manipulation
Specialized for Master of Muppets PCB layout optimization
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import math

@dataclass
class ComponentPlacement:
    """Component placement data structure"""
    reference: str
    footprint: str
    x: float
    y: float
    rotation: float
    layer: str
    locked: bool = False
    
    def distance_to(self, other: 'ComponentPlacement') -> float:
        """Calculate Euclidean distance to another component"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

@dataclass 
class BoardInfo:
    """PCB board information"""
    thickness: float
    layer_count: int
    layers: Dict[int, str]
    board_outline: List[Tuple[float, float]]
    size: Tuple[float, float]  # width, height

@dataclass
class NetConnection:
    """Net connectivity information"""
    net_name: str
    pins: List[str]  # ["U1-1", "R1-1", etc.]
    
class KiCadPCBParser:
    """Parse and analyze KiCad .kicad_pcb files"""
    
    def __init__(self, pcb_file_path: str):
        self.pcb_file = Path(pcb_file_path)
        self.components: Dict[str, ComponentPlacement] = {}
        self.board_info: Optional[BoardInfo] = None
        self.nets: Dict[str, NetConnection] = {}
        self.raw_content = ""
        
        if self.pcb_file.exists():
            self.load_pcb_file()
    
    def load_pcb_file(self):
        """Load and parse the PCB file"""
        print(f"[PCB] Loading {self.pcb_file.name}...")
        
        with open(self.pcb_file, 'r', encoding='utf-8') as f:
            self.raw_content = f.read()
        
        self._parse_board_info()
        self._parse_components()
        self._parse_nets()
        
        print(f"[PCB] Parsed {len(self.components)} components, {len(self.nets)} nets")
    
    def _parse_board_info(self):
        """Parse board-level information"""
        
        # Extract thickness
        thickness_match = re.search(r'\(thickness ([\d.]+)\)', self.raw_content)
        thickness = float(thickness_match.group(1)) if thickness_match else 1.6
        
        # Parse layers
        layers = {}
        layer_pattern = r'\((\d+) "([^"]+)" (\w+)'
        for match in re.finditer(layer_pattern, self.raw_content):
            layer_id, layer_name, layer_type = match.groups()
            layers[int(layer_id)] = layer_name
        
        # Determine layer count (signal layers only)
        signal_layers = [k for k, v in layers.items() if 'Cu' in v]
        layer_count = len(signal_layers)
        
        # Extract board outline (simplified - just get bounding box for now)
        board_outline = []
        size = (100.0, 80.0)  # Default, will be calculated from components
        
        self.board_info = BoardInfo(
            thickness=thickness,
            layer_count=layer_count,
            layers=layers,
            board_outline=board_outline,
            size=size
        )
    
    def _parse_components(self):
        """Parse component placements"""
        
        # Find all footprint sections - improved pattern
        footprint_sections = []
        
        # Split into sections by footprint boundaries
        lines = self.raw_content.split('\n')
        current_section = []
        in_footprint = False
        depth = 0
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('(footprint '):
                in_footprint = True
                current_section = [line]
                depth = 1
            elif in_footprint:
                current_section.append(line)
                # Count parentheses to track nesting
                depth += line.count('(') - line.count(')')
                
                if depth == 0:
                    # End of footprint section
                    footprint_sections.append('\n'.join(current_section))
                    in_footprint = False
                    current_section = []
        
        print(f"[DEBUG] Found {len(footprint_sections)} footprint sections")
        
        for i, section in enumerate(footprint_sections):
            try:
                # Extract footprint name
                footprint_match = re.search(r'\(footprint "([^"]+)"', section)
                if not footprint_match:
                    continue
                footprint = footprint_match.group(1)
                
                # Extract position
                position_match = re.search(r'\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)', section)
                if not position_match:
                    continue
                
                x = float(position_match.group(1))
                y = float(position_match.group(2))
                rotation = float(position_match.group(3)) if position_match.group(3) else 0.0
                
                # Extract layer
                layer_match = re.search(r'\(layer "([^"]+)"\)', section)
                layer = layer_match.group(1) if layer_match else "F.Cu"
                
                # Extract reference
                ref_match = re.search(r'\(property "Reference" "([^"]+)"', section)
                if not ref_match:
                    continue
                reference = ref_match.group(1)
                
                # Check if locked
                locked = '(locked yes)' in section
                
                component = ComponentPlacement(
                    reference=reference,
                    footprint=footprint,
                    x=x,
                    y=y,
                    rotation=rotation,
                    layer=layer,
                    locked=locked
                )
                
                self.components[reference] = component
                
            except Exception as e:
                print(f"[WARNING] Failed to parse component section: {e}")
                continue
    
    def _parse_nets(self):
        """Parse net connectivity information"""
        
        # Extract net definitions
        net_pattern = r'\(net (\d+) "([^"]+)"\)'
        net_matches = re.findall(net_pattern, self.raw_content)
        
        for net_id, net_name in net_matches:
            if net_name and net_name != "":
                self.nets[net_name] = NetConnection(net_name=net_name, pins=[])
        
        # Note: Detailed pin connectivity parsing would require more complex parsing
        # For now, we have the net names which is sufficient for initial analysis
    
    def get_component_by_reference(self, reference: str) -> Optional[ComponentPlacement]:
        """Get component by reference designator"""
        return self.components.get(reference)
    
    def get_components_by_footprint(self, footprint_pattern: str) -> List[ComponentPlacement]:
        """Get components matching footprint pattern"""
        matching = []
        for comp in self.components.values():
            if footprint_pattern.lower() in comp.footprint.lower():
                matching.append(comp)
        return matching
    
    def get_component_groups(self) -> Dict[str, List[ComponentPlacement]]:
        """Group components by type"""
        groups = {
            'microcontroller': [],
            'dac': [],
            'opamp': [],
            'jack': [],
            'resistor': [],
            'capacitor': [],
            'other': []
        }
        
        for comp in self.components.values():
            footprint = comp.footprint.lower()
            ref = comp.reference.lower()
            
            if 'teensy' in footprint or ref.startswith('u') and 'teensy' in comp.footprint:
                groups['microcontroller'].append(comp)
            elif 'tssop' in footprint or ref.startswith('u') and any(x in footprint for x in ['ad5593', 'dac']):
                groups['dac'].append(comp)
            elif 'soic' in footprint or ref.startswith('u') and any(x in footprint for x in ['tl074', 'opamp']):
                groups['opamp'].append(comp)
            elif 'jack' in footprint or ref.startswith('j'):
                groups['jack'].append(comp)
            elif ref.startswith('r') or 'resistor' in footprint:
                groups['resistor'].append(comp)
            elif ref.startswith('c') or 'capacitor' in footprint:
                groups['capacitor'].append(comp)
            else:
                groups['other'].append(comp)
        
        return groups
    
    def analyze_placement_quality(self) -> Dict[str, Any]:
        """Analyze current component placement quality"""
        
        groups = self.get_component_groups()
        analysis = {
            'component_counts': {k: len(v) for k, v in groups.items()},
            'placement_issues': [],
            'optimization_suggestions': []
        }
        
        # Check for obvious placement issues
        if groups['jack']:
            jack_positions = [(j.x, j.y) for j in groups['jack']]
            # Check if jacks are aligned
            x_coords = [pos[0] for pos in jack_positions]
            y_coords = [pos[1] for pos in jack_positions]
            
            if len(set(x_coords)) > 2:  # Jacks should be aligned
                analysis['placement_issues'].append("Jacks not aligned on board edge")
            
            # Check jack spacing
            if len(groups['jack']) > 1:
                for i in range(len(groups['jack']) - 1):
                    dist = groups['jack'][i].distance_to(groups['jack'][i + 1])
                    if dist < 19.0:  # Minimum 19mm spacing
                        analysis['placement_issues'].append(f"Jacks too close: {dist:.1f}mm < 19mm minimum")
        
        # Check if microcontroller is placed
        if not groups['microcontroller']:
            analysis['placement_issues'].append("No microcontroller found")
        elif len(groups['microcontroller']) > 1:
            analysis['placement_issues'].append("Multiple microcontrollers found")
        
        # Check DAC placement relative to microcontroller
        if groups['microcontroller'] and groups['dac']:
            mc = groups['microcontroller'][0]
            for dac in groups['dac']:
                dist = mc.distance_to(dac)
                if dist > 50.0:  # DACs should be within 50mm of microcontroller
                    analysis['placement_issues'].append(f"DAC {dac.reference} too far from microcontroller: {dist:.1f}mm")
        
        return analysis
    
    def get_bounding_box(self) -> Tuple[float, float, float, float]:
        """Get bounding box of all components (min_x, min_y, max_x, max_y)"""
        if not self.components:
            return (0, 0, 0, 0)
        
        x_coords = [comp.x for comp in self.components.values()]
        y_coords = [comp.y for comp in self.components.values()]
        
        return (min(x_coords), min(y_coords), max(x_coords), max(y_coords))
    
    def suggest_placement_improvements(self) -> List[str]:
        """Generate placement improvement suggestions"""
        suggestions = []
        groups = self.get_component_groups()
        
        # Jack placement suggestions
        if groups['jack']:
            suggestions.append("Place all jacks in a vertical line at board edge")
            suggestions.append("Ensure 19.05mm spacing between jack centers")
            suggestions.append("Consider jack numbering order for easy identification")
        
        # Power distribution suggestions
        if groups['microcontroller'] and groups['dac']:
            suggestions.append("Place DACs close to microcontroller for short I2C traces")
            suggestions.append("Group decoupling capacitors near their respective ICs")
        
        # OpAmp placement
        if groups['opamp'] and groups['dac']:
            suggestions.append("Place OpAmps close to their corresponding DAC outputs")
            suggestions.append("Minimize analog signal trace lengths")
        
        # Power section
        suggestions.append("Create dedicated power distribution area")
        suggestions.append("Separate analog and digital sections")
        
        return suggestions
    
    def export_placement_data(self, output_file: str):
        """Export placement data for external tools"""
        
        export_data = {
            'board_info': asdict(self.board_info) if self.board_info else {},
            'components': {ref: asdict(comp) for ref, comp in self.components.items()},
            'component_groups': {k: [asdict(comp) for comp in v] for k, v in self.get_component_groups().items()},
            'analysis': self.analyze_placement_quality(),
            'suggestions': self.suggest_placement_improvements(),
            'bounding_box': self.get_bounding_box()
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"[PCB] Placement data exported to {output_file}")
    
    def generate_placement_report(self) -> str:
        """Generate human-readable placement report"""
        
        groups = self.get_component_groups()
        analysis = self.analyze_placement_quality()
        suggestions = self.suggest_placement_improvements()
        bbox = self.get_bounding_box()
        
        report = f"""# Master of Muppets PCB Placement Report

## Board Information
- Layers: {self.board_info.layer_count if self.board_info else 'Unknown'}
- Thickness: {self.board_info.thickness if self.board_info else 'Unknown'}mm
- Component spread: {bbox[2]-bbox[0]:.1f} × {bbox[3]-bbox[1]:.1f}mm

## Component Summary
"""
        
        for group_name, components in groups.items():
            if components:
                report += f"- **{group_name.title()}**: {len(components)} components\n"
        
        report += f"\n## Placement Issues\n"
        if analysis['placement_issues']:
            for issue in analysis['placement_issues']:
                report += f"- WARNING: {issue}\n"
        else:
            report += "- OK: No major placement issues detected\n"
        
        report += f"\n## Optimization Suggestions\n"
        for suggestion in suggestions:
            report += f"- SUGGESTION: {suggestion}\n"
        
        report += f"\n## Component Details\n"
        for group_name, components in groups.items():
            if components:
                report += f"\n### {group_name.title()}\n"
                for comp in components:
                    report += f"- {comp.reference}: {comp.footprint} @ ({comp.x:.1f}, {comp.y:.1f})\n"
        
        return report

# CLI interface for quick testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python kicad_pcb_parser.py <pcb_file>")
        sys.exit(1)
    
    pcb_file = sys.argv[1]
    parser = KiCadPCBParser(pcb_file)
    
    # Generate reports
    report = parser.generate_placement_report()
    print(report)
    
    # Export data
    parser.export_placement_data(f"{Path(pcb_file).stem}_placement_analysis.json")