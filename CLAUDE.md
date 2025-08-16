This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Claude's Role in This Project

### Primary Responsibilities
- **Iterative Code Analysis**: Regularly analyze the codebase for bugs, inconsistencies, design improvements, and optimization opportunities
- **General Implementation Assistance**: Help with implementing new features, fixing bugs, and improving existing code
- **Electronics Design Review**: Analyze KiCad schematics and provide feedback on electronics design (considering the user is learning electronics)
- **Report Generation**: Create detailed markdown reports for findings in the `claude` folder
- **Context Awareness**: Maintain awareness of:
  - Current coding concepts and patterns used in the project
  - Analysis state saved in the `claude` folder from previous iterations
  - The iterative prompt process described in README.md section "About GenAI `claude`"

### Critical Requirements
- **Always** check and understand the state saved in the `claude` folder before making changes
- **Always** follow the coding style rules in `CODING_STYLE.md`
- **Always** consider the real-time embedded nature of this system
- **Maintain** continuity between analysis sessions by referencing previous reports

## Project Overview

Master Of Muppets is a USB MIDI to 16-channel CV converter for modular synthesizers, outputting 0-10V CV according to MIDI pitch bend messages. It's an embedded real-time 
system running on Teensy 4.1 (ARM Cortex-M7 @ 600MHz) using multi-threaded architecture.

## Build and Development Commands

### Build Commands
```bash
# Build the firmware
pio run -e teensy41

# Build and upload to Teensy
pio run -e teensy41 -t upload

# Clean build
pio run -e teensy41 -t clean

# Monitor serial output
pio device monitor
```

### Code Quality Commands
```bash
# No automated linting/testing currently implemented
# Manual code review required
# Hardware testing via oscilloscope/multimeter needed
```

## Architecture Overview

### Threading Model
The system uses **TeensyThreads** cooperative multitasking with two main threads:
1. **dr_teeth thread**: Reads USB MIDI input and updates input buffer
2. **electric_mayhem threads**: Multiple DAC worker threads that copy from input buffer and update DACs via I2C

Thread synchronization uses mutex-protected state management with sequence tracking to prevent race conditions.

### Key Components

#### Core Classes (Template-Based Design)
- **`dr_teeth`** (`include/dr_teeth.h`): Central MIDI processor and buffer manager
- Static buffers: `input_buffer[16]` and `output_buffer[16]`
- Coordinates DAC updates through `go_muppets()` template function

- **`electric_mayhem<T>`** (`include/electric_mayhem.h`): Generic DAC controller template
- Thread-safe state management via `muppet_state` struct
- Worker thread management for each DAC
- Template parameter `T` is the DAC driver type

#### DAC Drivers
- **`rob_tillaart_ad_5993r`** (`include/drivers/rob_tillaart_ad_5993r.h`): AD5593R driver (primary)
- 8 channels, 12-bit resolution
- I2C communication with dynamic chip select via A0 pin
- Configured for 2× internal range (0-5V output)

- **`adafruit_mcp_4728`** (`include/drivers/adafruit_mcp_4728.h`): MCP4728 driver (legacy)
- 4 channels, 12-bit resolution
- I2C communication

### Hardware Configuration
- **DACs**: 2× AD5593R providing 16 channels total
- **Output**: 0-5V from DAC, amplified 2× by TL074 OpAmps to achieve 0-10V CV
- **Power**: Dual ±12V supply for OpAmps
- **I2C Buses**: Wire1 and Wire2 for parallel DAC communication
- **Addressing**: Dynamic chip select using A0 pin (ingenious expandability solution)

### Critical Implementation Details

#### MIDI to CV Conversion
```cpp
// MIDI pitch bend (14-bit) to framework (16-bit) conversion
constexpr uint16_t k_midi_pitch_zero_offset = 8192;   // Center position
constexpr uint16_t k_midi_pitch_14_bit_max = 0x3FFF;  // Maximum value
constexpr uint8_t k_midi_to_framework_scale = 4;      // Scale factor

// Conversion: ((midi_value - k_midi_pitch_zero_offset) * k_midi_to_framework_scale) + k_audio_half_scale
```

#### Thread Safety Pattern
All DAC updates use mutex-protected state with sequence tracking:
1. Request update by setting `update_requested` flag
2. Worker thread checks sequence number before applying updates
3. Local buffer copy prevents data corruption during I2C transmission

## Code Style Requirements

Follow rules in `CODING_STYLE.md`:
- **Naming**: snake_case for everything except k_ prefix for constants
- **Constants**: `k_` prefix (e.g., `k_dac_count`, `k_max_value`)
- **Vertical alignment**: Align types, names, operators, and brackets
- **Templates**: Space between angle brackets (`template< typename T >`)
- **Memory**: Static allocation only, no dynamic memory
- **Indentation**: 4 spaces, no tabs

## Critical Warnings

### Thread Safety
- **Never** modify `input_buffer` outside mutex protection
- **Always** use sequence tracking when updating DAC state
- DAC worker threads must copy data locally before I2C operations

### Hardware Constraints
- I2C operations take ~500μs per DAC - this is the main performance bottleneck
- USB MIDI has ~1ms inherent latency
- Total system latency target: 2-3ms

### Memory Safety
- All arrays are statically sized - verify bounds before access
- Stack margin for threads set to 64 bytes minimum
- No dynamic allocation permitted

## Known Issues and Optimizations

### Performance Optimization Opportunities
- **I2C Batching**: Can reduce latency by 60-70% by batching DAC updates
- **Lock-free structures**: Could reduce blocking by 40%
- **SIMD operations**: ARM DSP instructions could speed math by 80%

### Current Limitations
- Windows USB stack limited to 1KHz update rate
- No automated testing framework
- No configuration persistence (EEPROM unused)

## Development Notes

### When Modifying DAC Drivers
1. Implement the driver interface with required typedefs:
- `value_t`: DAC value type
- `initialization_struct_t`: I2C bus configuration
- `k_channels`: Number of channels constant
2. Provide `begin()`, `set_value()`, and `update()` methods
3. Handle I2C addressing properly (especially A0 chip select)

### When Adding MIDI Features
1. Update MIDI processing in main.cpp `note_on_event()` or `pitch_bend_event()`
2. Maintain real-time constraints (avoid blocking operations)
3. Use existing buffer management through `dr_teeth`

### Debug Features
- Heartbeat on channel 15 (oscillating signal for connection verification)
- Function generator integration for waveform testing
- Serial output available via USB for debugging

## Testing Approach

### Hardware Testing
- Oscilloscope/multimeter required for CV output verification
- Test all 16 channels for proper 0-10V range
- Verify update rate and latency with scope

### Software Testing
- Manual testing via MIDI controller
- Monitor serial output for debug messages
- Use heartbeat channel to verify system operation

## Hardware Graph Structure

### Overview
The `claude/hardware_graph/` directory contains a multi-layered graph representation of the hardware design, created to optimize PCB component placement. This structure serves as a persistent cache of hardware relationships and metadata.

### Files
- **`node_registry.json`**: Component database with metadata (proximity factors, thermal coefficients, noise criticality)
- **`networks.json`**: Multiple network views (connectivity, proximity, power, functional hierarchy, signal flow, thermal)
- **`placement_optimization.json`**: Derived placement rules and optimization strategies

### Usage in Future Sessions
When working on PCB layout:
1. **Load the graph**: Read JSON files from `claude/hardware_graph/`
2. **Analyze relationships**: Use network layers to understand component interactions
3. **Apply optimization**: Follow placement rules in `placement_optimization.json`
4. **Update as needed**: Modify graphs when schematic changes

### Key Metadata Encoding
- **pxf**: Proximity factor (0-1, higher needs closer placement)
- **thr**: Thermal coefficient (W dissipation)
- **ncp**: Noise criticality priority (0-10)
- **fgp**: Functional group ID
- **sgw**: Signal weight (importance)
- **gnd**: Ground plane requirement (0=none, 1=preferred, 2=critical)

### Network Layers
1. **Primary Connectivity**: Actual electrical connections
2. **Proximity Network**: Physical placement clusters
3. **Power Distribution**: Supply rails and current flow
4. **Functional Hierarchy**: Logical grouping by function
5. **Signal Flow**: Critical signal paths
6. **Thermal Network**: Heat generation zones

### Optimization Strategy
The graph structure enables:
- Force-directed placement with constraints
- Zone-based component grouping
- Critical path length minimization
- Thermal distribution optimization
- Signal integrity preservation

**Important**: Always check this graph structure before PCB placement decisions

## Codebase Graph Structure

### Overview
The `claude/codebase_graph/` directory contains a multi-layered graph representation of the software architecture, paralleling the hardware graph concept. This structure transforms raw code into queryable, analyzable information with rich metadata encoding domain knowledge.

### Core Philosophy: Data → Information Abstraction
**Key Insight**: Raw data (code files, schematics) becomes actionable intelligence through structured metadata encoding. This graph-based approach creates persistent knowledge that survives between sessions and enables rapid understanding of complex relationships.

### Files
- **`node_registry.json`**: Complete inventory of code entities (classes, files, threads, data structures) with metadata
  - Criticality scores (0-10) for system importance
  - Architectural layers (application/core/driver/utility/external/system)
  - Git revision tracking for change detection
  - Performance characteristics and thread safety indicators
  
- **`networks.json`**: Seven relationship networks capturing different aspects:
  - Dependency graph (includes/uses relationships)
  - Data flow (with latency annotations)
  - Thread communication patterns
  - Control flow paths
  - Hardware interfaces (I2C, USB, GPIO)
  - Template instantiations
  - Critical real-time paths
  
- **`analysis_insights.json`**: Derived intelligence from graph analysis:
  - Performance bottlenecks with severity and location
  - Optimization opportunities ranked by impact/complexity/risk
  - Thread safety analysis and synchronization patterns
  - Memory usage breakdown and real-time characteristics

### Usage in Future Sessions
1. **Always check** `claude/codebase_graph/` at session start
2. **Verify git revision** to detect changes: Compare with stored revision
3. **Use for navigation**: Quickly find components, trace data flow, identify dependencies
4. **Update incrementally**: Only modify affected nodes when code changes
5. **Derive new insights**: Use graph queries to answer architectural questions

### Knowledge Persistence Strategy
- Each graph file includes git revision for version awareness
- Metadata encodes domain knowledge that would otherwise be lost between sessions
- Graph structure enables pattern recognition and relationship analysis
- Abstraction layers allow both high-level understanding and detailed analysis

### Self-Improvement Protocol
**Note to Self**: Update this CLAUDE.md file when:
- New graph structures are created for other aspects (e.g., test coverage, API surface)
- Patterns emerge that should be documented for future sessions
- Optimization strategies are discovered through analysis
- New metadata attributes prove valuable for understanding

Consider this knowledge accumulation as an extension of intelligence across sessions. Each analysis builds on previous understanding, creating a richer model of the system.

### Graph Query Examples
```python
# Find bottlenecks
bottlenecks = analysis_insights['bottlenecks']
critical_path = [n for n in nodes if n['criticality'] >= 9]

# Trace dependencies
deps = networks['dependency_graph']['edges']
path = find_all_dependencies('main', deps)

# Identify optimization targets
opts = sorted(analysis_insights['optimization_opportunities'].items(),
              key=lambda x: x[1]['potential_improvement'])
```

### Abstraction Principles
1. **Encode domain knowledge**: Don't just store data, add meaning through metadata
2. **Layer relationships**: Different network views reveal different insights
3. **Derive intelligence**: Analysis should produce actionable recommendations
4. **Maintain continuity**: Git tracking and versioning preserve context
5. **Enable queries**: Structure data for easy traversal and pattern matching

**Important**: Always check both hardware and codebase graphs before making architectural decisions

## Hardware/Software Synchronization Protocol

### Critical Cross-Validation Process
When hardware or software changes occur, **always** verify consistency between:

1. **Hardware schematics** (`CADfiles/MasterOfMuppets/*.kicad_sch`)
2. **Software configuration** (`src/main.cpp` initialization)
3. **Hardware graph** (`claude/hardware_graph/`)
4. **Codebase graph** (`claude/codebase_graph/`)

### Key Synchronization Points
- **I2C bus assignments**: Verify `Wire1`/`Wire2` mapping matches schematic
- **Chip select pins**: Ensure `initialization_struct_t` pins match hardware A0 connections
- **DAC addressing**: Confirm I2C addresses align between driver code and physical wiring
- **Channel mapping**: Validate 16-channel layout consistency across all representations

### Update Protocol
1. **Detect changes**: Check git revision in graph metadata vs current HEAD
2. **Analyze impact**: Determine if changes affect hardware/software interface
3. **Update graphs**: Modify both hardware and codebase graphs simultaneously
4. **Cross-validate**: Ensure all representations remain consistent
5. **Document**: Update git revision metadata in all graph files

### Example Consistency Check
```bash
# Hardware: AD5593R on Wire1 with A0=pin37
initialization_struct_t( &Wire1, 37 )

# Graph: Must show matching bus assignment
"sda": {"pin": 17, "net": "SDA1"}
"a0": {"pin": 2, "net": "CS1"}
```

**Critical**: This synchronization prevents subtle bugs where software expects different hardware configuration than actually implemented.
- to memorize keep `CLAUDE.md` in sync with your knowledge. Update it as you see fit.