#!/usr/bin/env python3
"""
KiCad Schematic to JSON Converter

Converts KiCad .kicad_sch files to structured JSON format for analysis and processing.
Maintains net connectivity information and component relationships.

Requirements:
    pip install kiutils

Usage:
    python kicad_sch_to_json.py <input.kicad_sch> [output.json]
    python kicad_sch_to_json.py --help
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import math
from collections import defaultdict

try:
    from kiutils.schematic import Schematic
    from kiutils.items.schitems import SchematicSymbol
except ImportError:
    print("ERROR: kiutils library not found. Install with: pip install kiutils")
    sys.exit(1)


class KicadSchematicToJsonConverter:
    """Converts KiCad schematic files to structured JSON format with net connectivity."""
    
    def __init__(self, tolerance: float = 5.0):
        """
        Initialize converter.
        
        Args:
            tolerance: Distance tolerance for wire endpoint matching (mm)
        """
        self.tolerance = tolerance
        self.net_counter = 0
        self.junction_map = {}
        self.wire_segments = []
        self.component_pins = {}
        
    def points_match(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
        """Check if two points match within tolerance."""
        return abs(p1[0] - p2[0]) < self.tolerance and abs(p1[1] - p2[1]) < self.tolerance
    
    def safe_get_property(self, obj: Any, prop: str, default: Any = None) -> Any:
        """Safely get property from object."""
        try:
            value = getattr(obj, prop, default)
            # Handle Property objects by extracting their value
            if hasattr(value, 'value'):  # This is likely a Property object
                return str(value.value) if value.value else str(default)
            return value
        except:
            return default
    
    def extract_component_properties(self, symbol: SchematicSymbol) -> Dict[str, Any]:
        """Extract properties from schematic symbol."""
        props = {}
        
        # Get basic properties
        if hasattr(symbol, 'properties') and symbol.properties:
            for prop in symbol.properties:
                if hasattr(prop, 'key') and hasattr(prop, 'value'):
                    # Extract only the string values, not the complex Property objects
                    key = str(prop.key) if prop.key else 'Unknown'
                    value = str(prop.value) if prop.value else ''
                    props[key] = value
        
        # Extract common properties with defaults
        reference = props.get('Reference', 'Unknown')
        value = props.get('Value', 'Unknown')
        footprint = props.get('Footprint', '')
        
        # Get position
        position = {'x': 0.0, 'y': 0.0, 'angle': 0.0}
        if hasattr(symbol, 'position') and symbol.position:
            position['x'] = self.safe_get_property(symbol.position, 'X', 0.0)
            position['y'] = self.safe_get_property(symbol.position, 'Y', 0.0)
            position['angle'] = self.safe_get_property(symbol.position, 'angle', 0.0)
        
        # Get library information
        library = self.safe_get_property(symbol, 'libraryIdentifier', 'Unknown')
        
        # Get UUID
        uuid = self.safe_get_property(symbol, 'uuid', '')
        
        return {
            'reference': reference,
            'value': value,
            'footprint': footprint,
            'library': library,
            'position': position,
            'uuid': uuid,
            'all_properties': props
        }
    
    def build_junction_map(self, schematic: Schematic) -> Dict[Tuple[float, float], str]:
        """Build map of junction positions to junction IDs."""
        junction_map = {}
        
        if hasattr(schematic, 'junctions') and schematic.junctions:
            for i, junction in enumerate(schematic.junctions):
                if hasattr(junction, 'position'):
                    pos = (
                        self.safe_get_property(junction.position, 'X', 0.0),
                        self.safe_get_property(junction.position, 'Y', 0.0)
                    )
                    junction_map[pos] = f"junction_{i}"
        
        return junction_map
    
    def extract_wire_segments(self, schematic: Schematic) -> List[Dict[str, Any]]:
        """Extract wire segments from graphical items."""
        wire_segments = []
        
        if hasattr(schematic, 'graphicalItems') and schematic.graphicalItems:
            for item in schematic.graphicalItems:
                if type(item).__name__ == 'Connection' and hasattr(item, 'points'):
                    if len(item.points) >= 2:
                        start_point = (
                            self.safe_get_property(item.points[0], 'X', 0.0),
                            self.safe_get_property(item.points[0], 'Y', 0.0)
                        )
                        end_point = (
                            self.safe_get_property(item.points[-1], 'X', 0.0),
                            self.safe_get_property(item.points[-1], 'Y', 0.0)
                        )
                        
                        wire_segments.append({
                            'start': start_point,
                            'end': end_point,
                            'uuid': self.safe_get_property(item, 'uuid', ''),
                            'points': [(self.safe_get_property(p, 'X', 0.0), 
                                      self.safe_get_property(p, 'Y', 0.0)) for p in item.points]
                        })
        
        return wire_segments
    
    def compute_net_connectivity(self, components: List[Dict], wire_segments: List[Dict], 
                                junction_map: Dict) -> Dict[str, Any]:
        """Compute electrical net connectivity from geometry."""
        
        # Build graph of connected points
        connected_points = defaultdict(set)
        all_points = set()
        
        # Add junction connections
        for junction_pos in junction_map.keys():
            all_points.add(junction_pos)
        
        # Add wire connections
        for wire in wire_segments:
            start = wire['start']
            end = wire['end']
            all_points.add(start)
            all_points.add(end)
            
            # Connect wire endpoints directly
            connected_points[start].add(end)
            connected_points[end].add(start)
            
            # Connect to junctions within tolerance
            for junction_pos in junction_map.keys():
                if self.points_match(start, junction_pos):
                    connected_points[start].add(junction_pos)
                    connected_points[junction_pos].add(start)
                if self.points_match(end, junction_pos):
                    connected_points[end].add(junction_pos)
                    connected_points[junction_pos].add(end)
        
        # Find connected components using DFS
        visited = set()
        nets = []
        
        def dfs(point, current_net_points):
            if point in visited:
                return
            visited.add(point)
            current_net_points.add(point)
            
            for connected_point in connected_points[point]:
                dfs(connected_point, current_net_points)
        
        for point in all_points:
            if point not in visited:
                net_points = set()
                dfs(point, net_points)
                if net_points:
                    nets.append(net_points)
        
        # Convert to structured format and match components
        structured_nets = []
        for i, net_points in enumerate(nets):
            net_id = f"net_{i}"
            
            # Find components connected to this net
            connected_components = []
            for component in components:
                comp_pos = (component['position']['x'], component['position']['y'])
                
                # Check if component is near any net point
                for net_point in net_points:
                    if self.points_match(comp_pos, net_point):
                        connected_components.append({
                            'reference': component['reference'],
                            'value': component['value'],
                            'library': component['library']
                        })
                        break
            
            # Handle ground symbol unification
            has_ground = any('GND' in comp['reference'] for comp in connected_components)
            
            structured_nets.append({
                'id': net_id,
                'wire_count': sum(1 for wire in wire_segments 
                                if any(self.points_match(wire['start'], p) or 
                                      self.points_match(wire['end'], p) for p in net_points)),
                'components': connected_components,
                'points': [{'x': p[0], 'y': p[1]} for p in net_points],
                'is_ground': has_ground,
                'junction_count': sum(1 for junction_pos in junction_map.keys() 
                                    if junction_pos in net_points)
            })
        
        # Unify ground nets
        ground_nets = [net for net in structured_nets if net['is_ground']]
        if len(ground_nets) > 1:
            # Merge all ground nets into the first one
            unified_ground = ground_nets[0]
            unified_ground['id'] = 'unified_ground'
            
            for ground_net in ground_nets[1:]:
                unified_ground['components'].extend(ground_net['components'])
                unified_ground['points'].extend(ground_net['points'])
                unified_ground['wire_count'] += ground_net['wire_count']
                unified_ground['junction_count'] += ground_net['junction_count']
            
            # Remove duplicate components
            seen_refs = set()
            unique_components = []
            for comp in unified_ground['components']:
                if comp['reference'] not in seen_refs:
                    unique_components.append(comp)
                    seen_refs.add(comp['reference'])
            unified_ground['components'] = unique_components
            
            # Remove other ground nets
            structured_nets = [net for net in structured_nets if not net['is_ground']] + [unified_ground]
        
        return {
            'nets': structured_nets,
            'junction_count': len(junction_map),
            'wire_count': len(wire_segments),
            'total_nets': len(structured_nets)
        }
    
    def convert_schematic(self, input_path: Path) -> Dict[str, Any]:
        """Convert KiCad schematic to JSON format."""
        
        try:
            # Load schematic
            schematic = Schematic.from_file(str(input_path))
            
            # Extract metadata
            metadata = {
                'converter_version': '1.0.0',
                'source_file': str(input_path),
                'kicad_version': self.safe_get_property(schematic, 'version', 'unknown'),
                'generator': self.safe_get_property(schematic, 'generator', 'unknown'),
                'uuid': self.safe_get_property(schematic, 'uuid', '')
            }
            
            # Extract components
            components = []
            if hasattr(schematic, 'schematicSymbols') and schematic.schematicSymbols:
                for symbol in schematic.schematicSymbols:
                    component_data = self.extract_component_properties(symbol)
                    components.append(component_data)
            
            # Build connectivity data
            junction_map = self.build_junction_map(schematic)
            wire_segments = self.extract_wire_segments(schematic)
            net_connectivity = self.compute_net_connectivity(components, wire_segments, junction_map)
            
            # Extract other schematic elements
            sheets = []
            if hasattr(schematic, 'sheets') and schematic.sheets:
                for sheet in schematic.sheets:
                    sheet_data = {
                        'name': self.safe_get_property(sheet, 'sheetName', 'Unknown'),
                        'file': self.safe_get_property(sheet, 'fileName', ''),
                        'uuid': self.safe_get_property(sheet, 'uuid', '')
                    }
                    if hasattr(sheet, 'position'):
                        sheet_data['position'] = {
                            'x': self.safe_get_property(sheet.position, 'X', 0.0),
                            'y': self.safe_get_property(sheet.position, 'Y', 0.0)
                        }
                    sheets.append(sheet_data)
            
            # Extract labels
            labels = []
            if hasattr(schematic, 'labels') and schematic.labels:
                for label in schematic.labels:
                    label_data = {
                        'text': self.safe_get_property(label, 'text', ''),
                        'uuid': self.safe_get_property(label, 'uuid', ''),
                        'type': 'local'
                    }
                    if hasattr(label, 'position'):
                        label_data['position'] = {
                            'x': self.safe_get_property(label.position, 'X', 0.0),
                            'y': self.safe_get_property(label.position, 'Y', 0.0)
                        }
                    labels.append(label_data)
            
            # Global labels
            if hasattr(schematic, 'globalLabels') and schematic.globalLabels:
                for label in schematic.globalLabels:
                    label_data = {
                        'text': self.safe_get_property(label, 'text', ''),
                        'uuid': self.safe_get_property(label, 'uuid', ''),
                        'type': 'global'
                    }
                    if hasattr(label, 'position'):
                        label_data['position'] = {
                            'x': self.safe_get_property(label.position, 'X', 0.0),
                            'y': self.safe_get_property(label.position, 'Y', 0.0)
                        }
                    labels.append(label_data)
            
            # Hierarchical labels
            if hasattr(schematic, 'hierarchicalLabels') and schematic.hierarchicalLabels:
                for label in schematic.hierarchicalLabels:
                    label_data = {
                        'text': self.safe_get_property(label, 'text', ''),
                        'uuid': self.safe_get_property(label, 'uuid', ''),
                        'type': 'hierarchical'
                    }
                    if hasattr(label, 'position'):
                        label_data['position'] = {
                            'x': self.safe_get_property(label.position, 'X', 0.0),
                            'y': self.safe_get_property(label.position, 'Y', 0.0)
                        }
                    labels.append(label_data)
            
            # Extract library symbols
            lib_symbols = []
            if hasattr(schematic, 'libSymbols') and schematic.libSymbols:
                for lib_symbol in schematic.libSymbols:
                    lib_data = {
                        'name': self.safe_get_property(lib_symbol, 'libraryNickname', '') + ':' + 
                               self.safe_get_property(lib_symbol, 'entryName', ''),
                        'library_nickname': self.safe_get_property(lib_symbol, 'libraryNickname', ''),
                        'entry_name': self.safe_get_property(lib_symbol, 'entryName', '')
                    }
                    lib_symbols.append(lib_data)
            
            # Build complete JSON structure
            result = {
                'metadata': metadata,
                'schematic_symbols': components,
                'sheets': sheets,
                'labels': labels,
                'lib_symbols': lib_symbols,
                'net_connectivity': net_connectivity,
                'wire_segments': wire_segments,
                'junctions': [{'position': {'x': pos[0], 'y': pos[1]}, 'id': jid} 
                             for pos, jid in junction_map.items()]
            }
            
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert schematic: {str(e)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert KiCad schematic (.kicad_sch) to JSON format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python kicad_sch_to_json.py input.kicad_sch
  python kicad_sch_to_json.py input.kicad_sch output.json
  python kicad_sch_to_json.py --tolerance 2.5 input.kicad_sch
        """
    )
    
    parser.add_argument('input', help='Input KiCad schematic file (.kicad_sch)')
    parser.add_argument('output', nargs='?', help='Output JSON file (optional)')
    parser.add_argument('--tolerance', type=float, default=5.0,
                       help='Wire endpoint matching tolerance in mm (default: 5.0)')
    parser.add_argument('--indent', type=int, default=2,
                       help='JSON indentation (default: 2)')
    parser.add_argument('--minify', action='store_true',
                       help='Output minified JSON')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file does not exist: {input_path}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.kicad_sch':
        print(f"WARNING: Input file does not have .kicad_sch extension: {input_path}")
    
    # Determine output file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.json')
    
    try:
        # Convert schematic
        converter = KicadSchematicToJsonConverter(tolerance=args.tolerance)
        json_data = converter.convert_schematic(input_path)
        
        # Test JSON serialization before writing
        try:
            json.dumps(json_data)
        except Exception as json_error:
            print(f"JSON serialization error: {json_error}")
            # Try to identify which part fails
            for key, value in json_data.items():
                try:
                    json.dumps({key: value})
                    print(f"Section '{key}' serializes OK")
                except Exception as section_error:
                    print(f"Section '{key}' fails: {section_error}")
                    print(f"Type: {type(value)}")
                    if isinstance(value, list) and value:
                        print(f"First item type: {type(value[0])}")
            raise json_error
        
        # Write JSON
        indent = None if args.minify else args.indent
        separators = (',', ':') if args.minify else None
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=indent, separators=separators, ensure_ascii=False)
        
        # Print summary
        print(f"Successfully converted: {input_path} -> {output_path}")
        print(f"Components: {len(json_data['schematic_symbols'])}")
        print(f"Nets: {json_data['net_connectivity']['total_nets']}")
        print(f"Wire segments: {json_data['net_connectivity']['wire_count']}")
        print(f"Junctions: {json_data['net_connectivity']['junction_count']}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()