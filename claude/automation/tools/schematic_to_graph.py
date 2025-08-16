#!/usr/bin/env python3
"""
Convert KiCad Schematic Summary to Hardware Graph Format

Takes the output from kicad_parser.py and converts it to the hardware graph
format used by Claude Code for PCB placement optimization.

This script bridges the gap between raw KiCad data and Claude's analysis format.
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any, List
import re

class SchematicToGraphConverter:
    """Convert parsed schematic data to hardware graph format"""
    
    def __init__(self):
        self.component_type_mapping = {
            'Device:R': {'type': 'resistor', 'fgp': 'passive'},
            'Device:C': {'type': 'capacitor', 'fgp': 'passive'}, 
            'PCM_4ms_Capacitor:C': {'type': 'capacitor', 'fgp': 'passive'},
            'Device:L': {'type': 'inductor', 'fgp': 'passive'},
            'Amplifier_Operational:TL074': {'type': 'opamp', 'fgp': 'analog_amp'},
            'Analog:AD5593R': {'type': 'dac', 'fgp': 'analog_dac'},
            'PCM_4ms_Jack:Jack_3.5mm_WQP-PJ398SM': {'type': 'jack', 'fgp': 'output'},
            'teensy:Teensy4.1': {'type': 'mcu', 'fgp': 'digital_core'},
            'power:GNDREF': {'type': 'power', 'fgp': 'power'},
            'power:+5V': {'type': 'power', 'fgp': 'power'},
            'power:+12V': {'type': 'power', 'fgp': 'power'},
            'power:-12V': {'type': 'power', 'fgp': 'power'},
        }
        
        self.default_metadata = {
            'resistor': {'pxf': 0.5, 'thr': 0.1, 'ncp': 3, 'sgw': 5, 'gnd': 0},
            'capacitor': {'pxf': 0.8, 'thr': 0, 'ncp': 4, 'sgw': 7, 'gnd': 1},
            'opamp': {'pxf': 0.7, 'thr': 0.2, 'ncp': 7, 'sgw': 8, 'gnd': 1},
            'dac': {'pxf': 0.9, 'thr': 0.1, 'ncp': 8, 'sgw': 9, 'gnd': 2},
            'jack': {'pxf': 0.1, 'thr': 0, 'ncp': 1, 'sgw': 5, 'gnd': 0},
            'mcu': {'pxf': 0.8, 'thr': 0.5, 'ncp': 5, 'sgw': 10, 'gnd': 2},
            'power': {'pxf': 0.1, 'thr': 0, 'ncp': 1, 'sgw': 2, 'gnd': 2}
        }
    
    def convert_schematic_summary(self, summary_file: Path, git_revision: str = None) -> Dict[str, Any]:
        """Convert schematic summary to hardware graph format"""
        
        with open(summary_file, 'r', encoding='utf-8') as f:
            schematic_data = json.load(f)
        
        # Initialize hardware graph structure
        hardware_graph = {
            "_metadata": {
                "version": "1.2.0",
                "git_revision": git_revision or "unknown",
                "source": "kicad_parser.py",
                "description": "Component node registry for Master of Muppets PCB",
                "encoding": {
                    "pxf": "proximity_factor (0-1, higher needs closer placement)",
                    "thr": "thermal_coefficient (W dissipation estimate)",
                    "ncp": "noise_criticality_priority (0-10, higher needs better isolation)",
                    "fgp": "functional_group_id",
                    "sgw": "signal_weight (importance of signal integrity)",
                    "gnd": "ground_plane_requirement (0=none, 1=preferred, 2=critical)"
                }
            },
            "nodes": {}
        }
        
        # Process all components from all schematic files
        for sch_name, sch_data in schematic_data.get('schematics', {}).items():
            components = sch_data.get('components', [])
            
            for comp in components:
                node = self._convert_component(comp, sch_name)
                if node:
                    ref = comp['reference']
                    hardware_graph['nodes'][ref] = node
        
        return hardware_graph
    
    def _convert_component(self, comp: Dict[str, Any], sheet_name: str) -> Dict[str, Any]:
        """Convert a single component to hardware graph node"""
        
        ref = comp['reference']
        lib_id = comp['lib_id']
        value = comp['value']
        footprint = comp['footprint']
        
        # Skip power symbols (they're not physical components)
        if ref.startswith('#PWR'):
            return None
        
        # Determine component type and functional group
        type_info = self.component_type_mapping.get(lib_id, {'type': 'unknown', 'fgp': 'misc'})
        comp_type = type_info['type']
        fgp = type_info['fgp']
        
        # Get default metadata for this component type
        metadata = self.default_metadata.get(comp_type, {
            'pxf': 0.5, 'thr': 0, 'ncp': 3, 'sgw': 5, 'gnd': 0
        }).copy()
        
        # Add component-specific metadata
        metadata.update({
            'sheet': sheet_name,
            'lib_id': lib_id,
            'fgp': fgp
        })
        
        # Special handling for specific components
        if 'AD5593R' in lib_id:
            metadata.update({
                'channels': 8,
                'resolution': 12,
                'i2c_device': True
            })
        elif 'TL074' in lib_id:
            metadata.update({
                'channels': 4,
                'supply_dual': True
            })
        elif 'Teensy' in lib_id:
            metadata.update({
                'i2c_master': True,
                'critical_placement': True
            })
        elif 'Jack' in lib_id:
            # Extract channel number from reference if possible
            channel_match = re.search(r'J(\d+)', ref)
            if channel_match:
                metadata['channel'] = int(channel_match.group(1))
        
        # Determine module assignment based on sheet
        module = 'main'
        if 'dac_module' in sheet_name:
            module = 'dac'
        elif 'amp_module' in sheet_name:
            module = 'amp'
        elif 'teensy_module' in sheet_name:
            module = 'teensy'
        elif 'jack_sheet' in sheet_name:
            module = 'jack'
        elif 'unripple_module' in sheet_name:
            module = 'power'
        
        node = {
            'type': comp_type,
            'value': value,
            'module': module,
            'footprint': footprint,
            'metadata': metadata
        }
        
        # Add position if available
        if comp.get('position'):
            node['position'] = {
                'x': comp['position'][0],
                'y': comp['position'][1],
                'rotation': comp.get('rotation', 0.0)
            }
        
        return node
    
    def generate_networks(self, hardware_graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate network connections based on component analysis"""
        
        networks = {
            "_metadata": {
                "version": "1.2.0",
                "description": "Multi-layer network representations for PCB placement optimization",
                "edge_weights": {
                    "prx": "proximity_requirement (0-10, higher requires closer placement)",
                    "sig": "signal_integrity_criticality (0-10)",
                    "cur": "current_capacity (mA)",
                    "frq": "frequency_content (0=DC, 1=low, 2=high)",
                    "len": "max_trace_length_mm"
                }
            },
            "networks": {
                "proximity_network": {
                    "description": "Components that should be physically close for optimal performance",
                    "clusters": []
                }
            }
        }
        
        # Analyze components to create clusters
        nodes = hardware_graph.get('nodes', {})
        
        # I2C cluster - all I2C devices should be close
        i2c_components = []
        dac_components = []
        mcu_components = []
        
        for ref, node in nodes.items():
            metadata = node.get('metadata', {})
            if metadata.get('i2c_device') or metadata.get('i2c_master'):
                i2c_components.append(ref)
            if node.get('type') == 'dac':
                dac_components.append(ref)
            if node.get('type') == 'mcu':
                mcu_components.append(ref)
        
        if i2c_components:
            networks["networks"]["proximity_network"]["clusters"].append({
                "id": "i2c_bus",
                "members": i2c_components,
                "max_diameter_mm": 50,
                "reason": "I2C signal integrity and timing"
            })
        
        # Amplifier clusters - each amp with its feedback resistors
        amp_clusters = self._find_amplifier_clusters(nodes)
        networks["networks"]["proximity_network"]["clusters"].extend(amp_clusters)
        
        return networks
    
    def _find_amplifier_clusters(self, nodes: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find amplifier components and their associated resistors"""
        clusters = []
        
        # Find all operational amplifiers
        amps = [ref for ref, node in nodes.items() if node.get('type') == 'opamp']
        
        for amp_ref in amps:
            # Find nearby resistors (simplified - in real implementation would use netlist)
            nearby_resistors = []
            for ref, node in nodes.items():
                if (node.get('type') == 'resistor' and 
                    node.get('module') == nodes[amp_ref].get('module')):
                    nearby_resistors.append(ref)
            
            if nearby_resistors:
                clusters.append({
                    "id": f"amp_cluster_{amp_ref}",
                    "members": [amp_ref] + nearby_resistors[:4],  # Limit to 4 resistors per amp
                    "max_diameter_mm": 15,
                    "reason": f"Operational amplifier {amp_ref} feedback network"
                })
        
        return clusters

def main():
    parser = argparse.ArgumentParser(description='Convert KiCad schematic summary to hardware graph')
    parser.add_argument('summary_file', type=Path, help='Path to schematic_summary.json')
    parser.add_argument('-o', '--output-dir', type=Path, help='Output directory (default: claude/hardware_graph)')
    parser.add_argument('-g', '--git-revision', type=str, help='Git revision to include in metadata')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if not args.summary_file.exists():
        print(f"Error: Summary file {args.summary_file} does not exist")
        return 1
    
    output_dir = args.output_dir or Path('claude/hardware_graph')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    converter = SchematicToGraphConverter()
    
    # Convert schematic summary to hardware graph
    if args.verbose:
        print(f"Converting {args.summary_file}...")
    
    hardware_graph = converter.convert_schematic_summary(args.summary_file, args.git_revision)
    
    # Generate networks
    networks = converter.generate_networks(hardware_graph)
    
    # Save outputs
    node_registry_file = output_dir / 'node_registry_auto.json'
    networks_file = output_dir / 'networks_auto.json'
    
    with open(node_registry_file, 'w', encoding='utf-8') as f:
        json.dump(hardware_graph, f, indent=2, ensure_ascii=False)
    
    with open(networks_file, 'w', encoding='utf-8') as f:
        json.dump(networks, f, indent=2, ensure_ascii=False)
    
    if args.verbose:
        print(f"Generated {len(hardware_graph['nodes'])} component nodes")
        print(f"Hardware graph saved to {node_registry_file}")
        print(f"Networks saved to {networks_file}")
    
    print(f"Conversion complete! Files saved to {output_dir}")
    return 0

if __name__ == '__main__':
    exit(main())