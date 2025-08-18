# KiCad Schematic Structure for kiutils Parsing

## Core Objects

### Schematic (.kicad_sch)
- **Main container** for all schematic data
- **Accessed via**: `Schematic.from_file(path)`
- **Key attributes**: `schematicSymbols`, `junctions`, `graphicalItems`, `libSymbols`

### Components (schematicSymbols)
- **Type**: List of `SchematicSymbol` objects  
- **Reference**: Extracted from `properties` where `key='Reference'`
- **Value**: Extracted from `properties` where `key='Value'`
- **Position**: `symbol.position.X`, `symbol.position.Y`
- **Library**: `symbol.libraryIdentifier`

### Wire Connectivity
- **Junctions**: Points where multiple wires connect (`schematic.junctions`)
  - Position: `junction.position.X`, `junction.position.Y`
- **Connections**: Individual wire segments (`graphicalItems` of type `Connection`)
  - Points: `connection.points[0]` (start), `connection.points[-1]` (end)
  - Each point has `.X` and `.Y` coordinates
- **Net Building**: Components connect via proximity to wire endpoints/junctions

### Hierarchical Sheets
- **Structure**: Sheets can instantiate multiple times as physical components
- **Connections**: Sheet pins connect to parent via hierarchical labels
- **Instances**: Same sheet used multiple times creates different component instances

## Critical Parsing Notes

### Coordinate System
- **Units**: KiCad uses millimeters (mm) internally
- **Grid**: Components typically snap to 2.54mm (0.1 inch) grid
- **Tolerance**: Use ~5-10mm tolerance when matching component positions to wire endpoints

### Net Connectivity Algorithm
1. **Extract junctions** from `schematic.junctions`
2. **Extract wire segments** from `graphicalItems` (type=`Connection`)
3. **Build wire graph** by connecting wires that share junction points
4. **Group connected wires** into electrical nets using graph traversal
5. **Match components** to nets by position proximity to wire endpoints

### Component Properties Access
```python
def get_component_reference(symbol):
    for prop in symbol.properties:
        if prop.key == 'Reference':
            return prop.value
    return None
```

### Position Matching
```python
def points_match(p1, p2, tolerance=5.0):
    return abs(p1[0] - p2[0]) < tolerance and abs(p1[1] - p2[1]) < tolerance
```

### Wire Connectivity Building
- **Not explicit**: KiCad doesn't store "nets" directly
- **Computed**: Must be derived from wire geometry and junctions
- **Junction-based**: Wires meeting at same junction point are electrically connected
- **Component pins**: Components connect where their position matches wire endpoints

#### Detailed Algorithm for Net Extraction
1. **Extract all wire segments** from `graphicalItems` where `type(item).__name__ == 'Connection'`
2. **Extract all junction positions** from `schematic.junctions`
3. **Build wire connectivity graph**:
   - For each wire, check if start/end points match junction positions
   - Connect wires that share junction points
   - Use graph traversal to group connected wire segments into nets
4. **Match components to nets** by position proximity (tolerance ~10mm)
5. **Post-process special symbols**: Unify ground symbols into single net

#### Net Connectivity Data Structure
```python
{
    'nets': [
        {
            'id': 'net_0',
            'wire_count': int,
            'components': ['component_refs', 'connected_to_this_net'],
            'points': [(x1, y1), (x2, y2), ...]  # Wire endpoint coordinates
        }
    ],
    'junction_count': int,
    'wire_count': int
}
```

## Important kiutils Patterns

### Loading Schematics
```python
from kiutils.schematic import Schematic
schematic = Schematic.from_file('path.kicad_sch')
```

### Extracting Wire Connections
```python
connections = [item for item in schematic.graphicalItems 
               if type(item).__name__ == 'Connection']
```

### Building Junction Map
```python
junction_positions = set()
for junction in schematic.junctions:
    junction_positions.add((junction.position.X, junction.position.Y))
```

### Component Position Access
```python
for symbol in schematic.schematicSymbols:
    if hasattr(symbol, 'position'):
        x, y = symbol.position.X, symbol.position.Y
```

## Common Pitfalls
- **No direct net objects**: Nets must be computed from wire geometry
- **Position precision**: Floating point coordinates need tolerance matching
- **Junction importance**: Critical for determining electrical connectivity
- **Wire segments**: Individual `Connection` objects, not complete nets
- **Component pins**: Not explicitly stored with wire connections
- **Ground symbol handling**: Multiple ground symbols (#GND1, #GND2, #GND3) should be unified into single electrical net

## Advanced Net Processing

### Ground Symbol Unification
KiCad allows multiple ground symbols with different reference designators (#GND1, #GND2, #GND3) but these should be treated as the same electrical net:

```python
def unify_ground_nets(nets):
    """Combine all nets containing ground symbols into unified ground net"""
    ground_components = []
    non_ground_nets = []
    
    for net in nets:
        ground_symbols = [comp for comp in net['components'] if comp.startswith('#GND')]
        if ground_symbols:
            ground_components.extend(net['components'])
        else:
            non_ground_nets.append(net)
    
    if ground_components:
        unified_ground_net = {
            'id': 'net_ground',
            'components': list(set(ground_components)),  # Remove duplicates
            'wire_count': sum(net['wire_count'] for net in nets 
                            if any(comp.startswith('#GND') for comp in net['components']))
        }
        non_ground_nets.append(unified_ground_net)
    
    return non_ground_nets
```

### Graph Visualization Considerations
- **Full mesh connectivity**: Within each net, create edges between all component pairs
- **Ground connectivity**: All ground symbols should connect through unified ground net
- **Physics simulation**: Use global repulsion between all nodes, selective gravity only between connected nodes
- **Overlap prevention**: Calculate minimum distances based on component bounding boxes

#### Physics-Based Layout Integration
For graph visualization libraries (e.g., Cytoscape.js):

```javascript
// General physics parameters for circuit layouts
const physicsConfig = {
    edgeLength: 100-200,     // Desired distance between connected nodes
    repulsion: 500-1000,     // Global repulsion strength (all nodes)
    gravity: 1-10,           // Attraction strength (connected nodes only)
    repulsionRange: 100-300, // Max distance for repulsion effects
    gravityRange: 200-500,   // Max distance for gravity effects
    damping: 0.8-0.9,        // Velocity damping for stability
    speed: 0.5-2.0           // Animation speed multiplier
};

// Overlap prevention based on component bounding boxes
function calculateMinDistance(node1, node2) {
    return Math.max(
        (node1.boundingBox.w + node2.boundingBox.w) * 0.5,
        (node1.boundingBox.h + node2.boundingBox.h) * 0.5
    );
}
```

#### Component Visualization Mapping
Common KiCad component types and suggested visual representations:
- **Passive components** (R, C, L): Rectangles, ellipses, spirals
- **Active components** (Q, U): Triangles, rectangles with multiple pins
- **Connectors**: Pentagons or custom connector shapes
- **Power symbols**: Stars or arrows (+V, -V)
- **Ground symbols**: Inverted triangles or diamonds
- **Test points**: Small circles

## JSON Structure and Parsing

### Complete Schematic JSON Format
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
  "sheets": [...],                // Hierarchical sheets
  "graphicalItems": [...],        // Wires, junctions, shapes
  "labels": [...],                // Local net labels
  "globalLabels": [...],          // Global net labels
  "hierarchicalLabels": [...],    // Sheet interface pins
  "libSymbols": [...],           // Library symbol definitions
  "symbolInstances": [...],      // Component instance data
  "busAliases": [...],           // Bus definitions
  "pageSettings": {...},         // Page size, orientation
  "titleBlock": {...},           // Title, revision, date
  "netConnectivity": {...}       // Computed net information
}
```

### Loading Schematic JSON Data
```python
import json
from pathlib import Path

def load_schematic_data(project_name):
    """Load schematic JSON data for a project"""
    json_path = Path(f"claude/data_store/schematics/{project_name}/complete_project/{project_name}.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        schematic_data = json.load(f)
    
    return schematic_data
```

### Component Analysis from JSON
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
                    # Extract letter prefix (R, C, U, Q, etc.)
                    prefix = ''.join(c for c in reference if c.isalpha())
                    type_counter[prefix] += 1
                break
    
    return dict(type_counter)
```

### Hierarchical Sheet Analysis
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

### Net Connectivity Analysis
```python
def trace_nets(schematic_data):
    """Trace all net connections"""
    nets = {
        'local': [],        # Local labels (sheet-scoped)
        'global': [],       # Global labels (project-wide)
        'hierarchical': [], # Hierarchical pins (sheet interfaces)
        'power': []         # Power symbols
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
        
        # Identify power nets by common naming conventions
        if any(pwr in net_name.upper() for pwr in ['GND', 'VCC', 'VDD', '+', '-', 'POWER']):
            nets['power'].append(net_name)
    
    # Hierarchical labels
    for label in schematic_data.get('hierarchicalLabels', []):
        nets['hierarchical'].append({
            'name': label.get('text', ''),
            'shape': label.get('shape', ''),
            'position': label.get('position', {})
        })
    
    return nets

def analyze_net_connectivity(schematic_data):
    """Analyze computed net connectivity data"""
    net_conn = schematic_data.get('netConnectivity', {})
    if not net_conn:
        return {}
    
    nets = net_conn.get('nets', [])
    
    analysis = {
        'total_nets': len(nets),
        'components_per_net': {},
        'largest_net': None,
        'ground_nets': [],
        'power_nets': []
    }
    
    largest_net_size = 0
    for net in nets:
        net_id = net.get('id', '')
        components = net.get('components', [])
        
        analysis['components_per_net'][net_id] = len(components)
        
        if len(components) > largest_net_size:
            largest_net_size = len(components)
            analysis['largest_net'] = {
                'id': net_id,
                'component_count': len(components),
                'components': components
            }
        
        # Identify special nets
        if any(comp.startswith('#GND') for comp in components):
            analysis['ground_nets'].append(net_id)
        
        if any(comp.startswith('#P+') or comp.startswith('#PWR') for comp in components):
            analysis['power_nets'].append(net_id)
    
    return analysis
```

### Wire Connection Analysis
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
                    'end': (points[-1].get('X'), points[-1].get('Y')),
                    'uuid': item.get('uuid', '')
                })
    
    # Extract junctions from dedicated junction list
    for junction in schematic_data.get('junctions', []):
        position = junction.get('position', {})
        junctions.append({
            'position': (position.get('X', 0), position.get('Y', 0)),
            'diameter': junction.get('diameter', 0)
        })
    
    return connections, junctions
```

### Utility Functions
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
                'position': component.get('position', {}),
                'library': component.get('libraryIdentifier', '')
            })
    
    return matches

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
                    
                    # Extract voltage level using regex
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

def safe_json_access(json_data, path, default=None):
    """Safely access nested JSON data with path like 'netConnectivity.nets.0.components'"""
    try:
        current = json_data
        for key in path.split('.'):
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]
        return current
    except (KeyError, IndexError, TypeError):
        return default
```

## Data Validation and Error Handling

### JSON Structure Validation
```python
def validate_schematic_json(schematic_data):
    """Validate schematic JSON structure and content"""
    errors = []
    warnings = []
    
    # Check required structure
    required_sections = ['metadata', 'schematicSymbols']
    for section in required_sections:
        if section not in schematic_data:
            errors.append(f"Missing '{section}' section")
    
    # Validate components
    components = schematic_data.get('schematicSymbols', [])
    components_without_ref = 0
    components_without_pos = 0
    
    for component in components:
        has_reference = False
        has_position = 'position' in component
        
        for prop in component.get('properties', []):
            if prop.get('key') == 'Reference' and prop.get('value'):
                has_reference = True
                break
        
        if not has_reference:
            components_without_ref += 1
        if not has_position:
            components_without_pos += 1
    
    if components_without_ref > 0:
        warnings.append(f"{components_without_ref} components missing reference designators")
    
    if components_without_pos > 0:
        warnings.append(f"{components_without_pos} components missing position information")
    
    # Check net connectivity if present
    if 'netConnectivity' in schematic_data:
        net_conn = schematic_data['netConnectivity']
        nets = net_conn.get('nets', [])
        
        if len(nets) == 0:
            warnings.append("Net connectivity present but no nets found")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'component_count': len(components)
    }
```

## File Organization
```
claude/data_store/schematics/
├── project_name/
│   ├── complete_project/
│   │   └── ProjectName.json
│   └── project_info.json
└── kicad_schematic_knowledge.md
```

## Best Practices

### Data Access
1. **Always use safe_json_access()** for nested data to avoid KeyError exceptions
2. **Check for computed netConnectivity** before analyzing nets manually
3. **Validate JSON structure** before processing to catch corruption early
4. **Use get() method** with defaults for optional fields

### Analysis Tips
1. **Start with component counting** to understand circuit complexity
2. **Check for hierarchical sheets** - same sheet may be used multiple times
3. **Identify power distribution** early to understand supply architecture  
4. **Cross-reference with PCB data** when available for complete analysis

### Performance Considerations
- **Cache component maps** for repeated analysis
- **Use Counter** for type counting rather than manual loops
- **Process large hierarchies** sheet-by-sheet to manage memory
- **Validate data types** before mathematical operations on positions
