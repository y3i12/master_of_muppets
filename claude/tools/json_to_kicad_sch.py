#!/usr/bin/env python3
"""
JSON to KiCad Schematic Converter

Converts structured JSON format back to KiCad .kicad_sch files.
Reconstructs schematic symbols, wires, junctions, and connectivity.

Requirements:
    pip install kiutils

Usage:
    python json_to_kicad_sch.py <input.json> [output.kicad_sch]
    python json_to_kicad_sch.py --help
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import uuid as uuid_module
from datetime import datetime

try:
    from kiutils.schematic import Schematic
    from kiutils.items.schitems import SchematicSymbol, Junction, Connection, LocalLabel, GlobalLabel, HierarchicalLabel
    from kiutils.items.common import Position, Property
    from kiutils.symbol import SymbolLib, Symbol
except ImportError:
    print("ERROR: kiutils library not found. Install with: pip install kiutils")
    sys.exit(1)


class JsonToKicadSchematicConverter:
    """Converts structured JSON format back to KiCad schematic files."""
    
    def __init__(self):
        """Initialize converter."""
        self.symbol_lib_cache = {}
        self.uuid_map = {}
    
    def generate_uuid(self) -> str:
        """Generate a new UUID for KiCad objects."""
        return str(uuid_module.uuid4())
    
    def safe_get(self, data: Dict, key: str, default: Any = None) -> Any:
        """Safely get value from dictionary."""
        return data.get(key, default)
    
    def create_position(self, pos_data: Dict[str, float]) -> Position:
        """Create Position object from JSON data."""
        x = pos_data.get('x', 0.0)
        y = pos_data.get('y', 0.0)
        angle = pos_data.get('angle', 0.0)
        
        position = Position()
        position.X = x
        position.Y = y
        position.angle = angle
        return position
    
    def create_property(self, key: str, value: str, id_num: int = 0) -> Property:
        """Create Property object."""
        prop = Property()
        prop.key = key
        prop.value = value
        prop.id = id_num
        return prop
    
    def create_schematic_symbol(self, symbol_data: Dict[str, Any]) -> SchematicSymbol:
        """Create SchematicSymbol from JSON data."""
        symbol = SchematicSymbol()
        
        # Set library identifier
        library = self.safe_get(symbol_data, 'library', 'Device:R')
        symbol.libraryIdentifier = library
        
        # Set position
        pos_data = self.safe_get(symbol_data, 'position', {})
        symbol.position = self.create_position(pos_data)
        
        # Set UUID
        symbol_uuid = self.safe_get(symbol_data, 'uuid', '')
        if not symbol_uuid:
            symbol_uuid = self.generate_uuid()
        symbol.uuid = symbol_uuid
        
        # Create properties
        symbol.properties = []
        
        # Standard properties
        reference = self.safe_get(symbol_data, 'reference', 'R?')
        value = self.safe_get(symbol_data, 'value', '1k')
        footprint = self.safe_get(symbol_data, 'footprint', '')
        
        symbol.properties.append(self.create_property('Reference', reference, 0))
        symbol.properties.append(self.create_property('Value', value, 1))
        
        if footprint:
            symbol.properties.append(self.create_property('Footprint', footprint, 2))
        
        # Additional properties from all_properties
        all_props = self.safe_get(symbol_data, 'all_properties', {})
        prop_id = 3
        for key, val in all_props.items():
            if key not in ['Reference', 'Value', 'Footprint']:
                symbol.properties.append(self.create_property(key, str(val), prop_id))
                prop_id += 1
        
        return symbol
    
    def create_junction(self, junction_data: Dict[str, Any]) -> Junction:
        """Create Junction from JSON data."""
        junction = Junction()
        
        # Set position
        pos_data = self.safe_get(junction_data, 'position', {})
        junction.position = self.create_position(pos_data)
        
        # Set diameter (default KiCad junction size)
        junction.diameter = 0.0  # KiCad default
        
        return junction
    
    def create_wire_connection(self, wire_data: Dict[str, Any]) -> Connection:
        """Create Connection (wire) from JSON data."""
        connection = Connection()
        
        # Create points from wire data
        points = []
        
        if 'points' in wire_data and wire_data['points']:
            # Use detailed points if available
            for point_data in wire_data['points']:
                if isinstance(point_data, (list, tuple)) and len(point_data) >= 2:
                    pos = Position()
                    pos.X = float(point_data[0])
                    pos.Y = float(point_data[1])
                    points.append(pos)
                elif isinstance(point_data, dict):
                    pos = Position()
                    pos.X = point_data.get('x', 0.0)
                    pos.Y = point_data.get('y', 0.0)
                    points.append(pos)
        else:
            # Create simple two-point wire from start/end
            start = wire_data.get('start', (0.0, 0.0))
            end = wire_data.get('end', (0.0, 0.0))
            
            start_pos = Position()
            start_pos.X = float(start[0])
            start_pos.Y = float(start[1])
            points.append(start_pos)
            
            end_pos = Position()
            end_pos.X = float(end[0])
            end_pos.Y = float(end[1])
            points.append(end_pos)
        
        connection.points = points
        
        # Set UUID
        wire_uuid = self.safe_get(wire_data, 'uuid', '')
        if not wire_uuid:
            wire_uuid = self.generate_uuid()
        connection.uuid = wire_uuid
        
        return connection
    
    def create_label(self, label_data: Dict[str, Any]) -> Any:
        """Create label object based on type."""
        label_type = self.safe_get(label_data, 'type', 'local')
        text = self.safe_get(label_data, 'text', '')
        
        if label_type == 'global':
            label = GlobalLabel()
        elif label_type == 'hierarchical':
            label = HierarchicalLabel()
        else:
            label = LocalLabel()
        
        label.text = text
        
        # Set position
        pos_data = self.safe_get(label_data, 'position', {})
        label.position = self.create_position(pos_data)
        
        # Set UUID
        label_uuid = self.safe_get(label_data, 'uuid', '')
        if not label_uuid:
            label_uuid = self.generate_uuid()
        label.uuid = label_uuid
        
        return label
    
    def reconstruct_wires_from_nets(self, net_data: Dict[str, Any]) -> List[Connection]:
        """Reconstruct wire segments from net connectivity data."""
        connections = []
        
        nets = self.safe_get(net_data, 'nets', [])
        
        for net in nets:
            points = self.safe_get(net, 'points', [])
            components = self.safe_get(net, 'components', [])
            
            # Skip nets with less than 2 points
            if len(points) < 2:
                continue
            
            # Create mesh connectivity within the net
            # For simplicity, create star topology from first point to all others
            if points:
                center_point = points[0]
                
                for i in range(1, len(points)):
                    other_point = points[i]
                    
                    # Create wire connection
                    wire_data = {
                        'start': (center_point['x'], center_point['y']),
                        'end': (other_point['x'], other_point['y']),
                        'uuid': self.generate_uuid()
                    }
                    
                    connection = self.create_wire_connection(wire_data)
                    connections.append(connection)
        
        return connections
    
    def convert_json_to_schematic(self, json_data: Dict[str, Any]) -> Schematic:
        """Convert JSON data to KiCad Schematic object."""
        
        # Create new schematic
        schematic = Schematic.create_new()
        
        # Set metadata
        metadata = self.safe_get(json_data, 'metadata', {})
        if 'kicad_version' in metadata:
            try:
                schematic.version = int(metadata['kicad_version'])
            except (ValueError, TypeError):
                schematic.version = 20220914  # Default KiCad 6.0 version
        
        if 'generator' in metadata:
            schematic.generator = metadata['generator']
        
        # Set UUID
        if 'uuid' in metadata and metadata['uuid']:
            schematic.uuid = metadata['uuid']
        else:
            schematic.uuid = self.generate_uuid()
        
        # Create schematic symbols (components)
        schematic.schematicSymbols = []
        symbols_data = self.safe_get(json_data, 'schematic_symbols', [])
        
        for symbol_data in symbols_data:
            symbol = self.create_schematic_symbol(symbol_data)
            schematic.schematicSymbols.append(symbol)
        
        # Create junctions
        schematic.junctions = []
        junctions_data = self.safe_get(json_data, 'junctions', [])
        
        for junction_data in junctions_data:
            junction = self.create_junction(junction_data)
            schematic.junctions.append(junction)
        
        # Create wire connections
        if not hasattr(schematic, 'graphicalItems'):
            schematic.graphicalItems = []
        
        # First, try to use existing wire segments
        wire_segments = self.safe_get(json_data, 'wire_segments', [])
        
        for wire_data in wire_segments:
            connection = self.create_wire_connection(wire_data)
            schematic.graphicalItems.append(connection)
        
        # If no wire segments, reconstruct from net connectivity
        if not wire_segments:
            net_connectivity = self.safe_get(json_data, 'net_connectivity', {})
            if net_connectivity:
                reconstructed_wires = self.reconstruct_wires_from_nets(net_connectivity)
                schematic.graphicalItems.extend(reconstructed_wires)
        
        # Create labels
        if not hasattr(schematic, 'labels'):
            schematic.labels = []
        if not hasattr(schematic, 'globalLabels'):
            schematic.globalLabels = []
        if not hasattr(schematic, 'hierarchicalLabels'):
            schematic.hierarchicalLabels = []
        
        labels_data = self.safe_get(json_data, 'labels', [])
        
        for label_data in labels_data:
            label = self.create_label(label_data)
            label_type = self.safe_get(label_data, 'type', 'local')
            
            if label_type == 'global':
                schematic.globalLabels.append(label)
            elif label_type == 'hierarchical':
                schematic.hierarchicalLabels.append(label)
            else:
                schematic.labels.append(label)
        
        # Create library symbols list (simplified)
        if not hasattr(schematic, 'libSymbols'):
            schematic.libSymbols = []
        
        lib_symbols_data = self.safe_get(json_data, 'lib_symbols', [])
        # Note: For full reconstruction, would need to load actual symbol definitions
        # For now, we'll leave this empty as KiCad can resolve symbols from libraries
        
        return schematic
    
    def convert_file(self, input_path: Path, output_path: Path) -> None:
        """Convert JSON file to KiCad schematic file."""
        
        try:
            # Load JSON data
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Convert to schematic
            schematic = self.convert_json_to_schematic(json_data)
            
            # Save schematic file
            schematic.to_file(str(output_path))
            
        except Exception as e:
            raise RuntimeError(f"Failed to convert JSON to schematic: {str(e)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Convert JSON format back to KiCad schematic (.kicad_sch)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python json_to_kicad_sch.py input.json
  python json_to_kicad_sch.py input.json output.kicad_sch
        """
    )
    
    parser.add_argument('input', help='Input JSON file')
    parser.add_argument('output', nargs='?', help='Output KiCad schematic file (.kicad_sch) (optional)')
    parser.add_argument('--validate', action='store_true',
                       help='Validate JSON structure before conversion')
    
    args = parser.parse_args()
    
    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file does not exist: {input_path}")
        sys.exit(1)
    
    if not input_path.suffix.lower() == '.json':
        print(f"WARNING: Input file does not have .json extension: {input_path}")
    
    # Determine output file
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_suffix('.kicad_sch')
    
    try:
        # Validate JSON if requested
        if args.validate:
            print("Validating JSON structure...")
            with open(input_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Basic validation
            required_sections = ['metadata', 'schematic_symbols']
            missing_sections = [section for section in required_sections 
                              if section not in json_data]
            
            if missing_sections:
                print(f"WARNING: Missing sections: {missing_sections}")
            else:
                print("JSON structure validation passed")
        
        # Convert JSON to schematic
        converter = JsonToKicadSchematicConverter()
        converter.convert_file(input_path, output_path)
        
        print(f"Successfully converted: {input_path} -> {output_path}")
        
        # Verify output file was created
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"Output file size: {file_size} bytes")
        else:
            print("WARNING: Output file was not created")
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON format: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()