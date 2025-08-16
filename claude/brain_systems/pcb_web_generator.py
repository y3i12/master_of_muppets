#!/usr/bin/env python3
"""
PCB Web Generator v1.0 - Bridge between Python analysis and interactive web tool
Generates interactive HTML from placement data
"""

import json
from pathlib import Path
from typing import Dict, List, Any

class PCBWebGenerator:
    """Generate interactive web PCB layout from Python data"""
    
    def __init__(self, template_path: str = "claude/brain_systems/pcb_interactive.html"):
        self.template_path = Path(template_path)
        self.components = []
        
    def load_from_coordinates(self, coord_data: List[Dict[str, Any]]) -> 'PCBWebGenerator':
        """Load component data from coordinate list"""
        self.components = coord_data
        return self
    
    def load_from_footprint_analyzer(self, analyzer_output: str) -> 'PCBWebGenerator':
        """Load from footprint analyzer output"""
        # Parse footprint analyzer coordinate output
        components = []
        for line in analyzer_output.split('\n'):
            if '@' in line and '[' in line:
                # Parse: "T1    (Teensy4.1) @ (20.0, 70.0) [61.0x17.8mm]"
                parts = line.split('@')
                if len(parts) == 2:
                    ref_part = parts[0].strip().split('(')
                    ref = ref_part[0].strip()
                    package = ref_part[1].rstrip(')').strip() if len(ref_part) > 1 else "Unknown"
                    
                    coord_part = parts[1].split('[')[0].strip()
                    coord_part = coord_part.strip('() ')
                    x, y = map(float, coord_part.split(','))
                    
                    size_part = parts[1].split('[')[1].rstrip('mm]').strip()
                    width, height = map(float, size_part.split('x'))
                    
                    components.append({
                        'ref': ref,
                        'package': package,
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    })
        
        self.components = components
        return self
    
    def generate_interactive_layout(self, output_path: str = "pcb_layout_interactive.html") -> str:
        """Generate interactive HTML file with current component data"""
        
        # Read template
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Generate JavaScript component data
        js_components = []
        for comp in self.components:
            js_components.append(f"""
            pcb.addComponent('{comp['package']}', {comp['x']}, {comp['y']});
            // Set custom ref: {comp['ref']}""")
        
        # Insert component loading into the loadDefaultLayout function
        component_js = '\n            '.join(js_components)
        
        # Replace the default layout
        template = template.replace(
            '// Default Master of Muppets layout',
            f'// Generated from Python data\n            {component_js}'
        )
        
        # Write output
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"[WEB] Interactive PCB layout generated: {output_file}")
        return str(output_file)
    
    def update_with_optimization_rules(self, optimization_file: str) -> 'PCBWebGenerator':
        """Enhance with placement optimization rules"""
        
        rules_path = Path(optimization_file)
        if rules_path.exists():
            with open(rules_path, 'r') as f:
                rules = json.load(f)
            
            # Extract constraints for visualization
            constraints = []
            if 'placement_rules' in rules:
                for constraint in rules['placement_rules'].get('absolute_constraints', []):
                    constraints.append({
                        'type': 'absolute',
                        'component': constraint.get('component', ''),
                        'position': constraint.get('position', ''),
                        'reason': constraint.get('reason', '')
                    })
            
            print(f"[RULES] Loaded {len(constraints)} placement constraints")
        
        return self
    
    def export_to_kicad_placement(self) -> str:
        """Export component positions in KiCad-compatible format"""
        
        kicad_lines = ["# KiCad PCB placement file"]
        kicad_lines.append("# Generated from interactive PCB layout")
        kicad_lines.append("")
        
        for comp in self.components:
            # KiCad placement format: Ref X Y Rotation Side
            kicad_lines.append(f"{comp['ref']} {comp['x']:.3f} {comp['y']:.3f} 0.0 F")
        
        placement_content = '\n'.join(kicad_lines)
        
        placement_file = Path("pcb_placement.pos")
        with open(placement_file, 'w') as f:
            f.write(placement_content)
        
        print(f"[KICAD] Placement file exported: {placement_file}")
        return str(placement_file)

def quick_generate_from_analyzer() -> str:
    """Quick function to generate interactive layout from existing analyzer"""
    
    # Sample coordinate data (from our earlier output)
    sample_data = """T1       (Teensy4.1 ) @ ( 20.0,  70.0) [61.0x17.8mm]
DAC1     (AD5593R   ) @ ( 25.0,  45.0) [ 4.4x 5.0mm]
DAC2     (AD5593R   ) @ ( 25.0, 100.0) [ 4.4x 5.0mm]
U1       (TL074     ) @ ( 60.0,  30.0) [ 3.9x 8.7mm]
U2       (TL074     ) @ ( 70.0,  30.0) [ 3.9x 8.7mm]
U3       (TL074     ) @ ( 60.0, 110.0) [ 3.9x 8.7mm]
U4       (TL074     ) @ ( 70.0, 110.0) [ 3.9x 8.7mm]
J2       (Jack_3.5mm) @ ( 85.0,  10.0) [15.8x 8.0mm]"""
    
    generator = PCBWebGenerator()
    generator.load_from_footprint_analyzer(sample_data)
    
    return generator.generate_interactive_layout()

# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("[WEB] PCB Web Generator - Interactive layout creation")
        print("Commands:")
        print("  quick           - Generate from sample data")
        print("  generate <file> - Generate from coordinate file")
        print("  demo            - Open quick generated layout")
        sys.exit(0)
    
    cmd = sys.argv[1]
    
    if cmd == "quick":
        output_file = quick_generate_from_analyzer()
        print(f"[SUCCESS] Open {output_file} in your browser!")
    
    elif cmd == "generate" and len(sys.argv) > 2:
        coord_file = sys.argv[2]
        generator = PCBWebGenerator()
        
        with open(coord_file, 'r') as f:
            coord_data = f.read()
        
        generator.load_from_footprint_analyzer(coord_data)
        output_file = generator.generate_interactive_layout()
        print(f"[SUCCESS] Generated {output_file}")
    
    elif cmd == "demo":
        import webbrowser
        import os
        
        output_file = quick_generate_from_analyzer()
        full_path = os.path.abspath(output_file)
        webbrowser.open(f'file://{full_path}')
        print(f"[DEMO] Opened {full_path} in browser")
    
    else:
        print(f"[ERROR] Unknown command: {cmd}")