#!/usr/bin/env python3
"""
kicad_pcb_json_converter.py

Comprehensive KiCad PCB (.kicad_pcb) to JSON converter using kiutils.
Preserves ALL PCB information for analysis and visualization.

Usage:
python kicad_pcb_json_converter.py to-json board.kicad_pcb
python kicad_pcb_json_converter.py to-json board.kicad_pcb -o output.json
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import argparse

from kiutils.board import Board
from kiutils.items.brditems import *
from kiutils.items.common import *


class KiCadPcbJsonConverter:
    """KiCad PCB to JSON converter using kiutils"""
    
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
        
    def pcb_to_json(self, pcb_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Convert KiCad PCB file to complete JSON representation"""
        pcb_file = Path(pcb_path)
        
        if not pcb_file.exists():
            raise FileNotFoundError(f"PCB file not found: {pcb_path}")
            
        try:
            board = Board.from_file(str(pcb_file))
        except Exception as e:
            raise ValueError(f"Error loading PCB: {e}")
            
        # Convert board to JSON-serializable format
        json_data = self._board_to_dict(board, str(pcb_file))
        
        # Save to file if output path provided
        if output_path:
            self._save_json(json_data, output_path)
            
        return json_data
        
    def _board_to_dict(self, board: Board, source_file: str) -> Dict[str, Any]:
        """Convert Board object to complete dictionary representation"""
        result = {
            "metadata": {
                "converter_version": self.version,
                "source_file": source_file,
                "kicad_version": getattr(board, 'version', None),
                "generator": getattr(board, 'generator', None)
            }
        }
        
        # Use safe conversion for the entire board object
        board_data = self._safe_convert(board)
        
        # Remove methods and private attributes from the root
        filtered_data = {}
        for key, value in board_data.items():
            if not key.startswith('_') and key not in ['from_file', 'to_file', 'from_sexpr', 'to_sexpr']:
                filtered_data[key] = value
                
        result.update(filtered_data)
        
        # Add computed information
        result['computed_info'] = self._extract_computed_info(board)
        
        return result
        
    def _extract_computed_info(self, board: Board) -> Dict[str, Any]:
        """Extract computed information from PCB for analysis"""
        info = {
            'layer_count': len(getattr(board, 'layers', [])),
            'footprint_count': len(getattr(board, 'footprints', [])),
            'track_count': len(getattr(board, 'tracks', [])),
            'via_count': len(getattr(board, 'vias', [])),
            'zone_count': len(getattr(board, 'zones', [])),
            'drawing_count': len(getattr(board, 'graphicalItems', [])),
        }
        
        # Analyze footprints
        if hasattr(board, 'footprints'):
            footprint_types = {}
            footprint_positions = []
            references = []
            
            for footprint in board.footprints:
                # Get footprint library and name
                lib_ref = getattr(footprint, 'libraryReference', None)
                entry_name = getattr(footprint, 'entryName', None)
                
                if lib_ref and entry_name:
                    full_ref = f"{lib_ref}:{entry_name}"
                elif entry_name:
                    full_ref = entry_name
                else:
                    full_ref = 'unknown'
                    
                if full_ref not in footprint_types:
                    footprint_types[full_ref] = 0
                footprint_types[full_ref] += 1
                
                # Get reference designator from properties
                ref_value = ''
                if hasattr(footprint, 'properties'):
                    for prop in footprint.properties:
                        if hasattr(prop, 'key') and prop.key == 'Reference':
                            ref_value = getattr(prop, 'value', '')
                            break
                
                if ref_value:
                    references.append(ref_value)
                
                # Get position
                if hasattr(footprint, 'position'):
                    pos = footprint.position
                    footprint_positions.append({
                        'reference': ref_value,
                        'library_reference': lib_ref,
                        'entry_name': entry_name,
                        'x': getattr(pos, 'X', 0),
                        'y': getattr(pos, 'Y', 0),
                        'rotation': getattr(pos, 'angle', 0),
                        'side': 'top'  # Could be enhanced to detect layer
                    })
            
            info['footprint_types'] = footprint_types
            info['footprint_positions'] = footprint_positions
            info['component_references'] = sorted(references)
        
        # Analyze layers
        if hasattr(board, 'layers'):
            layer_info = []
            for layer in board.layers:
                layer_info.append({
                    'ordinal': getattr(layer, 'ordinal', 0),
                    'canonical_name': getattr(layer, 'canonicalName', ''),
                    'type': getattr(layer, 'type', ''),
                    'user_name': getattr(layer, 'userName', '')
                })
            info['layers'] = layer_info
        
        # Analyze nets
        if hasattr(board, 'nets'):
            net_info = []
            for net in board.nets:
                net_info.append({
                    'number': getattr(net, 'number', 0),
                    'name': getattr(net, 'name', '')
                })
            info['nets'] = net_info
            info['net_count'] = len(board.nets)
        
        # Board dimensions
        if hasattr(board, 'graphicalItems'):
            # Look for board outline
            outline_segments = []
            for item in board.graphicalItems:
                if (hasattr(item, 'layer') and 
                    getattr(item.layer, 'canonicalName', '') == 'Edge.Cuts'):
                    outline_segments.append({
                        'type': type(item).__name__,
                        'layer': getattr(item.layer, 'canonicalName', '')
                    })
            info['outline_segments'] = outline_segments
        
        return info
        
    def _save_json(self, data: Dict[str, Any], output_path: str):
        """Save JSON data to file"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"JSON saved to: {output_file}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Convert KiCad PCB files to JSON format'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # PCB to JSON
    to_json_parser = subparsers.add_parser('to-json', help='Convert PCB to JSON')
    to_json_parser.add_argument('pcb', help='Input KiCad PCB file (.kicad_pcb)')
    to_json_parser.add_argument('-o', '--output', help='Output JSON file path')
    
    # Batch conversion
    batch_parser = subparsers.add_parser('batch', help='Convert all PCB files in a directory')
    batch_parser.add_argument('directory', help='Directory containing KiCad PCB files')
    batch_parser.add_argument('-o', '--output-dir', default='claude/data_store/pcb', 
                             help='Output directory for JSON files')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    converter = KiCadPcbJsonConverter()
    
    try:
        if args.command == 'to-json':
            # Convert PCB to JSON
            input_path = Path(args.pcb)
            if not input_path.exists():
                print(f"Error: File not found: {input_path}")
                sys.exit(1)
                
            # Default output path - organized by project
            if not args.output:
                # Extract project name from input path or use filename
                if "amplifier_board" in str(input_path):
                    project_name = "amplifier_board"
                else:
                    project_name = input_path.parent.name
                
                output_path = Path("claude/data_store/pcb") / project_name / "complete_project" / f"{input_path.stem}.json"
            else:
                output_path = Path(args.output)
                
            json_data = converter.pcb_to_json(str(input_path), str(output_path))
            print(f"Converted {input_path} to {output_path}")
            
            # Print summary
            computed = json_data.get('computed_info', {})
            print(f"  Layers: {computed.get('layer_count', 0)}")
            print(f"  Footprints: {computed.get('footprint_count', 0)}")
            print(f"  Tracks: {computed.get('track_count', 0)}")
            print(f"  Vias: {computed.get('via_count', 0)}")
            print(f"  Nets: {computed.get('net_count', 0)}")
            
        elif args.command == 'batch':
            # Convert all PCB files in directory
            input_dir = Path(args.directory)
            if not input_dir.exists():
                print(f"Error: Directory not found: {input_dir}")
                sys.exit(1)
            
            output_base = Path(args.output_dir)
            
            # Find all .kicad_pcb files
            pcb_files = list(input_dir.rglob('*.kicad_pcb'))
            if not pcb_files:
                print(f"No .kicad_pcb files found in {input_dir}")
                return
            
            print(f"Found {len(pcb_files)} PCB files to convert...")
            
            for pcb_file in pcb_files:
                try:
                    # Determine project name from directory structure
                    project_name = pcb_file.parent.name
                    output_path = output_base / project_name / "complete_project" / f"{pcb_file.stem}.json"
                    
                    json_data = converter.pcb_to_json(str(pcb_file), str(output_path))
                    print(f"Converted {pcb_file.name} -> {output_path}")
                    
                except Exception as e:
                    print(f"Error converting {pcb_file}: {e}")
                    continue
            
            print(f"\nBatch conversion complete. Files saved to: {output_base}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()