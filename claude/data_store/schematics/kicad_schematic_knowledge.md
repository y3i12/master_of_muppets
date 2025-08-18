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
