# Codebase Graph Structure

## Purpose
This directory contains a multi-layered graph representation of the Master of Muppets codebase, designed for automated analysis and knowledge persistence across Claude sessions.

## Core Concept
Similar to the hardware graph, this structure transforms raw code into queryable, analyzable information with rich metadata encoding domain knowledge about software architecture, performance characteristics, and optimization opportunities.

## Files

### `node_registry.json`
Complete inventory of all code entities (42 nodes) including:
- **Files**: Source files with LOC, complexity metrics
- **Classes**: Including templates, nested types, member functions
- **Data structures**: Buffers, mutexes, thread states
- **Threads**: Execution contexts and their properties
- **Libraries**: External dependencies and system libraries

**Key metadata per node:**
- `criticality`: 0-10 score for system importance
- `layer`: architectural layer (application/core/driver/utility/external/system)
- `complexity`: cyclomatic complexity estimate
- `git_last_modified`: commit hash for version tracking
- Thread-safety indicators, hardware interfaces, performance metrics

### `networks.json`
Seven network layers capturing different relationship aspects:

1. **dependency_graph**: Include/use relationships between components
2. **data_flow**: How data moves through the system with latency annotations
3. **thread_communication**: Inter-thread synchronization and signaling
4. **control_flow**: Function call chains and execution paths
5. **hardware_interface**: Connections to physical hardware (I2C, USB, GPIO)
6. **template_instantiation**: C++ template specializations
7. **criticality_flow**: Real-time critical paths through the system

### `analysis_insights.json`
Derived intelligence from graph analysis:
- **Bottlenecks**: I2C communication (500μs), mutex contention points
- **Hotspots**: High-frequency code paths and their CPU usage
- **Optimization opportunities**: Ranked by impact/complexity/risk
- **Architectural insights**: Design patterns, strengths, weaknesses
- **Thread analysis**: Safety score, synchronization primitives
- **Memory analysis**: Static allocations, stack usage per thread
- **Real-time analysis**: Latency, jitter, deadline characteristics

## Usage Patterns

### For Code Analysis
```python
import json

# Load the graph
with open('node_registry.json') as f:
    nodes = json.load(f)['nodes']

# Find critical components
critical = [n for n, data in nodes.items() 
           if data['metadata'].get('criticality', 0) >= 9]

# Identify thread-safe components
thread_safe = [n for n, data in nodes.items()
              if data['metadata'].get('thread_safe', False)]
```

### For Optimization
```python
with open('analysis_insights.json') as f:
    insights = json.load(f)

# Get optimization opportunities sorted by impact
opts = insights['optimization_opportunities']
by_impact = sorted(opts.items(), 
                  key=lambda x: x[1]['potential_improvement'])
```

### For Navigation
```python
with open('networks.json') as f:
    networks = json.load(f)['networks']

# Trace data flow from USB to DAC
data_flow = networks['data_flow']['edges']
path = find_path(data_flow, 'USBHost_t36', 'rob_tillaart_ad_5993r')
```

## Update Protocol

When code changes:
1. Check git revision: `git rev-parse HEAD`
2. Update affected nodes in `node_registry.json`
3. Modify relevant edges in `networks.json`
4. Recalculate insights if architectural changes
5. Update metadata timestamps

## Metadata Schema

### Node Attributes
- **type**: file/class/struct/template_class/thread/data/library
- **path**: filesystem location
- **language**: cpp/c
- **metadata**: Rich attributes specific to node type
- **dependencies**: Direct dependencies list
- **members**: Class/struct members
- **functions**: Defined functions

### Edge Attributes
- **type**: includes/uses/calls/reads/writes/locks
- **weight**: Importance/frequency (0-10)
- **latency_us**: Timing information
- **criticality**: Real-time importance
- **mechanism**: How communication occurs

### Analysis Metadata
- **severity**: low/medium/high/critical
- **potential_improvement**: Percentage or description
- **complexity**: low/medium/high
- **risk**: low/medium/high
- **location**: Code location [file:line]

## Benefits

1. **Persistent Knowledge**: Survives between Claude sessions
2. **Queryable Structure**: Easy to analyze specific aspects
3. **Version Aware**: Git revision tracking for change detection
4. **Performance Focus**: Latency, bottlenecks, optimization opportunities
5. **Architectural Overview**: Design patterns, coupling, dependencies
6. **Thread Safety**: Synchronization analysis and race condition detection

## Example Queries

- "What are the most critical components?" → Check criticality >= 9
- "Where are the bottlenecks?" → analysis_insights.bottlenecks
- "What depends on Wire library?" → dependency_graph edges to "Wire"
- "Which components are thread-safe?" → node metadata thread_safe flag
- "What's the data flow path?" → data_flow network traversal

---
*Generated: 2025-08-16*
*Version: 1.0.0*
*Git Revision: 0bdb53df897813bafc394d29242ff30ca9edac81*