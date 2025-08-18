#!/usr/bin/env python3
"""
Create SVG visualization of PCB components and pins from KiCad PCB JSON data
Usage: python pcb_to_svg.py input.json [output.svg]
"""

import json
import sys
import argparse
from pathlib import Path

def load_pcb_data(json_path):
    """Load the PCB JSON data from specified path"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_component_data(pcb_data):
    """Extract component positions and pin data from raw footprint data"""
    components = []
    
    for footprint in pcb_data.get('footprints', []):
        # Get component reference from properties
        reference = ""
        value = ""
        
        properties = footprint.get('properties', {})
        if isinstance(properties, dict):
            reference = properties.get('Reference', '')
            value = properties.get('Value', '')
        
        # Skip if no reference
        if not reference:
            continue
            
        # Get position
        position = footprint.get('position', {})
        x = position.get('X', 0)
        y = position.get('Y', 0)
        rotation = position.get('angle', 0) or 0
        
        # Get footprint info
        entry_name = footprint.get('entryName', '')
        description = footprint.get('description', '')
        
        # Extract pads (pins)
        pins = []
        for pad in footprint.get('pads', []):
            pad_pos = pad.get('position', {})
            pad_x = pad_pos.get('X', 0)
            pad_y = pad_pos.get('Y', 0)
            
            # Calculate absolute pin position
            abs_x = x + pad_x
            abs_y = y + pad_y
            
            pad_size = pad.get('size', {})
            
            pin_data = {
                'number': pad.get('number', ''),
                'shape': pad.get('shape', 'circle'),
                'x': abs_x,
                'y': abs_y,
                'width': pad_size.get('X', 1.27) if pad_size else 1.27,
                'height': pad_size.get('Y', 1.27) if pad_size else 1.27,
                'drill': pad.get('drill', {}).get('diameter', 0) if pad.get('drill') else 0,
                'net_name': pad.get('net', {}).get('name', '') if pad.get('net') else ''
            }
            pins.append(pin_data)
        
        component = {
            'reference': reference,
            'value': value,
            'x': x,
            'y': y,
            'rotation': rotation,
            'footprint_type': entry_name,
            'description': description,
            'pins': pins
        }
        
        components.append(component)
    
    return components

def create_svg(components, output_path, pcb_name="PCB"):
    """Create SVG visualization of the PCB"""
    
    if not components:
        print("No components found to visualize")
        return False
    
    # Calculate bounds
    all_x = []
    all_y = []
    
    for comp in components:
        all_x.append(comp['x'])
        all_y.append(comp['y'])
        for pin in comp['pins']:
            all_x.append(pin['x'])
            all_y.append(pin['y'])
    
    if not all_x or not all_y:
        print("No coordinate data found")
        return False
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    # Calculate base scale factor from drawing size
    pcb_width = max_x - min_x
    pcb_height = max_y - min_y
    base_scale = min(pcb_width, pcb_height) / 50  # Normalize to reasonable scale
    
    # Simple margins - just enough space around the components
    margin = max(20, base_scale * 5)
    
    svg_width = pcb_width + 2 * margin
    svg_height = pcb_height + 2 * margin
    
    # Transform coordinates to SVG (flip Y and add margin)
    def transform_x(x):
        return x - min_x + margin
    
    def transform_y(y):
        return svg_height - (y - min_y + margin)  # Flip Y axis
    
    # Start SVG
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width:.1f}" height="{svg_height:.1f}" viewBox="0 0 {svg_width:.1f} {svg_height:.1f}" 
     xmlns="http://www.w3.org/2000/svg">
  
  <!-- PCB Background -->
  <rect width="100%" height="100%" fill="#2d5016" stroke="#1a3009" stroke-width="{base_scale * 0.5:.1f}"/>
  
  <!-- Grid pattern -->
  <defs>
    <pattern id="grid" width="{base_scale * 2:.1f}" height="{base_scale * 2:.1f}" patternUnits="userSpaceOnUse">
      <path d="M {base_scale * 2:.1f} 0 L 0 0 0 {base_scale * 2:.1f}" fill="none" stroke="#4a6b2a" stroke-width="{base_scale * 0.1:.1f}" opacity="0.3"/>
    </pattern>
  </defs>
  <rect width="100%" height="100%" fill="url(#grid)"/>
  
'''
    
    # Component type colors
    component_colors = {
        'resistor': '#8b4513',
        'capacitor': '#4169e1', 
        'connector': '#ffa500',
        'transistor': '#dc143c',
        'switch': '#9932cc'
    }
    
    def get_component_color(footprint_type, description):
        ft_lower = (footprint_type or '').lower()
        desc_lower = (description or '').lower()
        
        if 'resistor' in desc_lower or '0204' in ft_lower:
            return component_colors['resistor']
        elif 'capacitor' in desc_lower or 'cap' in desc_lower or 'c0' in ft_lower or 'e' in ft_lower[:2]:
            return component_colors['capacitor']
        elif 'connector' in desc_lower or 'weidmuller' in ft_lower or 'pm' in ft_lower:
            return component_colors['connector']  
        elif 'transistor' in desc_lower or 'to92' in ft_lower or 'to126' in ft_lower:
            return component_colors['transistor']
        elif 'switch' in desc_lower or '2p2t' in ft_lower:
            return component_colors['switch']
        else:
            return '#666666'
    
    # Draw components and pins
    for i, comp in enumerate(components):
        comp_x = transform_x(comp['x'])
        comp_y = transform_y(comp['y'])
        
        color = get_component_color(comp['footprint_type'], comp['description'])
        
        # Draw component body
        if comp['pins']:
            # Calculate component size based on pin spread
            pin_xs = [transform_x(p['x']) for p in comp['pins']]
            pin_ys = [transform_y(p['y']) for p in comp['pins']]
            
            body_width = max(pin_xs) - min(pin_xs) + 4
            body_height = max(pin_ys) - min(pin_ys) + 4
            
            if body_width < 8:
                body_width = 8
            if body_height < 8:
                body_height = 8
        else:
            body_width = 10
            body_height = 6
        
        # Component body rectangle
        stroke_width = max(0.2, base_scale * 0.2)
        svg_content += f'''  <rect x="{comp_x - body_width/2:.1f}" y="{comp_y - body_height/2:.1f}" 
           width="{body_width:.1f}" height="{body_height:.1f}" 
           fill="{color}" stroke="white" stroke-width="{stroke_width:.1f}" opacity="0.8"/>
  
'''
        
        # Scale font sizes based on component size and overall drawing scale
        ref_font_size = min(body_width / 3, svg_width / 25, 8)
        value_font_size = min(body_width / 4, svg_width / 30, 6)
        
        # Component reference text
        text_spacing = max(0.5, base_scale * 0.2)
        svg_content += f'''  <text x="{comp_x:.1f}" y="{comp_y - body_height/2 - text_spacing:.1f}" text-anchor="middle" 
           fill="white" font-family="Arial, sans-serif" font-size="{ref_font_size:.1f}" font-weight="bold">
    {comp['reference']}
  </text>
  
'''
        
        # Component value text  
        if comp['value']:
            svg_content += f'''  <text x="{comp_x:.1f}" y="{comp_y + body_height/2 + value_font_size + text_spacing:.1f}" text-anchor="middle" 
               fill="white" font-family="Arial, sans-serif" font-size="{value_font_size:.1f}">
      {comp['value']}
    </text>
    
'''
        
        # Draw pins
        for pin in comp['pins']:
            pin_x = transform_x(pin['x'])
            pin_y = transform_y(pin['y'])
            
            # Pin color based on net
            if pin['net_name']:
                pin_color = '#ffd700'  # Gold for connected pins
            else:
                pin_color = '#c0c0c0'  # Silver for unconnected
            
            # Draw pin pad
            pin_stroke_width = max(0.1, base_scale * 0.1)
            if pin['shape'] == 'circle':
                radius = max(pin['width'], pin['height']) / 2
                svg_content += f'''  <circle cx="{pin_x:.1f}" cy="{pin_y:.1f}" r="{radius:.1f}" 
                 fill="{pin_color}" stroke="#333" stroke-width="{pin_stroke_width:.1f}"/>
  
'''
            else:
                # Rectangle pad
                pad_w = pin['width']
                pad_h = pin['height']
                svg_content += f'''  <rect x="{pin_x - pad_w/2:.1f}" y="{pin_y - pad_h/2:.1f}" 
                 width="{pad_w:.1f}" height="{pad_h:.1f}" 
                 fill="{pin_color}" stroke="#333" stroke-width="{pin_stroke_width:.1f}"/>
  
'''
            
            # Pin number
            if pin['number']:
                pin_font_size = min(max(pin['width'], pin['height']) / 2, svg_width / 40, 4)
                svg_content += f'''  <text x="{pin_x:.1f}" y="{pin_y + pin_font_size/2:.1f}" text-anchor="middle" 
                 fill="black" font-family="Arial, sans-serif" font-size="{pin_font_size:.1f}" font-weight="bold">
      {pin['number']}
    </text>
    
'''
            
            # Draw drill hole if present
            if pin['drill'] > 0:
                drill_radius = pin['drill'] / 2
                drill_stroke_width = max(0.05, base_scale * 0.05)
                svg_content += f'''  <circle cx="{pin_x:.1f}" cy="{pin_y:.1f}" r="{drill_radius:.1f}" 
                 fill="#2d5016" stroke="#000" stroke-width="{drill_stroke_width:.1f}"/>
  
'''
    
    # Close SVG
    svg_content += '</svg>'
    
    # Save SVG
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"SVG saved to: {output_path}")
    print(f"Components: {len(components)}")
    print(f"Total pins: {sum(len(c['pins']) for c in components)}")
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Create SVG visualization of PCB components and pins from KiCad PCB JSON data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pcb_to_svg.py board.json
  python pcb_to_svg.py board.json output.svg
  python pcb_to_svg.py path/to/project.json custom_name.svg
        """
    )
    
    parser.add_argument('input', help='Input PCB JSON file path')
    parser.add_argument('output', nargs='?', help='Output SVG file path (optional)')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Show detailed component summary')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file '{input_path}' does not exist")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.json':
        print(f"WARNING: Input file '{input_path}' does not have .json extension")
    
    # Generate output filename if not provided
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.svg')
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating PCB SVG visualization...")
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    
    try:
        # Load and process PCB data
        pcb_data = load_pcb_data(input_path)
        components = extract_component_data(pcb_data)
        
        if not components:
            print("ERROR: No components found with reference designators")
            sys.exit(1)
        
        # Create SVG
        pcb_name = input_path.stem
        success = create_svg(components, output_path, pcb_name)
        
        if success:
            if args.verbose:
                print("\nComponent Summary:")
                for comp in components:
                    pin_count = len(comp['pins'])
                    print(f"  {comp['reference']:8s} | {comp['footprint_type']:20s} | {pin_count:2d} pins | {comp['value']}")
            
            print(f"\nVisualization complete! Open {output_path} in a web browser to view.")
        else:
            print("ERROR: Failed to create SVG visualization")
            sys.exit(1)
            
    except FileNotFoundError:
        print(f"ERROR: Could not read input file '{input_path}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in input file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()