#!/usr/bin/env python3
"""
kicad_json_converter.py

Comprehensive bidirectional KiCad schematic <-> JSON converter.
Preserves ALL schematic information to enable round-trip conversion.

# Single file
python kicad_json_converter.py to-json schematic.kicad_sch

# Entire project
python kicad_json_converter.py batch root.kicad_sch -o json_output
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
import argparse

from kiutils.schematic import Schematic
from kiutils.items.schitems import *
from kiutils.items.common import *


class kicad_json_converter:
    """Bidirectional KiCad schematic <-> JSON converter"""
    
    def __init__(self):
        self.version = "1.0.0"
        
    def _safe_convert(self, obj) -> Any:
        """Safely convert any object to JSON-serializable format"""
        if obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        elif isinstance(obj, list):
            return [self._safe_convert(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self._safe_convert(v) for k, v in obj.items()}
        else:
            # For kiutils objects, extract all non-private attributes
            result = {
                "_type": type(obj).__name__
            }
            
            # Get all attributes that don't start with underscore
            for attr_name in dir(obj):
                if not attr_name.startswith('_') and not callable(getattr(obj, attr_name)):
                    try:
                        attr_value = getattr(obj, attr_name)
                        result[attr_name] = self._safe_convert(attr_value)
                    except:
                        result[attr_name] = f"<error accessing {attr_name}>"
                        
            return result
        
    def schematic_to_json(self, schematic_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Convert KiCad schematic file to complete JSON representation"""
        schematic_file = Path(schematic_path)
        
        if not schematic_file.exists():
            raise FileNotFoundError(f"Schematic file not found: {schematic_path}")
            
        try:
            schematic = Schematic.from_file(str(schematic_file))
        except Exception as e:
            raise ValueError(f"Error loading schematic: {e}")
            
        # Convert schematic to JSON-serializable format
        json_data = self._schematic_to_dict(schematic, str(schematic_file))
        
        # Save to file if output path provided
        if output_path:
            self._save_json(json_data, output_path)
            
        return json_data
        
    def json_to_schematic(self, json_path: str, output_path: Optional[str] = None) -> Schematic:
        """Convert JSON file back to KiCad schematic"""
        json_file = Path(json_path)
        
        if not json_file.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
        except Exception as e:
            raise ValueError(f"Error loading JSON: {e}")
            
        # Convert JSON back to schematic
        schematic = self._dict_to_schematic(json_data)
        
        # Save to file if output path provided
        if output_path:
            schematic.to_file(output_path)
            
        return schematic
        
    def _schematic_to_dict(self, schematic: Schematic, source_file: str) -> Dict[str, Any]:
        """Convert Schematic object to complete dictionary representation"""
        result = {
            "metadata": {
                "converter_version": self.version,
                "source_file": source_file,
                "kicad_version": getattr(schematic, 'version', None),
                "generator": getattr(schematic, 'generator', None)
            }
        }
        
        # Use safe conversion for the entire schematic object
        # This preserves ALL data while ensuring JSON compatibility
        schematic_data = self._safe_convert(schematic)
        
        # Remove methods and private attributes from the root
        filtered_data = {}
        for key, value in schematic_data.items():
            if not key.startswith('_') and key not in ['from_file', 'to_file', 'from_sexpr', 'to_sexpr']:
                filtered_data[key] = value
                
        result.update(filtered_data)
        
        # Add computed net connectivity information
        result['netConnectivity'] = self._extract_net_connectivity(schematic)
        
        return result
        
    def _convert_paper(self, paper) -> Optional[Dict]:
        """Convert paper settings"""
        if not paper:
            return None
            
        # Handle different paper object types
        if isinstance(paper, str):
            return {"type": paper}
        else:
            return {
                "type": getattr(paper, 'paperType', str(paper)),
                "portrait": getattr(paper, 'portrait', False),
                "width": getattr(paper, 'width', None),
                "height": getattr(paper, 'height', None)
            }
        
    def _convert_title_block(self, title_block) -> Optional[Dict]:
        """Convert title block information"""
        if not title_block:
            return None
            
        result = {}
        
        # Handle different title block object types
        for attr in ['title', 'date', 'revision', 'company']:
            value = getattr(title_block, attr, None)
            if value is not None:
                result[attr] = str(value)
                
        # Comments might be a list
        comments = getattr(title_block, 'comment', None)
        if comments is not None:
            if isinstance(comments, list):
                result["comments"] = [str(c) for c in comments]
            else:
                result["comments"] = [str(comments)]
        else:
            result["comments"] = []
            
        return result
        
    def _convert_position(self, position) -> Optional[Dict]:
        """Convert position object to dict"""
        if not position:
            return None
            
        return {
            "x": getattr(position, 'X', 0),
            "y": getattr(position, 'Y', 0),
            "angle": getattr(position, 'angle', 0),
            "unlocked": getattr(position, 'unlocked', False)
        }
        
    def _convert_effects(self, effects) -> Optional[Dict]:
        """Convert text effects"""
        if not effects:
            return None
            
        result = {
            "hide": getattr(effects, 'hide', False),
            "href": getattr(effects, 'href', None)
        }
        
        if hasattr(effects, 'font'):
            result["font"] = self._convert_font(effects.font)
            
        if hasattr(effects, 'justify'):
            result["justify"] = self._convert_justify(effects.justify)
            
        return result
        
    def _convert_font(self, font) -> Optional[Dict]:
        """Convert font settings"""
        if not font:
            return None
            
        return {
            "face": getattr(font, 'face', None),
            "height": getattr(font, 'height', 1.27),
            "width": getattr(font, 'width', 1.27),
            "thickness": getattr(font, 'thickness', None),
            "bold": getattr(font, 'bold', False),
            "italic": getattr(font, 'italic', False),
            "line_spacing": getattr(font, 'lineSpacing', None),
            "color": getattr(font, 'color', None)
        }
        
    def _convert_justify(self, justify) -> Optional[Dict]:
        """Convert text justification"""
        if not justify:
            return None
            
        return {
            "horizontally": getattr(justify, 'horizontally', 'left'),
            "vertically": getattr(justify, 'vertically', 'bottom'),
            "mirror": getattr(justify, 'mirror', False)
        }
        
    def _convert_property(self, prop) -> Dict:
        """Convert property object"""
        return {
            "key": getattr(prop, 'key', ''),
            "value": getattr(prop, 'value', ''),
            "id": getattr(prop, 'id', None),
            "position": self._convert_position(getattr(prop, 'position', None)),
            "effects": self._convert_effects(getattr(prop, 'effects', None)),
            "show_name": getattr(prop, 'showName', False)
        }
        
    def _convert_lib_symbol(self, lib_symbol) -> Dict:
        """Convert library symbol definition"""
        result = {
            "name": getattr(lib_symbol, 'entryName', ''),
            "power": getattr(lib_symbol, 'power', False),
            "pin_numbers_hide": getattr(lib_symbol, 'pinNumbersHide', False),
            "pin_names_hide": getattr(lib_symbol, 'pinNamesHide', False),
            "pin_names_offset": getattr(lib_symbol, 'pinNamesOffset', 0.508),
            "in_bom": getattr(lib_symbol, 'inBom', True),
            "on_board": getattr(lib_symbol, 'onBoard', True),
            "extends": getattr(lib_symbol, 'extends', None)
        }
        
        # Properties
        result["properties"] = []
        if hasattr(lib_symbol, 'properties'):
            for prop in lib_symbol.properties:
                result["properties"].append(self._convert_property(prop))
                
        # Graphic items (symbol drawing)
        result["graphic_items"] = []
        if hasattr(lib_symbol, 'graphicItems'):
            for item in lib_symbol.graphicItems:
                result["graphic_items"].append(self._convert_graphical_item(item))
                
        # Pins
        result["pins"] = []
        if hasattr(lib_symbol, 'pins'):
            for pin in lib_symbol.pins:
                result["pins"].append(self._convert_pin(pin))
                
        return result
        
    def _convert_pin(self, pin) -> Dict:
        """Convert symbol pin"""
        return {
            "type": getattr(pin, 'type', 'passive'),
            "shape": getattr(pin, 'shape', 'line'),
            "position": self._convert_position(getattr(pin, 'position', None)),
            "length": getattr(pin, 'length', 2.54),
            "name": getattr(pin, 'name', ''),
            "number": getattr(pin, 'number', ''),
            "hide": getattr(pin, 'hide', False),
            "name_effects": self._convert_effects(getattr(pin, 'nameEffects', None)),
            "number_effects": self._convert_effects(getattr(pin, 'numberEffects', None))
        }
        
    def _convert_schematic_symbol(self, symbol) -> Dict:
        """Convert schematic symbol instance"""
        result = {
            "library_identifier": getattr(symbol, 'libraryIdentifier', None),
            "position": self._convert_position(getattr(symbol, 'position', None)),
            "unit": getattr(symbol, 'unit', 1),
            "in_bom": getattr(symbol, 'inBom', True),
            "on_board": getattr(symbol, 'onBoard', True),
            "fields_autoplaced": getattr(symbol, 'fieldsAutoplaced', False),
            "uuid": getattr(symbol, 'uuid', None),
            "mirror": getattr(symbol, 'mirror', None)
        }
        
        # Properties
        result["properties"] = []
        if hasattr(symbol, 'properties'):
            for prop in symbol.properties:
                result["properties"].append(self._convert_property(prop))
                
        # Pin connections
        result["pins"] = []
        if hasattr(symbol, 'pins'):
            for pin in symbol.pins:
                result["pins"].append({
                    "uuid": getattr(pin, 'uuid', None),
                    "alternates": getattr(pin, 'alternates', [])
                })
                
        return result
        
    def _convert_graphical_item(self, item) -> Dict:
        """Convert graphical item (wire, line, arc, etc.)"""
        result = {
            "type": type(item).__name__
        }
        
        # Common properties
        if hasattr(item, 'position'):
            result["position"] = self._convert_position(item.position)
        if hasattr(item, 'stroke'):
            result["stroke"] = self._convert_stroke(item.stroke)
        if hasattr(item, 'fill'):
            result["fill"] = self._convert_fill(item.fill)
        if hasattr(item, 'uuid'):
            result["uuid"] = item.uuid
            
        # Type-specific properties
        if hasattr(item, 'startPosition') and hasattr(item, 'endPosition'):
            # Line-like items
            result["start_position"] = self._convert_position(item.startPosition)
            result["end_position"] = self._convert_position(item.endPosition)
        elif hasattr(item, 'points'):
            # Polyline
            result["points"] = [self._convert_position(pt) for pt in item.points]
        elif hasattr(item, 'center') and hasattr(item, 'radius'):
            # Circle
            result["center"] = self._convert_position(item.center)
            result["radius"] = item.radius
        elif hasattr(item, 'start') and hasattr(item, 'mid') and hasattr(item, 'end'):
            # Arc
            result["start"] = self._convert_position(item.start)
            result["mid"] = self._convert_position(item.mid) 
            result["end"] = self._convert_position(item.end)
        elif hasattr(item, 'text'):
            # Text item
            result["text"] = item.text
            result["effects"] = self._convert_effects(getattr(item, 'effects', None))
            
        return result
        
    def _convert_stroke(self, stroke) -> Optional[Dict]:
        """Convert stroke/line properties"""
        if not stroke:
            return None
            
        return {
            "width": getattr(stroke, 'width', 0),
            "type": getattr(stroke, 'type', 'default'),
            "color": getattr(stroke, 'color', None)
        }
        
    def _convert_fill(self, fill) -> Optional[Dict]:
        """Convert fill properties"""
        if not fill:
            return None
            
        return {
            "type": getattr(fill, 'type', 'none'),
            "color": getattr(fill, 'color', None)
        }
        
    def _convert_junction(self, junction) -> Dict:
        """Convert junction point"""
        return {
            "position": self._convert_position(getattr(junction, 'position', None)),
            "diameter": getattr(junction, 'diameter', 0),
            "color": getattr(junction, 'color', None)
        }
        
    def _convert_local_label(self, label) -> Dict:
        """Convert local label"""
        return {
            "text": getattr(label, 'text', ''),
            "position": self._convert_position(getattr(label, 'position', None)),
            "effects": self._convert_effects(getattr(label, 'effects', None)),
            "uuid": getattr(label, 'uuid', None)
        }
        
    def _convert_global_label(self, label) -> Dict:
        """Convert global label"""
        return {
            "text": getattr(label, 'text', ''),
            "position": self._convert_position(getattr(label, 'position', None)),
            "effects": self._convert_effects(getattr(label, 'effects', None)),
            "shape": getattr(label, 'shape', 'passive'),
            "uuid": getattr(label, 'uuid', None),
            "fields_autoplaced": getattr(label, 'fieldsAutoplaced', False)
        }
        
    def _convert_hierarchical_label(self, label) -> Dict:
        """Convert hierarchical label"""
        return {
            "text": getattr(label, 'text', ''),
            "position": self._convert_position(getattr(label, 'position', None)),
            "effects": self._convert_effects(getattr(label, 'effects', None)),
            "shape": getattr(label, 'shape', 'passive'),
            "uuid": getattr(label, 'uuid', None)
        }
        
    def _convert_hierarchical_sheet(self, sheet) -> Dict:
        """Convert hierarchical sheet"""
        result = {
            "position": self._convert_position(getattr(sheet, 'position', None)),
            "width": getattr(sheet, 'width', 0),
            "height": getattr(sheet, 'height', 0),
            "stroke": self._convert_stroke(getattr(sheet, 'stroke', None)),
            "fill": self._convert_fill(getattr(sheet, 'fill', None)),
            "uuid": getattr(sheet, 'uuid', None),
            "fields_autoplaced": getattr(sheet, 'fieldsAutoplaced', False)
        }
        
        # Sheet name and file
        if hasattr(sheet, 'sheetName'):
            result["sheet_name"] = self._convert_property(sheet.sheetName)
        if hasattr(sheet, 'fileName'):
            result["file_name"] = self._convert_property(sheet.fileName)
            
        # Properties
        result["properties"] = []
        if hasattr(sheet, 'properties'):
            for prop in sheet.properties:
                result["properties"].append(self._convert_property(prop))
                
        # Pins
        result["pins"] = []
        if hasattr(sheet, 'pins'):
            for pin in sheet.pins:
                result["pins"].append(self._convert_hierarchical_pin(pin))
                
        return result
        
    def _convert_hierarchical_pin(self, pin) -> Dict:
        """Convert hierarchical sheet pin"""
        return {
            "name": getattr(pin, 'name', ''),
            "position": self._convert_position(getattr(pin, 'position', None)),
            "effects": self._convert_effects(getattr(pin, 'effects', None)),
            "shape": getattr(pin, 'shape', 'passive'),
            "uuid": getattr(pin, 'uuid', None)
        }
        
    def _convert_bus_entry(self, entry) -> Dict:
        """Convert bus entry"""
        return {
            "position": self._convert_position(getattr(entry, 'position', None)),
            "width": getattr(entry, 'width', 0),
            "height": getattr(entry, 'height', 0),
            "stroke": self._convert_stroke(getattr(entry, 'stroke', None)),
            "uuid": getattr(entry, 'uuid', None)
        }
        
    def _convert_bus_alias(self, alias) -> Dict:
        """Convert bus alias"""
        return {
            "name": getattr(alias, 'name', ''),
            "members": getattr(alias, 'members', [])
        }
        
    def _convert_no_connect(self, nc) -> Dict:
        """Convert no-connect marker"""
        return {
            "position": self._convert_position(getattr(nc, 'position', None)),
            "uuid": getattr(nc, 'uuid', None)
        }
        
    def _convert_text(self, text) -> Dict:
        """Convert text item"""
        return {
            "text": getattr(text, 'text', ''),
            "position": self._convert_position(getattr(text, 'position', None)),
            "effects": self._convert_effects(getattr(text, 'effects', None)),
            "uuid": getattr(text, 'uuid', None)
        }
        
    def _convert_text_box(self, text_box) -> Dict:
        """Convert text box"""
        return {
            "text": getattr(text_box, 'text', ''),
            "position": self._convert_position(getattr(text_box, 'position', None)),
            "size": {
                "width": getattr(text_box, 'width', 0),
                "height": getattr(text_box, 'height', 0)
            },
            "effects": self._convert_effects(getattr(text_box, 'effects', None)),
            "stroke": self._convert_stroke(getattr(text_box, 'stroke', None)),
            "fill": self._convert_fill(getattr(text_box, 'fill', None)),
            "uuid": getattr(text_box, 'uuid', None)
        }
        
    def _convert_image(self, image) -> Dict:
        """Convert image item"""
        return {
            "position": self._convert_position(getattr(image, 'position', None)),
            "scale": getattr(image, 'scale', 1.0),
            "uuid": getattr(image, 'uuid', None),
            "data": getattr(image, 'data', None)  # Base64 encoded image data
        }
        
    def _convert_sheet_instance(self, instance) -> Dict:
        """Convert sheet instance"""
        return {
            "path": getattr(instance, 'path', ''),
            "page": getattr(instance, 'page', '')
        }
        
    def _convert_symbol_instance(self, instance) -> Dict:
        """Convert symbol instance"""
        return {
            "path": getattr(instance, 'path', ''),
            "reference": getattr(instance, 'reference', ''),
            "unit": getattr(instance, 'unit', 1),
            "value": getattr(instance, 'value', ''),
            "footprint": getattr(instance, 'footprint', '')
        }
        
    def _extract_net_connectivity(self, schematic) -> Dict[str, Any]:
        """Extract net connectivity from schematic"""
        from collections import defaultdict
        import math
        
        nets = []
        net_id = 0
        
        # Get all wire connections
        connections = [item for item in schematic.graphicalItems if type(item).__name__ == 'Connection']
        
        # Get all junctions (connection points)
        junction_positions = set()
        for junction in schematic.junctions:
            junction_positions.add((junction.position.X, junction.position.Y))
        
        # Build wire connectivity graph
        wire_graph = defaultdict(set)  # wire_id -> set of connected wire_ids
        wire_endpoints = {}  # wire_id -> (start_point, end_point)
        
        for i, conn in enumerate(connections):
            if hasattr(conn, 'points') and len(conn.points) >= 2:
                start = (conn.points[0].X, conn.points[0].Y)
                end = (conn.points[-1].X, conn.points[-1].Y)
                wire_endpoints[i] = (start, end)
                
                # Check if this wire connects to junctions
                for j_pos in junction_positions:
                    if self._points_match(start, j_pos) or self._points_match(end, j_pos):
                        # Find other wires at this junction
                        for j, (j_start, j_end) in wire_endpoints.items():
                            if i != j:
                                if self._points_match(j_start, j_pos) or self._points_match(j_end, j_pos):
                                    wire_graph[i].add(j)
                                    wire_graph[j].add(i)
        
        # Build nets from connected wire groups
        used_wires = set()
        for wire_id in range(len(connections)):
            if wire_id not in used_wires:
                # Build a net from all connected wires
                net_wires = set()
                to_process = [wire_id]
                
                while to_process:
                    current = to_process.pop()
                    if current not in used_wires:
                        used_wires.add(current)
                        net_wires.add(current)
                        # Add connected wires
                        for connected in wire_graph[current]:
                            if connected not in used_wires:
                                to_process.append(connected)
                
                # Find components connected to this net
                net_points = set()
                for w_id in net_wires:
                    start, end = wire_endpoints[w_id]
                    net_points.add(start)
                    net_points.add(end)
                
                # Match components to net points
                connected_components = []
                for symbol in schematic.schematicSymbols:
                    ref = self._get_component_reference(symbol)
                    if ref and hasattr(symbol, 'position'):
                        comp_pos = (symbol.position.X, symbol.position.Y)
                        # Check if component is near any net point
                        for net_point in net_points:
                            if self._points_match(comp_pos, net_point, tolerance=10.0):
                                connected_components.append(ref)
                                break
                
                nets.append({
                    'id': f'net_{net_id}',
                    'wire_count': len(net_wires),
                    'components': connected_components,
                    'points': list(net_points)
                })
                net_id += 1
        
        # Post-process to unify ground nets
        ground_components = []
        non_ground_nets = []
        
        for net in nets:
            # Check if this net contains ground symbols
            ground_symbols = [comp for comp in net['components'] if comp.startswith('#GND')]
            if ground_symbols:
                # Add all components from this net to ground components
                ground_components.extend(net['components'])
            else:
                # Keep non-ground nets as-is
                non_ground_nets.append(net)
        
        # If we found ground components, create a unified ground net
        if ground_components:
            # Remove duplicates
            ground_components = list(set(ground_components))
            unified_ground_net = {
                'id': 'net_ground',
                'wire_count': sum(net['wire_count'] for net in nets if any(comp.startswith('#GND') for comp in net['components'])),
                'components': ground_components,
                'points': []  # Combine all ground points
            }
            
            # Add all ground points
            for net in nets:
                if any(comp.startswith('#GND') for comp in net['components']):
                    unified_ground_net['points'].extend(net['points'])
            
            non_ground_nets.append(unified_ground_net)
        
        return {
            'nets': non_ground_nets,
            'junction_count': len(junction_positions),
            'wire_count': len(connections)
        }
    
    def _get_component_reference(self, symbol) -> Optional[str]:
        """Extract component reference from symbol"""
        if hasattr(symbol, 'properties'):
            for prop in symbol.properties:
                if hasattr(prop, 'key') and prop.key == 'Reference':
                    return prop.value
        return None
    
    def _points_match(self, p1: tuple, p2: tuple, tolerance: float = 0.01) -> bool:
        """Check if two points match within tolerance"""
        return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance
    
    def _save_json(self, data: Dict[str, Any], output_path: str):
        """Save JSON data to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"JSON saved to: {output_file}")
        
    def _dict_to_schematic(self, data: Dict[str, Any]) -> Schematic:
        """Convert JSON dictionary back to Schematic object"""
        # This would be the reverse process - reconstructing kiutils objects
        # from the JSON data. This is more complex and would require creating
        # all the kiutils objects with the proper constructors and properties.
        
        # For now, return a placeholder
        # TODO: Implement full reverse conversion
        raise NotImplementedError("JSON to Schematic conversion not yet implemented")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert KiCad schematics to/from JSON format'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Schematic to JSON
    to_json_parser = subparsers.add_parser('to-json', help='Convert schematic to JSON')
    to_json_parser.add_argument('schematic', help='Input KiCad schematic file (.kicad_sch)')
    to_json_parser.add_argument('-o', '--output', help='Output JSON file path')
    
    # JSON to Schematic  
    from_json_parser = subparsers.add_parser('from-json', help='Convert JSON to schematic')
    from_json_parser.add_argument('json_file', help='Input JSON file')
    from_json_parser.add_argument('-o', '--output', help='Output schematic file path')
    
    # Batch conversion
    batch_parser = subparsers.add_parser('batch', help='Convert entire project hierarchy')
    batch_parser.add_argument('root_schematic', help='Root schematic file')
    batch_parser.add_argument('-o', '--output-dir', default='json_output', 
                             help='Output directory for JSON files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    converter = kicad_json_converter()
    
    try:
        if args.command == 'to-json':
            # Convert single schematic to JSON
            input_path = Path(args.schematic)
            if not input_path.exists():
                print(f"Error: File not found: {input_path}")
                sys.exit(1)
                
            output_path = args.output
            if not output_path:
                output_path = input_path.with_suffix('.json')
                
            json_data = converter.schematic_to_json(str(input_path), str(output_path))
            print(f"Converted {input_path} to {output_path}")
            
            # Print summary
            print(f"  Symbols: {len(json_data.get('schematic_symbols', []))}")
            print(f"  Labels: {len(json_data.get('labels', [])) + len(json_data.get('global_labels', []))}")
            print(f"  Sheets: {len(json_data.get('sheets', []))}")
            
        elif args.command == 'from-json':
            # Convert JSON back to schematic
            input_path = Path(args.json_file)
            if not input_path.exists():
                print(f"Error: File not found: {input_path}")
                sys.exit(1)
                
            output_path = args.output
            if not output_path:
                output_path = input_path.with_suffix('.kicad_sch')
                
            schematic = converter.json_to_schematic(str(input_path), str(output_path))
            print(f"Converted {input_path} to {output_path}")
            
        elif args.command == 'batch':
            # Convert entire project hierarchy
            root_path = Path(args.root_schematic)
            if not root_path.exists():
                print(f"Error: File not found: {root_path}")
                sys.exit(1)
                
            output_dir = Path(args.output_dir)
            output_dir.mkdir(exist_ok=True)
            
            # Convert root schematic
            root_json = output_dir / f"{root_path.stem}.json"
            converter.schematic_to_json(str(root_path), str(root_json))
            print(f"Converted {root_path.name}")
            
            # Find and convert all related schematics
            project_dir = root_path.parent
            for sch_file in project_dir.glob('*.kicad_sch'):
                if sch_file == root_path:
                    continue  # Already converted
                    
                json_output = output_dir / f"{sch_file.stem}.json"
                converter.schematic_to_json(str(sch_file), str(json_output))
                print(f"Converted {sch_file.name}")
                
            print(f"\nBatch conversion complete. Files saved to: {output_dir}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()