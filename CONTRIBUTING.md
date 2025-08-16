# Contributing to Master Of Muppets

Thank you for your interest in contributing to Master Of Muppets! This guide will help you get started with development, understand our unique AI-assisted workflow, and maintain code quality.

## Table of Contents
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [AI-Assisted Development](#ai-assisted-development)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community Tools](#community-tools)

## Development Setup

### Prerequisites

#### Hardware
- **Teensy 4.1** development board
- **USB Cable** for programming and debugging
- **Oscilloscope** (recommended for testing)
- **MIDI Controller** (for testing)

#### Software
- **PlatformIO** (VS Code extension recommended)
- **Python 3.8+** (for tooling)
- **Git** for version control
- **KiCad 7.0+** (for hardware design)

### Environment Setup

1. **Clone the Repository**
```bash
git clone https://github.com/y3i12/master_of_muppets.git
cd master_of_muppets
```

2. **Install PlatformIO**
```bash
# Via pip
pip install platformio

# Or use VS Code extension marketplace
```

3. **Install Project Tools**
```bash
# Install KiCad Hierarchical Parser
pip install -e claude/tools/

# Verify installation
kicad-parser --help
```

4. **Build the Firmware**
```bash
# Build for Teensy 4.1
pio run -e teensy41

# Clean build
pio run -e teensy41 -t clean
```

5. **Upload to Device**
```bash
# Upload firmware
pio run -e teensy41 -t upload

# Monitor serial output
pio device monitor
```

### Repository Structure

```
master_of_muppets/
├── src/                 # Source code
├── include/            # Headers and templates
│   ├── drivers/        # DAC driver implementations
│   ├── dr_teeth.h      # MIDI processor
│   └── electric_mayhem.h # DAC controller template
├── lib/                # External libraries
├── claude/             # AI development artifacts
│   ├── sessions/       # Development episodes
│   ├── tools/          # KiCad parser and utilities
│   ├── hardware_graph/ # Hardware relationship data
│   └── codebase_graph/ # Software architecture data
├── CADfiles/           # KiCad schematics and PCB
└── docs/               # Additional documentation
```

## Coding Standards

We follow specific conventions outlined in [CODING_STYLE.md](CODING_STYLE.md):

### Naming Conventions
```cpp
// Constants: k_ prefix
constexpr uint8_t k_channel_count = 16;
constexpr uint16_t k_max_value = 65535;

// Variables and functions: snake_case
uint16_t input_value;
void process_midi_event();

// Classes and templates: snake_case
template< typename T >
class electric_mayhem {
    // ...
};
```

### Code Organization

#### Vertical Alignment
Align related elements for readability:
```cpp
constexpr uint8_t  k_channels        = 16;
constexpr uint16_t k_max_dac_value   = 4095;
constexpr uint32_t k_update_interval = 1000;

void set_channel_value( uint8_t channel, uint16_t value );
void request_update   ( void );
void clear_all_values ( void );
```

#### Template Formatting
```cpp
// Space between angle brackets
template< typename T >
class dac_controller {
    using value_t = typename T::value_t;
    // ...
};
```

### Memory Management
- **No dynamic allocation** - Use static buffers
- **Fixed-size arrays** - Prevent buffer overflows
- **Stack monitoring** - Minimum 64-byte margin

### Real-Time Constraints
- **Bounded execution time** - No unbounded loops
- **Deterministic operations** - Avoid variable-time algorithms
- **Priority awareness** - Respect thread priorities

## AI-Assisted Development

This project pioneered AI-assisted embedded systems development. Here's how to work with our AI protocols:

### Using Claude AI

#### Initial Setup
When starting a session with Claude:
1. Share the [CLAUDE.md](CLAUDE.md) file for context
2. Reference current season/episode structure
3. Point to relevant knowledge graphs

#### Effective Prompting
```markdown
# Example: Starting a new feature
"I'm working on Season 02, Episode 01: [Topic Name].
Please check the hardware_graph and codebase_graph for current state.
I want to implement [feature description].
Consider real-time constraints and existing patterns."
```

### Knowledge Graphs

#### Hardware Graph
Located in `claude/hardware_graph/`:
- **node_registry.json**: Component metadata
- **networks.json**: Relationship networks
- **placement_optimization.json**: PCB rules

#### Codebase Graph  
Located in `claude/codebase_graph/`:
- **node_registry.json**: Code entity inventory
- **networks.json**: Software relationships
- **analysis_insights.json**: Performance analysis

### Episode Documentation

When documenting work:

1. **Write Episode**: Create new episode file
```bash
claude/sessions/season_XX_theme/episode_YY_topic.md
```

2. **Update Episode**: Append to existing episode
```markdown
### OP:
[Your message/question]

### Sir Claude:
[AI response and actions]
```

3. **Episode Structure**:
- Session overview
- Key innovations
- Breakthrough moments
- Technical achievements
- Lessons learned

### Seasonal Development

Each season represents a major development phase:
- **Season = Git Branch** (e.g., `claude_sessions_2_pcb`)
- **Episode = Focused Topic** (e.g., "PCB Layout Optimization")
- **Merge = Season Complete** (integrate to main)

## Testing Guidelines

### Firmware Testing

#### Unit Tests
```cpp
// Test MIDI conversion accuracy
void test_midi_to_cv_conversion() {
    uint16_t midi_value = 8192;  // Center position
    uint16_t cv_value = convert_midi_to_cv(midi_value);
    assert(cv_value == 32768);
}
```

#### Integration Tests
- Multi-channel stress testing
- Latency measurements
- Long-duration stability
- Power cycle recovery

### Hardware Testing

#### Required Equipment
- Oscilloscope for waveform verification
- Multimeter for voltage calibration
- MIDI controller for input testing

#### Test Procedures
1. **Voltage Calibration**
   - Verify 0-10V output range
   - Check all 16 channels
   - Measure OpAmp gain (2×)

2. **Timing Verification**
   - Measure end-to-end latency
   - Check update rate consistency
   - Verify thread timing

3. **Stress Testing**
   - All channels simultaneous updates
   - Rapid MIDI message flooding
   - Extended operation (24+ hours)

### Tool Testing

For KiCad parser and other tools:
```bash
# Run test suite
cd claude/tools
python test_parser.py

# Test with sample file
kicad-parser ../CADfiles/MasterOfMuppets/MasterOfMuppets.kicad_sch
```

## Pull Request Process

### Before Submitting

1. **Update Documentation**
   - Add/update relevant markdown files
   - Update knowledge graphs if needed
   - Document in appropriate episode

2. **Run Quality Checks**
```bash
# Build firmware
pio run -e teensy41

# Test tools (if modified)
python claude/tools/test_parser.py
```

3. **Verify Hardware Compatibility**
   - Test with actual hardware if possible
   - Document any hardware requirements

### PR Guidelines

#### Title Format
```
Season XX: [Feature/Fix/Docs] - Brief description
```

Examples:
- `Season 02: Feature - Add EEPROM configuration persistence`
- `Season 02: Fix - Resolve I2C timeout on bus reset`
- `Season 02: Docs - Update hardware specifications`

#### Description Template
```markdown
## Overview
[Brief description of changes]

## Episode Reference
Season XX, Episode YY: [Episode Title]

## Changes
- [List of specific changes]
- [Include file paths when relevant]

## Testing
- [How you tested the changes]
- [Hardware used]
- [Test results]

## Performance Impact
- [Latency changes]
- [Memory usage]
- [CPU utilization]

## Checklist
- [ ] Code follows CODING_STYLE.md
- [ ] Documentation updated
- [ ] Episode documented
- [ ] Hardware tested (if applicable)
- [ ] Knowledge graphs updated (if needed)
```

### Review Process

1. **Automated Checks** (when available)
2. **Code Review** by maintainers
3. **Hardware Testing** verification
4. **Documentation Review**
5. **Merge to Season Branch**

## Community Tools

### KiCad Hierarchical Parser

The project includes a production-ready KiCad parser:

#### Installation
```bash
pip install kicad-hierarchical-parser
```

#### Development
```bash
# Clone and install in development mode
cd claude/tools
pip install -e .

# Run tests
python test_parser.py
```

#### Contributing to Tools
- Maintain 100% test coverage
- Update README and examples
- Follow Python PEP 8 style
- Document performance characteristics

### Creating New Tools

When developing new tools:
1. Place in `claude/tools/` directory
2. Include comprehensive README
3. Add MIT license header
4. Create test suite
5. Document in episode
6. Consider pip packaging

## Getting Help

### Resources
- [Project README](README.md) - Overview and quick start
- [Architecture Guide](ARCHITECTURE.md) - System design details
- [Hardware Guide](HARDWARE.md) - Schematics and specifications
- [AI Sessions](claude/sessions/) - Development history
- [Issues](https://github.com/y3i12/master_of_muppets/issues) - Bug reports and features

### Communication
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions

### AI Assistance
For AI-assisted development:
1. Reference this guide and CLAUDE.md
2. Use episode structure for documentation
3. Maintain knowledge graphs
4. Follow established patterns

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Share knowledge freely
- Credit contributions properly
- Maintain project's playful spirit (Muppets references encouraged!)

---

*Thank you for contributing to Master Of Muppets! Together we're making human-AI collaboration more intelligent, one session at a time.* 🤝