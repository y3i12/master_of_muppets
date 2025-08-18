# KiCad PCB Structure for kiutils Parsing

## Core Objects

### Board (.kicad_pcb)
- **Main container** for all PCB data
- **Accessed via**: `Board.from_file(path)`
- **Key attributes**: `footprints`, `tracks`, `vias`, `nets`, `layers`, `zones`

### Footprints (Components)
- **Type**: List of `Footprint` objects
- **Reference**: Extracted from `properties` where `key='Reference'`
- **Position**: `footprint.position.X`, `footprint.position.Y`
- **Rotation**: `footprint.position.angle`
- **Library**: `footprint.libraryReference` and `footprint.entryName`
- **Side**: Determined by layer placement

### Layers
- **Stack definition**: Physical layer stackup
- **Types**: Signal, power, ground, mechanical, silkscreen, etc.
- **Properties**: `ordinal`, `canonicalName`, `type`, `userName`
- **Access**: `board.layers`

### Nets
- **Electrical connectivity**: Named electrical nets
- **Properties**: `number` (unique ID), `name` (user-defined)
- **Usage**: Referenced by tracks, vias, and pads

### Tracks and Vias
- **Tracks**: Copper routing between components
- **Vias**: Layer-to-layer connections
- **Properties**: width, layer, net assignment
- **Connectivity**: Link footprint pads through nets

## Critical Parsing Notes

### Coordinate System
- **Units**: KiCad uses millimeters (mm) internally
- **Origin**: Bottom-left corner of board outline
- **Y-axis**: Increases upward (opposite to screen coordinates)

### Footprint Analysis
```python
def analyze_footprints(board):
    footprint_data = []
    for footprint in board.footprints:
        # Extract reference designator
        ref = ''
        if hasattr(footprint, 'properties'):
            for prop in footprint.properties:
                if prop.key == 'Reference':
                    ref = prop.value
                    break
        
        # Get library information
        lib_ref = getattr(footprint, 'libraryReference', None)
        entry_name = getattr(footprint, 'entryName', None)
        
        # Position and rotation
        pos = footprint.position
        
        footprint_data.append({
            'reference': ref,
            'library': f"{lib_ref}:{entry_name}" if lib_ref else entry_name,
            'x': pos.X,
            'y': pos.Y,
            'rotation': getattr(pos, 'angle', 0)
        })
    
    return footprint_data
```

### Layer Stack Analysis
```python
def analyze_layers(board):
    layers = []
    for layer in board.layers:
        layers.append({
            'ordinal': layer.ordinal,
            'name': layer.canonicalName,
            'type': layer.type,
            'user_name': layer.userName
        })
    return sorted(layers, key=lambda x: x['ordinal'])
```

### Net Connectivity
```python
def analyze_nets(board):
    nets = []
    for net in board.nets:
        nets.append({
            'number': net.number,
            'name': net.name,
            'track_count': sum(1 for track in board.tracks if track.net == net.number),
            'via_count': sum(1 for via in board.vias if via.net == net.number)
        })
    return nets
```

## PCB Data Structure

### Complete PCB JSON Format
```python
{
    'metadata': {
        'converter_version': str,
        'source_file': str,
        'kicad_version': int,
        'generator': str
    },
    'computed_info': {
        'layer_count': int,
        'footprint_count': int,
        'track_count': int,
        'via_count': int,
        'net_count': int,
        'footprint_types': {
            'library:footprint_name': count
        },
        'footprint_positions': [
            {
                'reference': str,
                'library_reference': str,
                'entry_name': str,
                'x': float,
                'y': float,
                'rotation': float,
                'side': str
            }
        ],
        'component_references': [sorted_list_of_refs],
        'nets': [
            {
                'number': int,
                'name': str
            }
        ],
        'layers': [
            {
                'ordinal': int,
                'canonical_name': str,
                'type': str,
                'user_name': str
            }
        ]
    }
}
```

## JSON Parsing Patterns

### Loading PCB JSON Data
```python
import json
from pathlib import Path

def load_pcb_data(project_name):
    """Load PCB JSON data for a project"""
    json_path = Path(f"claude/data_store/pcb/{project_name}/complete_project/{project_name}.json")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        pcb_data = json.load(f)
    
    return pcb_data
```

### Extracting Component Information
```python
def get_component_positions(pcb_data):
    """Extract all component positions and references"""
    computed_info = pcb_data.get('computed_info', {})
    positions = computed_info.get('footprint_positions', [])
    
    components = []
    for pos in positions:
        if pos['reference']:  # Skip components without references
            components.append({
                'ref': pos['reference'],
                'x': pos['x'],
                'y': pos['y'], 
                'rotation': pos['rotation'],
                'footprint': pos['entry_name'],
                'library': pos['library_reference']
            })
    
    return sorted(components, key=lambda x: x['ref'])

def get_component_types(pcb_data):
    """Get footprint type distribution"""
    computed_info = pcb_data.get('computed_info', {})
    return computed_info.get('footprint_types', {})
```

### Net Analysis from JSON
```python
def analyze_pcb_nets(pcb_data):
    """Analyze net information from PCB JSON"""
    computed_info = pcb_data.get('computed_info', {})
    nets = computed_info.get('nets', [])
    
    net_analysis = {
        'total_nets': len(nets),
        'named_nets': [net for net in nets if net['name']],
        'unnamed_nets': [net for net in nets if not net['name']],
        'power_nets': [net for net in nets if any(keyword in net['name'].upper() 
                      for keyword in ['VCC', 'VDD', 'GND', '+', '-']) if net['name']],
        'signal_nets': []
    }
    
    # Signal nets are named nets that aren't power nets
    net_analysis['signal_nets'] = [net for net in net_analysis['named_nets'] 
                                  if net not in net_analysis['power_nets']]
    
    return net_analysis
```

### Layer Stack Analysis
```python
def get_layer_stack(pcb_data):
    """Extract and organize layer stack information"""
    computed_info = pcb_data.get('computed_info', {})
    layers = computed_info.get('layers', [])
    
    # Organize layers by type
    layer_stack = {
        'signal_layers': [],
        'plane_layers': [],
        'mechanical_layers': [],
        'other_layers': []
    }
    
    for layer in layers:
        layer_info = {
            'ordinal': layer['ordinal'],
            'name': layer['canonical_name'],
            'type': layer['type'],
            'user_name': layer['user_name']
        }
        
        if layer['type'] == 'signal':
            layer_stack['signal_layers'].append(layer_info)
        elif layer['type'] in ['power', 'mixed']:
            layer_stack['plane_layers'].append(layer_info)
        elif 'mechanical' in layer['canonical_name'].lower():
            layer_stack['mechanical_layers'].append(layer_info)
        else:
            layer_stack['other_layers'].append(layer_info)
    
    return layer_stack
```

### Board Statistics
```python
def get_pcb_statistics(pcb_data):
    """Generate comprehensive PCB statistics"""
    computed_info = pcb_data.get('computed_info', {})
    
    stats = {
        'overview': {
            'total_components': computed_info.get('footprint_count', 0),
            'total_nets': computed_info.get('net_count', 0),
            'layer_count': computed_info.get('layer_count', 0),
            'track_count': computed_info.get('track_count', 0),
            'via_count': computed_info.get('via_count', 0)
        },
        'component_breakdown': computed_info.get('footprint_types', {}),
        'references': computed_info.get('component_references', [])
    }
    
    # Component type analysis
    total_components = sum(stats['component_breakdown'].values())
    stats['type_percentages'] = {
        footprint: (count / total_components * 100) 
        for footprint, count in stats['component_breakdown'].items()
    }
    
    return stats
```

### Cross-Reference with Schematic Data
```python
def cross_reference_sch_pcb(schematic_data, pcb_data):
    """Cross-reference schematic and PCB component data"""
    
    # Get component references from both
    sch_components = set()
    if 'netConnectivity' in schematic_data:
        for net in schematic_data['netConnectivity']['nets']:
            for comp in net['components']:
                if not comp.startswith('#'):  # Skip power symbols
                    sch_components.add(comp)
    
    pcb_components = set(pcb_data['computed_info'].get('component_references', []))
    
    analysis = {
        'schematic_only': sch_components - pcb_components,
        'pcb_only': pcb_components - sch_components, 
        'common_components': sch_components & pcb_components,
        'match_percentage': len(sch_components & pcb_components) / max(len(sch_components), 1) * 100
    }
    
    return analysis
```

### Visualization Data Preparation
```python
def prepare_visualization_data(pcb_data):
    """Prepare data for PCB visualization tools"""
    computed_info = pcb_data.get('computed_info', {})
    positions = computed_info.get('footprint_positions', [])
    
    # Convert to visualization format (e.g., for D3.js, Three.js, etc.)
    viz_data = {
        'nodes': [],
        'board_bounds': {'min_x': 0, 'max_x': 0, 'min_y': 0, 'max_y': 0}
    }
    
    if positions:
        x_coords = [pos['x'] for pos in positions if pos['reference']]
        y_coords = [pos['y'] for pos in positions if pos['reference']]
        
        viz_data['board_bounds'] = {
            'min_x': min(x_coords) if x_coords else 0,
            'max_x': max(x_coords) if x_coords else 0,
            'min_y': min(y_coords) if y_coords else 0,
            'max_y': max(y_coords) if y_coords else 0
        }
        
        for pos in positions:
            if pos['reference']:
                viz_data['nodes'].append({
                    'id': pos['reference'],
                    'x': pos['x'],
                    'y': pos['y'],
                    'rotation': pos['rotation'],
                    'type': pos['entry_name'],
                    'library': pos['library_reference']
                })
    
    return viz_data
```

### Footprint Size and Pin Extraction
```python
def extract_footprint_dimensions(pcb_data):
    """Extract physical dimensions and pin layouts from footprints"""
    footprint_info = []
    
    for footprint in pcb_data.get('footprints', []):
        fp_info = {
            'entry_name': footprint.get('entryName', ''),
            'description': footprint.get('description', ''),
            'pads': [],
            'dimensions': {'width': 0, 'height': 0},
            'courtyard': None
        }
        
        # Extract pad information
        for pad in footprint.get('pads', []):
            pad_info = {
                'number': pad.get('number', ''),
                'type': pad.get('type', ''),
                'shape': pad.get('shape', ''),
                'position': {
                    'x': pad.get('position', {}).get('X', 0),
                    'y': pad.get('position', {}).get('Y', 0)
                },
                'size': {
                    'width': pad.get('size', {}).get('X', 0) if pad.get('size') else 0,
                    'height': pad.get('size', {}).get('Y', 0) if pad.get('size') else 0
                },
                'drill': {
                    'diameter': pad.get('drill', {}).get('diameter', 0) if pad.get('drill') else 0,
                    'oval': pad.get('drill', {}).get('oval', False) if pad.get('drill') else False
                },
                'layers': pad.get('layers', []),
                'net': {
                    'name': pad.get('net', {}).get('name', '') if pad.get('net') else '',
                    'number': pad.get('net', {}).get('number', 0) if pad.get('net') else 0
                }
            }
            fp_info['pads'].append(pad_info)
        
        # Calculate footprint dimensions from pad positions
        if fp_info['pads']:
            x_positions = [pad['position']['x'] for pad in fp_info['pads']]
            y_positions = [pad['position']['y'] for pad in fp_info['pads']]
            pad_sizes_x = [pad['size']['width'] for pad in fp_info['pads']]
            pad_sizes_y = [pad['size']['height'] for pad in fp_info['pads']]
            
            # Approximate footprint size based on pad spread
            min_x = min(x_positions) - max(pad_sizes_x) / 2
            max_x = max(x_positions) + max(pad_sizes_x) / 2
            min_y = min(y_positions) - max(pad_sizes_y) / 2
            max_y = max(y_positions) + max(pad_sizes_y) / 2
            
            fp_info['dimensions'] = {
                'width': max_x - min_x,
                'height': max_y - min_y,
                'bounds': {'min_x': min_x, 'max_x': max_x, 'min_y': min_y, 'max_y': max_y}
            }
        
        # Look for courtyard information in graphicItems
        courtyard_items = []
        for item in footprint.get('graphicItems', []):
            if item.get('layer', '').endswith('.CrtYd'):
                courtyard_items.append(item)
        
        if courtyard_items:
            fp_info['courtyard'] = len(courtyard_items)
        
        footprint_info.append(fp_info)
    
    return footprint_info

def get_component_pin_mapping(pcb_data):
    """Create mapping of components to their pin layouts"""
    pin_mapping = {}
    
    computed_info = pcb_data.get('computed_info', {})
    positions = computed_info.get('footprint_positions', [])
    
    # Create position lookup
    position_lookup = {pos['reference']: pos for pos in positions if pos.get('reference')}
    
    for footprint in pcb_data.get('footprints', []):
        # Find corresponding component reference
        component_ref = None
        for prop in footprint.get('properties', []):
            if prop.get('key') == 'Reference':
                component_ref = prop.get('value', '')
                break
        
        if not component_ref:
            continue
            
        # Get component position from computed info
        comp_position = position_lookup.get(component_ref, {})
        comp_x = comp_position.get('x', 0)
        comp_y = comp_position.get('y', 0)
        
        pin_info = {
            'reference': component_ref,
            'footprint_type': footprint.get('entryName', ''),
            'position': {'x': comp_x, 'y': comp_y},
            'pins': []
        }
        
        for pad in footprint.get('pads', []):
            pin_data = {
                'pin_number': pad.get('number', ''),
                'pin_type': pad.get('type', ''),
                'relative_position': {
                    'x': pad.get('position', {}).get('X', 0),
                    'y': pad.get('position', {}).get('Y', 0)
                },
                'absolute_position': {
                    'x': comp_x + pad.get('position', {}).get('X', 0),
                    'y': comp_y + pad.get('position', {}).get('Y', 0)
                },
                'size': {
                    'width': pad.get('size', {}).get('X', 0) if pad.get('size') else 0,
                    'height': pad.get('size', {}).get('Y', 0) if pad.get('size') else 0
                },
                'shape': pad.get('shape', ''),
                'drill_size': pad.get('drill', {}).get('diameter', 0) if pad.get('drill') else 0,
                'net_name': pad.get('net', {}).get('name', '') if pad.get('net') else '',
                'net_number': pad.get('net', {}).get('number', 0) if pad.get('net') else 0,
                'layers': pad.get('layers', [])
            }
            pin_info['pins'].append(pin_data)
        
        pin_mapping[component_ref] = pin_info
    
    return pin_mapping

def analyze_footprint_sizes(pcb_data):
    """Analyze footprint sizes and generate statistics"""
    footprint_dims = extract_footprint_dimensions(pcb_data)
    
    size_analysis = {
        'footprint_types': {},
        'size_distribution': [],
        'pin_count_distribution': {},
        'largest_footprints': [],
        'smallest_footprints': []
    }
    
    for fp in footprint_dims:
        fp_type = fp['entry_name']
        width = fp['dimensions']['width']
        height = fp['dimensions']['height']
        area = width * height
        pin_count = len(fp['pads'])
        
        # Group by footprint type
        if fp_type not in size_analysis['footprint_types']:
            size_analysis['footprint_types'][fp_type] = {
                'count': 0,
                'avg_width': 0,
                'avg_height': 0,
                'avg_area': 0,
                'pin_counts': []
            }
        
        type_info = size_analysis['footprint_types'][fp_type]
        type_info['count'] += 1
        type_info['avg_width'] = (type_info['avg_width'] * (type_info['count'] - 1) + width) / type_info['count']
        type_info['avg_height'] = (type_info['avg_height'] * (type_info['count'] - 1) + height) / type_info['count']
        type_info['avg_area'] = (type_info['avg_area'] * (type_info['count'] - 1) + area) / type_info['count']
        type_info['pin_counts'].append(pin_count)
        
        # Overall size distribution
        size_analysis['size_distribution'].append({
            'type': fp_type,
            'width': width,
            'height': height,
            'area': area,
            'pin_count': pin_count
        })
        
        # Pin count distribution
        if pin_count not in size_analysis['pin_count_distribution']:
            size_analysis['pin_count_distribution'][pin_count] = 0
        size_analysis['pin_count_distribution'][pin_count] += 1
    
    # Sort by area for largest/smallest
    sorted_by_area = sorted(size_analysis['size_distribution'], key=lambda x: x['area'], reverse=True)
    size_analysis['largest_footprints'] = sorted_by_area[:5]
    size_analysis['smallest_footprints'] = sorted_by_area[-5:]
    
    return size_analysis

def get_board_outline_dimensions(pcb_data):
    """Extract board outline dimensions from Edge.Cuts layer"""
    edge_cuts = []
    
    for item in pcb_data.get('graphicalItems', []):
        if (hasattr(item, 'get') and 
            item.get('layer') == 'Edge.Cuts'):
            
            if item.get('_type') == 'GrLine':
                # Line segment
                start = item.get('start', {})
                end = item.get('end', {})
                edge_cuts.append({
                    'type': 'line',
                    'start': (start.get('X', 0), start.get('Y', 0)),
                    'end': (end.get('X', 0), end.get('Y', 0))
                })
            elif item.get('_type') == 'GrArc':
                # Arc segment
                start = item.get('start', {})
                end = item.get('end', {})
                center = item.get('center', {})
                edge_cuts.append({
                    'type': 'arc',
                    'start': (start.get('X', 0), start.get('Y', 0)),
                    'end': (end.get('X', 0), end.get('Y', 0)),
                    'center': (center.get('X', 0), center.get('Y', 0))
                })
    
    if not edge_cuts:
        return None
    
    # Calculate bounding box from edge cuts
    all_points = []
    for edge in edge_cuts:
        all_points.append(edge['start'])
        all_points.append(edge['end'])
        if 'center' in edge:
            all_points.append(edge['center'])
    
    if all_points:
        x_coords = [p[0] for p in all_points]
        y_coords = [p[1] for p in all_points]
        
        return {
            'width': max(x_coords) - min(x_coords),
            'height': max(y_coords) - min(y_coords),
            'bounds': {
                'min_x': min(x_coords),
                'max_x': max(x_coords),
                'min_y': min(y_coords),
                'max_y': max(y_coords)
            },
            'edge_segments': len(edge_cuts)
        }
    
    return None
```

### Component Shape Extraction
```python
def extract_footprint_shapes(pcb_data):
    """Extract detailed shape information from footprint graphics"""
    footprint_shapes = {}
    
    for footprint in pcb_data.get('footprints', []):
        # Get footprint identifier
        entry_name = footprint.get('entryName', '')
        description = footprint.get('description', '')
        
        shape_data = {
            'entry_name': entry_name,
            'description': description,
            'graphics': {
                'silkscreen': [],      # F.SilkS, B.SilkS layers
                'fabrication': [],     # F.Fab, B.Fab layers  
                'courtyard': [],       # F.CrtYd, B.CrtYd layers
                'assembly': [],        # User layers for assembly
                'other': []
            },
            'text_elements': [],
            'shape_bounds': None
        }
        
        # Process all graphic items
        for item in footprint.get('graphicItems', []):
            shape_element = extract_graphic_element(item)
            
            if shape_element:
                # Categorize by layer
                layer = item.get('layer', '')
                if 'SilkS' in layer:
                    shape_data['graphics']['silkscreen'].append(shape_element)
                elif 'Fab' in layer:
                    shape_data['graphics']['fabrication'].append(shape_element)
                elif 'CrtYd' in layer:
                    shape_data['graphics']['courtyard'].append(shape_element)
                elif 'User' in layer or 'Dwgs' in layer:
                    shape_data['graphics']['assembly'].append(shape_element)
                else:
                    shape_data['graphics']['other'].append(shape_element)
        
        # Calculate overall shape bounds
        all_graphics = []
        for category in shape_data['graphics'].values():
            all_graphics.extend(category)
        
        if all_graphics:
            shape_data['shape_bounds'] = calculate_shape_bounds(all_graphics)
        
        footprint_shapes[entry_name] = shape_data
    
    return footprint_shapes

def extract_graphic_element(item):
    """Extract individual graphic element with position and properties"""
    item_type = item.get('_type', '')
    layer = item.get('layer', '')
    
    element = {
        'type': item_type,
        'layer': layer,
        'stroke_width': item.get('stroke', {}).get('width', 0) if item.get('stroke') else 0,
        'coordinates': []
    }
    
    if item_type == 'FpLine':
        # Line segment
        start = item.get('start', {})
        end = item.get('end', {})
        element['coordinates'] = [
            {'x': start.get('X', 0), 'y': start.get('Y', 0)},
            {'x': end.get('X', 0), 'y': end.get('Y', 0)}
        ]
        element['geometry'] = 'line'
        
    elif item_type == 'FpRect':
        # Rectangle
        start = item.get('start', {})
        end = item.get('end', {})
        element['coordinates'] = [
            {'x': start.get('X', 0), 'y': start.get('Y', 0)},
            {'x': end.get('X', 0), 'y': end.get('Y', 0)}
        ]
        element['geometry'] = 'rectangle'
        element['width'] = abs(end.get('X', 0) - start.get('X', 0))
        element['height'] = abs(end.get('Y', 0) - start.get('Y', 0))
        
    elif item_type == 'FpCircle':
        # Circle
        center = item.get('center', {})
        end = item.get('end', {})  # Point on circumference
        center_x, center_y = center.get('X', 0), center.get('Y', 0)
        edge_x, edge_y = end.get('X', 0), end.get('Y', 0)
        radius = ((edge_x - center_x)**2 + (edge_y - center_y)**2)**0.5
        
        element['coordinates'] = [{'x': center_x, 'y': center_y}]
        element['geometry'] = 'circle'
        element['radius'] = radius
        
    elif item_type == 'FpArc':
        # Arc
        start = item.get('start', {})
        mid = item.get('mid', {})
        end = item.get('end', {})
        element['coordinates'] = [
            {'x': start.get('X', 0), 'y': start.get('Y', 0)},
            {'x': mid.get('X', 0), 'y': mid.get('Y', 0)} if mid else None,
            {'x': end.get('X', 0), 'y': end.get('Y', 0)}
        ]
        element['geometry'] = 'arc'
        
    elif item_type == 'FpPoly':
        # Polygon
        points = item.get('points', [])
        element['coordinates'] = [
            {'x': pt.get('X', 0), 'y': pt.get('Y', 0)} 
            for pt in points
        ]
        element['geometry'] = 'polygon'
        
    elif item_type == 'FpText':
        # Text element
        position = item.get('position', {})
        element['coordinates'] = [{'x': position.get('X', 0), 'y': position.get('Y', 0)}]
        element['geometry'] = 'text'
        element['text'] = item.get('text', '')
        element['font_size'] = item.get('effects', {}).get('font', {}).get('height', 0)
        
    else:
        return None  # Unknown element type
    
    return element

def calculate_shape_bounds(graphics):
    """Calculate bounding box for a collection of graphic elements"""
    all_x = []
    all_y = []
    
    for element in graphics:
        for coord in element.get('coordinates', []):
            if coord:  # Skip None coordinates
                all_x.append(coord['x'])
                all_y.append(coord['y'])
        
        # Handle circles specially
        if element.get('geometry') == 'circle' and element.get('radius'):
            center = element['coordinates'][0]
            radius = element['radius']
            all_x.extend([center['x'] - radius, center['x'] + radius])
            all_y.extend([center['y'] - radius, center['y'] + radius])
    
    if not all_x or not all_y:
        return None
    
    return {
        'min_x': min(all_x),
        'max_x': max(all_x),
        'min_y': min(all_y),
        'max_y': max(all_y),
        'width': max(all_x) - min(all_x),
        'height': max(all_y) - min(all_y)
    }

def get_component_visual_representation(pcb_data, component_ref):
    """Get complete visual representation for a specific component"""
    # Find the footprint for this component
    target_footprint = None
    
    for footprint in pcb_data.get('footprints', []):
        for prop in footprint.get('properties', []):
            if (prop.get('key') == 'Reference' and 
                prop.get('value') == component_ref):
                target_footprint = footprint
                break
        if target_footprint:
            break
    
    if not target_footprint:
        return None
    
    # Get component position from computed info
    computed_info = pcb_data.get('computed_info', {})
    positions = computed_info.get('footprint_positions', [])
    comp_position = None
    
    for pos in positions:
        if pos.get('reference') == component_ref:
            comp_position = pos
            break
    
    if not comp_position:
        return None
    
    comp_x = comp_position.get('x', 0)
    comp_y = comp_position.get('y', 0)
    rotation = comp_position.get('rotation', 0)
    
    # Extract shape data
    visual_rep = {
        'reference': component_ref,
        'footprint_type': target_footprint.get('entryName', ''),
        'position': {'x': comp_x, 'y': comp_y},
        'rotation': rotation,
        'shapes': [],
        'pads': [],
        'overall_bounds': None
    }
    
    # Get all graphic elements
    for item in target_footprint.get('graphicItems', []):
        element = extract_graphic_element(item)
        if element:
            # Transform coordinates to board position
            transformed_element = transform_element_to_board(
                element, comp_x, comp_y, rotation
            )
            visual_rep['shapes'].append(transformed_element)
    
    # Get pad shapes
    for pad in target_footprint.get('pads', []):
        pad_shape = {
            'pin_number': pad.get('number', ''),
            'shape': pad.get('shape', ''),
            'position': {
                'x': comp_x + pad.get('position', {}).get('X', 0),
                'y': comp_y + pad.get('position', {}).get('Y', 0)
            },
            'size': {
                'width': pad.get('size', {}).get('X', 0) if pad.get('size') else 0,
                'height': pad.get('size', {}).get('Y', 0) if pad.get('size') else 0
            },
            'drill_diameter': pad.get('drill', {}).get('diameter', 0) if pad.get('drill') else 0
        }
        visual_rep['pads'].append(pad_shape)
    
    # Calculate overall bounds
    all_shapes = visual_rep['shapes'] + visual_rep['pads']
    if all_shapes:
        visual_rep['overall_bounds'] = calculate_component_bounds(all_shapes)
    
    return visual_rep

def transform_element_to_board(element, comp_x, comp_y, rotation):
    """Transform footprint coordinates to board coordinates"""
    import math
    
    transformed = element.copy()
    
    # Convert rotation to radians
    rot_rad = math.radians(rotation) if rotation else 0
    
    # Transform each coordinate
    new_coords = []
    for coord in element.get('coordinates', []):
        if coord is None:
            new_coords.append(None)
            continue
            
        # Apply rotation
        x, y = coord['x'], coord['y']
        if rotation:
            rotated_x = x * math.cos(rot_rad) - y * math.sin(rot_rad)
            rotated_y = x * math.sin(rot_rad) + y * math.cos(rot_rad)
            x, y = rotated_x, rotated_y
        
        # Apply translation
        new_coords.append({
            'x': x + comp_x,
            'y': y + comp_y
        })
    
    transformed['coordinates'] = new_coords
    return transformed

def calculate_component_bounds(shapes_and_pads):
    """Calculate bounding box for component including pads"""
    all_x = []
    all_y = []
    
    for item in shapes_and_pads:
        # Handle pad positions
        if 'position' in item and isinstance(item['position'], dict):
            all_x.append(item['position']['x'])
            all_y.append(item['position']['y'])
            
            # Add pad size if available
            if 'size' in item:
                pad_w = item['size'].get('width', 0) / 2
                pad_h = item['size'].get('height', 0) / 2
                all_x.extend([item['position']['x'] - pad_w, item['position']['x'] + pad_w])
                all_y.extend([item['position']['y'] - pad_h, item['position']['y'] + pad_h])
        
        # Handle graphic coordinates
        for coord in item.get('coordinates', []):
            if coord:
                all_x.append(coord['x'])
                all_y.append(coord['y'])
        
        # Handle circles
        if item.get('geometry') == 'circle' and item.get('radius'):
            center = item['coordinates'][0]
            radius = item['radius']
            all_x.extend([center['x'] - radius, center['x'] + radius])
            all_y.extend([center['y'] - radius, center['y'] + radius])
    
    if not all_x or not all_y:
        return None
    
    return {
        'min_x': min(all_x),
        'max_x': max(all_x),
        'min_y': min(all_y),
        'max_y': max(all_y),
        'width': max(all_x) - min(all_x),
        'height': max(all_y) - min(all_y)
    }

def analyze_component_shapes(pcb_data):
    """Analyze shape complexity and types across all components"""
    shapes = extract_footprint_shapes(pcb_data)
    
    analysis = {
        'shape_complexity': {},
        'layer_usage': {},
        'geometric_elements': {
            'lines': 0,
            'rectangles': 0,
            'circles': 0,
            'arcs': 0,
            'polygons': 0,
            'text': 0
        },
        'most_complex_footprints': [],
        'shape_categories': {
            'simple': [],      # Basic geometric shapes
            'moderate': [],    # Multiple elements
            'complex': []      # Many detailed elements
        }
    }
    
    for fp_name, shape_data in shapes.items():
        # Count elements by type
        total_elements = 0
        fp_elements = {'lines': 0, 'rectangles': 0, 'circles': 0, 'arcs': 0, 'polygons': 0, 'text': 0}
        
        for category, elements in shape_data['graphics'].items():
            total_elements += len(elements)
            
            for element in elements:
                geom_type = element.get('geometry', 'unknown')
                if geom_type == 'line':
                    fp_elements['lines'] += 1
                    analysis['geometric_elements']['lines'] += 1
                elif geom_type == 'rectangle':
                    fp_elements['rectangles'] += 1
                    analysis['geometric_elements']['rectangles'] += 1
                elif geom_type == 'circle':
                    fp_elements['circles'] += 1
                    analysis['geometric_elements']['circles'] += 1
                elif geom_type == 'arc':
                    fp_elements['arcs'] += 1
                    analysis['geometric_elements']['arcs'] += 1
                elif geom_type == 'polygon':
                    fp_elements['polygons'] += 1
                    analysis['geometric_elements']['polygons'] += 1
                elif geom_type == 'text':
                    fp_elements['text'] += 1
                    analysis['geometric_elements']['text'] += 1
        
        # Categorize complexity
        if total_elements <= 4:
            analysis['shape_categories']['simple'].append(fp_name)
        elif total_elements <= 12:
            analysis['shape_categories']['moderate'].append(fp_name)
        else:
            analysis['shape_categories']['complex'].append(fp_name)
        
        analysis['shape_complexity'][fp_name] = {
            'total_elements': total_elements,
            'elements_by_type': fp_elements,
            'has_silkscreen': len(shape_data['graphics']['silkscreen']) > 0,
            'has_fabrication': len(shape_data['graphics']['fabrication']) > 0,
            'has_courtyard': len(shape_data['graphics']['courtyard']) > 0
        }
    
    # Sort by complexity
    complex_sorted = sorted(analysis['shape_complexity'].items(), 
                           key=lambda x: x[1]['total_elements'], reverse=True)
    analysis['most_complex_footprints'] = complex_sorted[:5]
    
    return analysis
```

### JSON Data Navigation
```python
def navigate_pcb_json(pcb_data):
    """Demonstrate how to navigate the PCB JSON structure"""
    
    # Top-level structure
    metadata = pcb_data.get('metadata', {})
    computed_info = pcb_data.get('computed_info', {})
    raw_data = {k: v for k, v in pcb_data.items() 
                if k not in ['metadata', 'computed_info']}
    
    print(f"File source: {metadata.get('source_file', 'unknown')}")
    print(f"KiCad version: {metadata.get('kicad_version', 'unknown')}")
    
    # Computed analysis data (recommended for most use cases)
    print(f"Components: {computed_info.get('footprint_count', 0)}")
    print(f"Nets: {computed_info.get('net_count', 0)}")
    
    # Raw kiutils data (for advanced processing)
    if 'footprints' in raw_data:
        print(f"Raw footprints available: {len(raw_data['footprints'])}")
    
    return {
        'metadata': metadata,
        'computed': computed_info,
        'raw': raw_data
    }

def safe_json_access(json_data, path, default=None):
    """Safely access nested JSON data with path like 'computed_info.nets.0.name'"""
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

# Usage examples:
# component_count = safe_json_access(pcb_data, 'computed_info.footprint_count', 0)
# first_net_name = safe_json_access(pcb_data, 'computed_info.nets.0.name', '')
```

### Error Handling and Validation
```python
def validate_pcb_json(pcb_data):
    """Validate PCB JSON structure and content"""
    errors = []
    warnings = []
    
    # Check required structure
    if 'metadata' not in pcb_data:
        errors.append("Missing 'metadata' section")
    
    if 'computed_info' not in pcb_data:
        errors.append("Missing 'computed_info' section")
    
    computed_info = pcb_data.get('computed_info', {})
    
    # Check computed data consistency
    footprint_count = computed_info.get('footprint_count', 0)
    positions = computed_info.get('footprint_positions', [])
    
    if len(positions) != footprint_count:
        warnings.append(f"Position count ({len(positions)}) != footprint count ({footprint_count})")
    
    # Check for empty references
    empty_refs = sum(1 for pos in positions if not pos.get('reference'))
    if empty_refs > 0:
        warnings.append(f"{empty_refs} components missing reference designators")
    
    # Check coordinate validity
    invalid_coords = sum(1 for pos in positions 
                        if not isinstance(pos.get('x'), (int, float)) or 
                           not isinstance(pos.get('y'), (int, float)))
    if invalid_coords > 0:
        warnings.append(f"{invalid_coords} components have invalid coordinates")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }
```

## Integration Patterns

### PCB Visualization
- **Component placement**: Use footprint positions for layout
- **Net highlighting**: Color-code components by net assignment
- **Layer visualization**: Show different layers with opacity/color
- **3D representation**: Use footprint dimensions for height

### Cross-Reference with Schematic
- **Reference matching**: Link PCB footprints to schematic symbols by reference
- **Net correlation**: Verify PCB nets match schematic nets
- **Component validation**: Ensure all schematic components have PCB footprints

### Manufacturing Data
- **Pick and place**: Export component positions and rotations
- **BOM generation**: Extract component references and values
- **Assembly drawings**: Use silkscreen and reference information
- **Drill files**: Via and pad hole information

## Common Pitfalls
- **Coordinate system**: PCB Y-axis increases upward, different from screen coordinates
- **Layer numbering**: Ordinal numbers may not be sequential
- **Reference extraction**: References stored in properties, not direct attributes
- **Net correlation**: Net numbers vs names can be inconsistent
- **Footprint libraries**: May reference external library files not included in PCB

## File Organization
```
claude/data_store/pcb/
├── project_name/
│   ├── complete_project/
│   │   └── ProjectName.json
│   └── project_info.json
└── kicad_pcb_knowledge.md
```

This structure supports multiple PCB projects with comprehensive analysis data.