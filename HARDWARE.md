# Hardware Design Documentation

## Overview

Master Of Muppets hardware provides 16 channels of precision CV output (0-10V) from USB MIDI input. The design emphasizes modularity, expandability, and DIY-friendly construction using commonly available components.

## Specifications

### Electrical Characteristics

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Output Channels** | 16 | Independent CV outputs |
| **Output Range** | 0-10V | 2× amplified from DAC |
| **Resolution** | 12-bit | 4096 steps (2.44mV/step) |
| **Output Impedance** | 1kΩ | Standard for modular synths |
| **Update Rate** | 1-2kHz | Limited by USB on Windows |
| **Latency** | 2-3ms | End-to-end |
| **Power Supply** | ±12V | Eurorack standard |
| **Current Draw** | ~200mA | +12V rail |
| **Current Draw** | ~50mA | -12V rail |
| **USB Power** | 500mA | Teensy 4.1 requirement |

### Physical Dimensions

| Dimension | Value | Notes |
|-----------|-------|-------|
| **Format** | TBD | Eurorack compatible planned |
| **Width** | TBD HP | Target: 12-16 HP |
| **Depth** | <40mm | Skiff-friendly design goal |
| **Connectors** | 3.5mm jack | Standard modular |

## System Architecture

### Block Diagram

```
                    ┌──────────────┐
                    │   USB Host   │
                    │   (Computer) │
                    └──────┬───────┘
                           │ USB MIDI
                    ┌──────▼───────┐
                    │  Teensy 4.1  │
                    │  (Cortex-M7)  │
                    └──┬───────┬───┘
                       │       │
                  Wire1│       │Wire2
                  (I2C)│       │(I2C)
                       │       │
              ┌────────▼───┐ ┌─▼──────────┐
              │  AD5593R   │ │  AD5593R   │
              │   (DAC 1)  │ │  (DAC 2)   │
              │  Ch 1-8    │ │  Ch 9-16   │
              └────┬───────┘ └─────┬──────┘
                   │ 0-5V          │ 0-5V
              ┌────▼───────┐ ┌─────▼──────┐
              │   TL074    │ │   TL074    │
              │  (2× Gain) │ │ (2× Gain)  │
              └────┬───────┘ └─────┬──────┘
                   │ 0-10V         │ 0-10V
              ┌────▼───────────────▼──────┐
              │    16× CV Output Jacks    │
              └───────────────────────────┘
```

### Power Distribution

```
+12V Input ──┬──→ Voltage Regulator ──→ +5V ──→ Teensy 4.1
             │                                 └→ AD5593R (×2)
             └──→ TL074 OpAmps (×4)
             
-12V Input ────→ TL074 OpAmps (×4)

GND ───────────→ Common Ground Plane
```

## Component Selection

### Core Components

#### Microcontroller: Teensy 4.1
- **Processor**: ARM Cortex-M7 @ 600MHz
- **Memory**: 8MB Flash, 1MB RAM
- **USB**: Native USB 2.0 High Speed
- **I2C**: Multiple buses available
- **GPIO**: 55 digital pins
- **Why chosen**: Performance headroom, USB MIDI support, excellent library ecosystem

#### DAC: AD5593R (×2)
- **Channels**: 8 per chip
- **Resolution**: 12-bit
- **Interface**: I2C (400kHz capable)
- **Reference**: Internal 2.5V (doubled to 5V)
- **Features**: Integrated GPIO, ADC capability
- **Why chosen**: Multi-channel integration, future ADC expansion, reliable performance

#### OpAmp: TL074 (×4)
- **Channels**: 4 per chip (16 total needed)
- **Configuration**: Non-inverting, 2× gain
- **Power**: ±12V operation
- **Slew Rate**: 13V/μs
- **Why chosen**: Ubiquitous, affordable, adequate performance for CV

### Supporting Components

#### Passive Components
```
Per Channel:
- R1: 10kΩ (feedback resistor)
- R2: 10kΩ (gain setting resistor)
- R3: 1kΩ (output protection)
- C1: 100nF (bypass capacitor)
- C2: 10nF (filter capacitor)

Power Supply:
- C3-C6: 100μF electrolytic (bulk bypass)
- C7-C10: 100nF ceramic (high-frequency bypass)
```

#### Connectors
- **CV Outputs**: 16× 3.5mm mono jacks (Thonkiconn or similar)
- **Power**: 10-pin Eurorack power header
- **USB**: USB-B or USB-C to host
- **Expansion**: Optional I2C header for future modules

## Schematic Design

### Hierarchical Structure

The KiCad schematic uses a hierarchical design for modularity:

```
MasterOfMuppets (Root Sheet)
├── Power_Supply
│   ├── Input_Protection
│   ├── Voltage_Regulation
│   └── Power_Distribution
├── Digital_Core
│   ├── Teensy_4.1
│   ├── I2C_Bus_1
│   └── I2C_Bus_2
├── DAC_Module_1
│   ├── AD5593R_1
│   └── Channel_Outputs_1-8
├── DAC_Module_2
│   ├── AD5593R_2
│   └── Channel_Outputs_9-16
└── Analog_Output
    ├── OpAmp_Block_1 (Ch 1-4)
    ├── OpAmp_Block_2 (Ch 5-8)
    ├── OpAmp_Block_3 (Ch 9-12)
    └── OpAmp_Block_4 (Ch 13-16)
```

### I2C Addressing

#### Bus Configuration
- **Wire1 (I2C Bus 1)**: DAC 1 (Channels 1-8)
  - SDA: Pin 17
  - SCL: Pin 16
  - Chip Select: Pin 11

- **Wire2 (I2C Bus 2)**: DAC 2 (Channels 9-16)
  - SDA: Pin 25
  - SCL: Pin 24
  - Chip Select: Pin 37

#### Address Scheme
```cpp
// AD5593R base address
#define AD5593R_BASE_ADDR 0x10

// Dynamic addressing via A0 pin
// A0 = LOW:  Address = 0x10
// A0 = HIGH: Address = 0x11
```

### OpAmp Configuration

#### Gain Stage (Per Channel)
```
DAC Output (0-5V)
      │
      R1
      10kΩ
      │
   ┌──┴──┐
   │ +   │
   │     ├──── CV Output (0-10V)
   │ -   │     │
   └──┬──┘     R3
      │        1kΩ
      R2       │
      10kΩ     ⊥ (Protection)
      │
      ⊥ GND
      
Gain = 1 + (R1/R2) = 2×
```

## PCB Design Status

### Current Status: 📋 **Layout Pending** (Season 02 Focus)

### Design Goals

#### Layer Stack
- **Target**: 4-layer PCB
- **Layers**:
  1. Top: Signal routing, component placement
  2. Ground plane
  3. Power planes (±12V, 5V)
  4. Bottom: Signal routing, I2C buses

#### Component Placement Strategy

Based on hardware graph analysis (`claude/hardware_graph/`):

```
┌─────────────────────────────────────┐
│            POWER ZONE               │
│  [Regulators] [Bulk Capacitors]     │
├─────────────────────────────────────┤
│         DIGITAL ZONE                │
│     [Teensy 4.1] [Connectors]       │
├─────────────┬───────────┬───────────┤
│   DAC 1     │  ROUTING  │   DAC 2   │
│ [AD5593R]   │   ZONE    │ [AD5593R] │
├─────────────┴───────────┴───────────┤
│          ANALOG ZONE                │
│  [TL074×4] [Output Protection]      │
├─────────────────────────────────────┤
│         OUTPUT ZONE                 │
│    [16× 3.5mm Jack Connectors]      │
└─────────────────────────────────────┘
```

#### Routing Priorities
1. **Power Distribution**: Star grounding, thick traces
2. **I2C Buses**: Matched length, away from analog
3. **Analog Signals**: Short paths, guard traces
4. **Digital Signals**: Away from sensitive analog

### Manufacturing Considerations

#### PCB Specifications
- **Minimum Trace Width**: 0.2mm (8 mil)
- **Minimum Via Size**: 0.3mm (12 mil)
- **Copper Weight**: 1oz standard
- **Solder Mask**: Green (standard)
- **Silkscreen**: White
- **Surface Finish**: HASL or ENIG

#### Assembly Options
- **DIY Kit**: Through-hole components where possible
- **SMD Components**: 0805 or larger for hand soldering
- **Pre-assembled**: Option for SMD sections

## Testing & Calibration

### Hardware Test Points

Include test points for:
- Power rails (±12V, 5V, 3.3V)
- I2C signals (SDA, SCL)
- DAC outputs (before OpAmp)
- CV outputs (after OpAmp)
- Ground references

### Calibration Procedure

1. **Power Supply Verification**
   - Check all voltage rails
   - Verify current consumption
   - Test protection circuits

2. **Digital Communication**
   - Verify I2C communication with both DACs
   - Test chip select functionality
   - Confirm addressing scheme

3. **Output Calibration**
   ```
   For each channel:
   1. Send MIDI pitch bend center (8192)
   2. Measure CV output (should be 5.0V)
   3. Send minimum pitch bend (0)
   4. Measure CV output (should be 0.0V)
   5. Send maximum pitch bend (16383)
   6. Measure CV output (should be 10.0V)
   ```

4. **Performance Testing**
   - Measure update latency
   - Test all channels simultaneously
   - Verify long-term stability

## Future Hardware Expansions

### Planned Features (Season 02+)

#### ADC Input Module
- Read CV inputs (0-10V)
- Convert to MIDI CC/pitch
- Use AD5593R ADC capability
- Bidirectional CV/MIDI conversion

#### Display Module
- OLED display for configuration
- Show channel values
- Display MIDI activity
- Configuration menu system

#### Ethernet Module
- RTP-MIDI support
- Lower latency potential
- Network configuration
- Multiple device sync

### Modular Expansion System

Design for stackable modules:
```
[Base Unit: 16 CV Out]
         ↕
[Expansion 1: 16 CV In]
         ↕
[Expansion 2: Display/Control]
         ↕
[Expansion 3: Ethernet/WiFi]
```

## Design Files

### KiCad Project Structure

```
CADfiles/MasterOfMuppets/
├── MasterOfMuppets.kicad_pro      # Project file
├── MasterOfMuppets.kicad_sch      # Root schematic
├── Power_Supply.kicad_sch         # Power subsystem
├── Digital_Core.kicad_sch         # Teensy and I2C
├── DAC_Module.kicad_sch           # DAC template
├── Analog_Output.kicad_sch        # OpAmp stages
├── MasterOfMuppets.kicad_pcb      # PCB layout (pending)
└── hardware_analysis.json         # Parser output
```

### Version Control

- Schematics: Text-based for git diff
- Libraries: Project-specific symbols/footprints
- 3D Models: Standard STEP files
- Documentation: Markdown with images

## Bill of Materials (Preliminary)

| Component | Quantity | Unit Cost | Total | Source |
|-----------|----------|-----------|-------|---------|
| Teensy 4.1 | 1 | $30 | $30 | PJRC |
| AD5593R | 2 | $8 | $16 | Mouser |
| TL074 | 4 | $1 | $4 | Various |
| 3.5mm Jack | 16 | $1 | $16 | Thonkiconn |
| Resistors (misc) | 50 | $0.02 | $1 | Various |
| Capacitors (misc) | 30 | $0.10 | $3 | Various |
| Power Header | 1 | $2 | $2 | Various |
| PCB | 1 | $20 | $20 | JLCPCB |
| **Total** | | | **~$92** | |

*Prices are estimates and may vary*

## Safety Considerations

### Electrical Safety
- Proper grounding essential
- Current limiting on outputs
- Protection against reverse power
- ESD protection on I/O

### Thermal Management
- Adequate ventilation required
- Heat sinks on regulators if needed
- Monitor OpAmp temperature
- Consider thermal zones in PCB layout

---

*For software architecture, see [ARCHITECTURE.md](ARCHITECTURE.md). For contributing to hardware design, see [CONTRIBUTING.md](CONTRIBUTING.md).*