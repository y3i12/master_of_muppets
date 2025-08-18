# Claude's KiCad Schematic Analysis Guide

## Multi-Project Schematic Data Store

This directory contains complete JSON representations of multiple KiCad projects. All data has been preserved from the original KiCad files to enable full analysis without external context.

## Directory Structure

```
claude/data_store/schematics/
├── CLAUDE_SCHEMATIC_GUIDE.md           # This universal instruction file
├── README.md                           # Overview of all projects
├── master_of_muppets/                  # Project: USB MIDI to 16ch CV converter
│   ├── project_info.json              # Project metadata
│   ├── complete_project/               # Full JSON schematics
│   │   ├── MasterOfMuppets.json       # Root schematic
│   │   ├── dac_module.json            # DAC modules
│   │   └── ...                        # Other sheets
│   ├── analysis/                       # Project-specific analysis
│   └── README.md                       # Project documentation
├── amplifier_board/                    # Project: Audio/CV amplifier
│   ├── project_info.json              # Project metadata
│   ├── complete_project/               # Full JSON schematics
│   │   └── AmpBoard.json              # Single-sheet design
│   ├── analysis/                       # Analysis tools
│   └── README.md                       # Project documentation
└── [future_projects]/                  # Additional projects follow same structure
```

## How to Work with Any Project

### 1. Discover Available Projects

```python
import os
import json
from pathlib import Path

# List all available projects
def list_projects():
    base_path = Path('claude/data_store/schematics')
    projects = []
    
    for item in base_path.iterdir():
        if item.is_dir() and item.name not in ['__pycache__']:
            info_file = item / 'project_info.json'
            if info_file.exists():
                with open(info_file, 'r') as f:
                    info = json.load(f)
                    projects.append({
                        'name': item.name,
                        'description': info.get('description', ''),
                        'root_schematic': info.get('root_schematic', '')
                    })
    
    return projects

# Example usage
for project in list_projects():
    print(f"Project: {project['name']}")
    print(f"  Description: {project['description']}")
    print(f"  Root file: {project['root_schematic']}")
```

### 2. Load and Analyze Any Project

```python
def load_project(project_name):
    """Load a project's root schematic and metadata"""
    project_path = Path(f'claude/data_store/schematics/{project_name}')
    
    # Load project info
    with open(project_path / 'project_info.json', 'r') as f:
        project_info = json.load(f)
    
    # Load root schematic
    root_file = project_info.get('root_schematic', 'root.json')
    with open(project_path / 'complete_project' / root_file, 'r') as f:
        schematic = json.load(f)
    
    return project_info, schematic

# Example: Load master_of_muppets
info, schematic = load_project('master_of_muppets')
print(f"Loaded: {info['project_name']}")
print(f"Components: {len(schematic.get('schematicSymbols', []))}")
```

## Understanding the JSON Structure

Every converted KiCad schematic follows this structure:

```json
{
  "metadata": {
    "converter_version": "1.0.0",
    "source_file": "path/to/original.kicad_sch",
    "kicad_version": 20240101,
    "generator": "eeschema"
  },
  "schematicSymbols": [...],      // Components
  "sheets": [...],                 // Hierarchical sheets
  "graphicalItems": [...],         // Wires, junctions, shapes
  "labels": [...],                 // Local net labels
  "globalLabels": [...],           // Global net labels
  "hierarchicalLabels": [...],     // Sheet interface pins
  "libSymbols": [...],            // Library symbol definitions
  "symbolInstances": [...],       // Component instance data
  "busAliases": [...],            // Bus definitions
  "pageSettings": {...},          // Page size, orientation
  "titleBlock": {...}             // Title, revision, date
}
```

## Key Data Access Patterns

### Components (schematicSymbols)

```python
def analyze_components(schematic_data):
    """Extract and categorize all components"""
    components = schematic_data.get('schematicSymbols', [])
    
    component_map = {}
    for component in components:
        # Extract properties
        reference = ""
        value = ""
        footprint = ""
        
        for prop in component.get('properties', []):
            key = prop.get('key', '')
            val = prop.get('value', '')
            
            if key == 'Reference':
                reference = val
            elif key == 'Value':
                value = val
            elif key == 'Footprint':
                footprint = val
        
        if reference:
            component_map[reference] = {
                'value': value,
                'footprint': footprint,
                'library': component.get('libraryIdentifier', ''),
                'position': component.get('position', {}),
                'uuid': component.get('uuid', '')
            }
    
    return component_map
```

### Hierarchical Sheets

```python
def get_sheet_hierarchy(schematic_data):
    """Extract hierarchical sheet structure"""
    sheets = schematic_data.get('sheets', [])
    
    sheet_tree = []
    for sheet in sheets:
        sheet_info = {
            'name': '',
            'file': '',
            'instances': []
        }
        
        # Extract sheet properties
        if 'sheetName' in sheet:
            sheet_info['name'] = sheet['sheetName'].get('value', '')
        if 'fileName' in sheet:
            sheet_info['file'] = sheet['fileName'].get('value', '')
        
        # Sheet instances (multiple uses of same sheet)
        instances = sheet.get('instances', [])
        for instance in instances:
            sheet_info['instances'].append({
                'path': instance.get('path', ''),
                'page': instance.get('page', '')
            })
        
        sheet_tree.append(sheet_info)
    
    return sheet_tree
```

### Net Connectivity

```python
def trace_nets(schematic_data):
    """Trace all net connections"""
    nets = {
        'local': [],      # Local labels (sheet-scoped)
        'global': [],     # Global labels (project-wide)
        'hierarchical': [], # Hierarchical pins (sheet interfaces)
        'power': []       # Power symbols
    }
    
    # Local labels
    for label in schematic_data.get('labels', []):
        nets['local'].append({
            'name': label.get('text', ''),
            'position': label.get('position', {})
        })
    
    # Global labels
    for label in schematic_data.get('globalLabels', []):
        net_name = label.get('text', '')
        nets['global'].append({
            'name': net_name,
            'position': label.get('position', {})
        })
        
        # Identify power nets
        if any(pwr in net_name for pwr in ['GND', 'VCC', '+12V', '-12V', '+5V', '+3V3']):
            nets['power'].append(net_name)
    
    # Hierarchical labels
    for label in schematic_data.get('hierarchicalLabels', []):
        nets['hierarchical'].append({
            'name': label.get('text', ''),
            'shape': label.get('shape', ''),
            'position': label.get('position', {})
        })
    
    return nets
```

### Wire Connections

```python
def get_connections(schematic_data):
    """Extract wire connections and junctions"""
    connections = []
    junctions = []
    
    for item in schematic_data.get('graphicalItems', []):
        item_type = item.get('_type', '')
        
        if item_type == 'Connection':
            # Wire segment
            points = item.get('points', [])
            if len(points) >= 2:
                connections.append({
                    'start': (points[0].get('X'), points[0].get('Y')),
                    'end': (points[1].get('X'), points[1].get('Y'))
                })
        
        elif item_type == 'Junction':
            # Wire junction point
            position = item.get('position', {})
            junctions.append((position.get('X'), position.get('Y')))
    
    return connections, junctions
```

## Project-Specific Analysis

### Master of Muppets (16-channel CV converter)

```python
# Expected components for Master of Muppets
def validate_master_of_muppets():
    info, root = load_project('master_of_muppets')
    
    # Load all sheets for complete analysis
    all_components = []
    sheets_to_check = ['dac_module', 'amp_module', 'teensy_module', 'jack_sheet']
    
    for sheet_name in sheets_to_check:
        sheet_path = f'master_of_muppets/complete_project/{sheet_name}.json'
        with open(sheet_path, 'r') as f:
            sheet_data = json.load(f)
            all_components.extend(sheet_data.get('schematicSymbols', []))
    
    # Validate expectations
    validations = {
        'DAC ICs': any('AD5593' in c.get('libraryIdentifier', '') for c in all_components),
        'Teensy 4.1': any('Teensy' in c.get('libraryIdentifier', '') for c in all_components),
        '16 CV outputs': len([c for c in all_components if 'Jack' in str(c)]) >= 16,
        'Power distribution': any('power' in c.get('libraryIdentifier', '').lower() for c in all_components)
    }
    
    return validations
```

### Amplifier Board (audio/CV amplifier)

```python
# Analyze amplifier board
def analyze_amplifier_board():
    info, schematic = load_project('amplifier_board')
    
    components = analyze_components(schematic)
    
    # Find key components
    op_amps = [ref for ref, comp in components.items() if ref.startswith('U')]
    transistors = [ref for ref, comp in components.items() if ref.startswith('Q')]
    resistors = [ref for ref in components.keys() if ref.startswith('R')]
    capacitors = [ref for ref in components.keys() if ref.startswith('C')]
    
    return {
        'op_amps': op_amps,
        'transistors': transistors,
        'resistor_count': len(resistors),
        'capacitor_count': len(capacitors),
        'total_components': len(components)
    }
```

## Common Analysis Tasks

### 1. Component Count by Type

```python
def count_components_by_type(schematic_data):
    """Count components grouped by reference prefix"""
    from collections import Counter
    
    components = schematic_data.get('schematicSymbols', [])
    type_counter = Counter()
    
    for component in components:
        for prop in component.get('properties', []):
            if prop.get('key') == 'Reference':
                reference = prop.get('value', '')
                if reference:
                    # Extract letter prefix
                    prefix = ''.join(c for c in reference if c.isalpha())
                    type_counter[prefix] += 1
                break
    
    return dict(type_counter)
```

### 2. Find Specific Component Values

```python
def find_components_by_value(schematic_data, search_value):
    """Find all components with a specific value"""
    matches = []
    components = schematic_data.get('schematicSymbols', [])
    
    for component in components:
        reference = ""
        value = ""
        
        for prop in component.get('properties', []):
            if prop.get('key') == 'Reference':
                reference = prop.get('value', '')
            elif prop.get('key') == 'Value':
                value = prop.get('value', '')
        
        if search_value.lower() in value.lower():
            matches.append({
                'reference': reference,
                'value': value,
                'position': component.get('position', {})
            })
    
    return matches
```

### 3. Power Analysis

```python
def analyze_power_distribution(schematic_data):
    """Analyze power distribution in the schematic"""
    power_info = {
        'power_symbols': [],
        'power_nets': [],
        'voltage_levels': set()
    }
    
    # Find power symbols
    components = schematic_data.get('schematicSymbols', [])
    for component in components:
        lib_id = component.get('libraryIdentifier', '')
        if 'power' in lib_id.lower():
            for prop in component.get('properties', []):
                if prop.get('key') == 'Value':
                    power_value = prop.get('value', '')
                    power_info['power_symbols'].append(power_value)
                    
                    # Extract voltage level
                    import re
                    voltage_match = re.search(r'([+-]?\d+\.?\d*)[Vv]', power_value)
                    if voltage_match:
                        power_info['voltage_levels'].add(voltage_match.group(1) + 'V')
    
    # Find power-related global labels
    for label in schematic_data.get('globalLabels', []):
        label_text = label.get('text', '')
        if any(pwr in label_text.upper() for pwr in ['VCC', 'VDD', 'GND', '+', '-']):
            power_info['power_nets'].append(label_text)
    
    power_info['voltage_levels'] = list(power_info['voltage_levels'])
    return power_info
```

## Tips for Effective Analysis

1. **Always Start with project_info.json**: Contains metadata about the project
2. **Use Root Schematic First**: Understand the hierarchy before diving into details
3. **Check Sheet Instances**: Same sheet may be used multiple times (e.g., 16 identical channels)
4. **Validate Data Types**: All positions are dictionaries with X, Y keys
5. **Handle Missing Data**: Use `.get()` method with defaults for optional fields
6. **Cross-Reference Sheets**: Components may connect across sheet boundaries via hierarchical labels

## Troubleshooting

### If Components Seem Missing
- Check all sheets, not just the root
- Look for hierarchical instantiation (same sheet used multiple times)
- Some components may be in libSymbols as definitions

### If Connections Don't Make Sense
- Remember local labels are sheet-scoped
- Global labels connect across all sheets
- Hierarchical labels connect parent-child sheets
- Power symbols are implicitly connected by name

### If Analysis Results Differ from Expectations
- Verify you're loading all relevant sheets
- Check for multiple instances of the same sheet
- Consider that some "components" might be power symbols or mounting holes

## Summary

This guide provides everything needed to parse and analyze KiCad schematics converted to JSON format. The data is complete and self-contained - no external context or libraries are required. Each project follows the same structure, making it easy to write reusable analysis code that works across all projects.