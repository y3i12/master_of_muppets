# Hardware Graph Structure

## Purpose
This directory contains a multi-layered graph representation of the Master of Muppets hardware design, optimized for PCB placement analysis and decision-making.

## Files

### `node_registry.json` *(deprecated - see complete_node_registry.json)*
Initial partial component database (54 components).

### `complete_node_registry.json`
**CURRENT**: Complete component database with all 163 components from KiCad TSV export.

**Key attributes per node:**
- Component type, value, module, footprint
- Proximity factor (pxf): How close to other components
- Thermal coefficient (thr): Heat generation estimate
- Noise criticality (ncp): Isolation requirements
- Functional group (fgp): Logical grouping
- Signal weight (sgw): Signal integrity importance
- Ground plane requirement (gnd): 0=none, 1=preferred, 2=critical

### `networks.json`
Multiple network representations capturing different relationships:

1. **Primary Connectivity**: Direct electrical connections from schematic
2. **Proximity Network**: Physical clustering requirements
3. **Power Distribution**: Supply rail hierarchy and current flow
4. **Functional Hierarchy**: Logical organization by function
5. **Signal Flow**: Critical signal paths from input to output
6. **Thermal Network**: Heat generation and dissipation zones

### `placement_optimization.json`
Derived placement rules and optimization strategies:
- Absolute constraints (edge placement, fixed positions)
- Relative constraints (proximity requirements)
- Zone assignments (functional areas on PCB)
- Routing priorities (trace length limits, width requirements)
- Optimization scoring weights

## Usage

### For PCB Placement
1. Load node registry to understand component requirements
2. Apply zone assignments for initial placement
3. Use proximity network to cluster related components
4. Check power distribution for decoupling placement
5. Verify signal flow paths for trace routing
6. Consider thermal zones for heat management

### For Analysis
```python
# Example: Find components needing close placement
import json

with open('node_registry.json') as f:
    nodes = json.load(f)['nodes']

critical_proximity = [
    (node_id, data['metadata']['pxf']) 
    for node_id, data in nodes.items() 
    if data['metadata']['pxf'] > 0.8
]
```

## Metadata Encoding Reference

### Proximity Factor (pxf): 0.0 - 1.0
- 0.95-1.0: Must be within 3mm (decoupling caps)
- 0.8-0.95: Should be within 10mm (feedback components)
- 0.6-0.8: Prefer within 20mm (related signals)
- 0.3-0.6: Same functional zone
- 0.0-0.3: Can be anywhere (connectors)

### Noise Criticality Priority (ncp): 0-10
- 8-10: Highly sensitive analog (DAC outputs, op-amp inputs)
- 5-7: Digital high-speed (I2C, MCU)
- 2-4: Power management
- 0-1: Mechanical (connectors, jacks)

### Functional Group IDs (fgp)
- `digital_core`: MCU and immediate support
- `analog_dac`: DAC and references
- `analog_amp`: Op-amps and feedback
- `i2c_pullup`: I2C bus components
- `power_input`: Power entry
- `power_filter`: Filtering and decoupling
- `output`: Output jacks and protection

## Update Protocol
When schematic changes:
1. Update node_registry.json with new components
2. Modify networks.json connections
3. Recalculate placement_optimization.json rules
4. Test placement with new constraints

## Visualization
The graph structure is designed for both human understanding and algorithmic processing. Consider using graph visualization tools for complex relationship analysis.

---
*Generated: 2025-08-15*
*Version: 1.0.0*