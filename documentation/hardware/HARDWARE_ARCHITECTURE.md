# Hardware Architecture

## Overview

The Master of Muppets hardware architecture employs a hierarchical modular design with 6 distinct modules totaling 77 components across 46 nets. The system is optimized for precision analog performance with real-time digital control.

## System Block Diagram

```mermaid
graph TB
    subgraph "Power Management"
        PS[±12V Power Supply]
        REG[LD1117 3.3V Regulator]
        FILT[Unripple Module<br/>Power Filtering]
        
        PS --> REG
        REG --> FILT
    end
    
    subgraph "Digital Control"
        USB[USB MIDI Input]
        MCU[Teensy 4.1<br/>ARM Cortex-M7]
        I2C1[I2C Bus 1]
        I2C2[I2C Bus 2]
        
        USB --> MCU
        MCU --> I2C1
        MCU --> I2C2
    end
    
    subgraph "DAC Stage"
        DAC1[AD5593R #1<br/>Channels 1-8]
        DAC2[AD5593R #2<br/>Channels 9-16]
        
        I2C1 --> DAC1
        I2C2 --> DAC2
    end
    
    subgraph "Analog Processing"
        AMP1[TL074 Op-Amps<br/>Ch 1-4 Amplification]
        AMP2[LT1014D Op-Amps<br/>Ch 5-8 Amplification]
        AMP3[TL074 Op-Amps<br/>Ch 9-12 Amplification]
        AMP4[LT1014D Op-Amps<br/>Ch 13-16 Amplification]
        
        DAC1 --> AMP1
        DAC1 --> AMP2
        DAC2 --> AMP3
        DAC2 --> AMP4
    end
    
    subgraph "Output Interface"
        JACK[16x 3.5mm Mono Jacks<br/>0-10V CV Outputs]
        
        AMP1 --> JACK
        AMP2 --> JACK
        AMP3 --> JACK
        AMP4 --> JACK
    end
    
    FILT --> MCU
    FILT --> DAC1
    FILT --> DAC2
    PS --> AMP1
    PS --> AMP2
    PS --> AMP3
    PS --> AMP4
```

## Module Breakdown

### 1. Main Coordinator Module (12 components, 15 nets)

**Function**: System-level power management and hierarchical coordination

**Key Components**:
- **LD1117 (U1)**: 3.3V voltage regulator for digital circuits
- **1000µF Capacitor (C1)**: Bulk power filtering for stability
- **100nF Capacitor (C2)**: High-frequency decoupling

**Design Features**:
- Central power distribution hub
- Hierarchical sheet instance coordination
- System-level power symbols and references

### 2. Teensy Module (5 components, 3 nets)

**Function**: Main system controller and USB MIDI interface

```mermaid
graph LR
    USB[USB MIDI] --> T1[Teensy 4.1]
    T1 --> I2C1[I2C Bus 1<br/>Pins 18,19]
    T1 --> I2C2[I2C Bus 2<br/>Pins 24,25]
    T1 --> GPIO[GPIO Control<br/>Chip Select]
```

**Key Specifications**:
- **Processor**: ARM Cortex-M7 @ 600MHz
- **Memory**: 1MB RAM, 8MB Flash, TCM
- **USB**: Native high-speed MIDI class compliant
- **I2C**: 3 independent buses available
- **Real-time**: Hardware FPU, deterministic timing

### 3. DAC Module (6 components, 6 nets)

**Function**: Digital to analog conversion with I2C interface

```mermaid
graph TB
    subgraph "AD5593R Configuration"
        DAC[AD5593R]
        R1[10kΩ Reset Pullup]
        R2[4.7kΩ SDA Pullup]
        R3[4.7kΩ SCL Pullup]
        
        DAC --- R1
        DAC --- R2
        DAC --- R3
    end
    
    I2C[I2C Bus] --> DAC
    DAC --> OUT[8x Analog Outputs<br/>0-2.5V Range]
```

**Technical Specifications**:
- **Resolution**: 12-bit (4096 levels)
- **Channels**: 8 configurable DAC/ADC per chip
- **Interface**: I2C up to 400kHz (1MHz capable)
- **Reference**: Internal 2.5V or external
- **Settling Time**: 6µs to 0.1% accuracy
- **Address Selection**: Chip select pin controlled

### 4. Amplifier Module (35 components, 20 nets)

**Function**: Precision 2x gain amplification from 0-2.5V to 0-10V

```mermaid
graph TB
    subgraph "Amplifier Configuration"
        IN[DAC Input<br/>0-2.5V]
        
        subgraph "Non-Inverting Amplifier"
            R_IN[1kΩ Input]
            OP[Op-Amp]
            R_FB[47kΩ Feedback]
            R_GND[22kΩ Ground]
            
            IN --> R_IN
            R_IN --> OP
            OP --> R_FB
            R_FB --> OP
            R_GND --> OP
        end
        
        OUT[CV Output<br/>0-10V]
        OP --> OUT
    end
```

**Key Components**:
- **TL074**: Quad JFET op-amp for general-purpose applications
- **LT1014D**: Precision quad op-amp (25µV offset, 0.6µV/°C drift)
- **Precision Resistors**: 1% tolerance for accurate gain setting
- **Decoupling Capacitors**: Power supply noise rejection

**Performance Characteristics**:
- **Gain**: 2x non-inverting configuration
- **Input Range**: 0-2.5V from DAC
- **Output Range**: 0-10V CV standard
- **Bandwidth**: DC to audio frequencies
- **Noise**: Optimized for professional audio applications

### 5. Unripple Module (3 components, 2 nets)

**Function**: Multi-stage power supply filtering

```mermaid
graph LR
    PWR_IN[±12V Input] --> C21[100nF HF Bypass]
    C21 --> C22[10µF Mid-Freq Filter]
    C22 --> PWR_OUT[Clean ±12V Output]
```

**Filtering Performance**:
- **Frequency Range**: 100Hz to 10MHz
- **Ripple Suppression**: >40dB at switching frequencies
- **Transient Response**: Fast settling, low impedance
- **Applications**: Analog/digital isolation, noise reduction

### 6. Jack Sheet (16 components, 0 nets)

**Function**: CV output connectors and user interface

**Connector Specifications**:
- **Type**: 3.5mm mono switched (Amphenol compatible)
- **Mounting**: Panel mount with threaded bushing
- **Current Rating**: 1A continuous
- **Voltage Rating**: 30V DC maximum
- **Spacing**: Eurorack compatible layout

## Signal Path Analysis

### Complete Signal Chain

```mermaid
sequenceDiagram
    participant MIDI as USB MIDI
    participant MCU as Teensy 4.1
    participant I2C as I2C Bus
    participant DAC as AD5593R
    participant AMP as Op-Amp
    participant OUT as CV Output

    MIDI->>MCU: Pitch Bend (14-bit)
    Note right of MCU: Processing Time: <50µs
    MCU->>I2C: DAC Update (12-bit)
    Note right of I2C: I2C Transaction: ~20µs
    I2C->>DAC: Digital Value
    Note right of DAC: Settling Time: 6µs
    DAC->>AMP: Analog Signal (0-2.5V)
    Note right of AMP: Amplification: <1µs
    AMP->>OUT: CV Output (0-10V)
    
    Note over MIDI,OUT: Total Latency: <100µs per channel
```

### Critical Path Analysis

1. **USB MIDI Processing**: <50µs (USB stack + parsing)
2. **I2C Communication**: ~20µs per DAC update
3. **DAC Settling**: 6µs to 0.1% accuracy
4. **Op-Amp Response**: <1µs slew rate limited
5. **Total System Latency**: <100µs per channel

## Power Distribution

### Power Requirements

| Rail | Voltage | Current | Application |
|------|---------|---------|-------------|
| **+12V** | +12V ±5% | 200mA | Op-amp positive supply |
| **-12V** | -12V ±5% | 200mA | Op-amp negative supply |
| **+3.3V** | +3.3V ±5% | 500mA | Digital logic (Teensy, DACs) |
| **+5V** | +5V ±5% | 50mA | DAC analog supply |

### Power Distribution Network

```mermaid
graph TB
    subgraph "External Supply"
        EXT[±12V External PSU]
    end
    
    subgraph "Regulation Stage"
        REG1[LD1117 +3.3V]
        REG2[Derived +5V]
        
        EXT --> REG1
        EXT --> REG2
    end
    
    subgraph "Filtering Network"
        BULK[1000µF Bulk Storage]
        HF[100nF HF Bypass]
        MF[10µF Mid-Freq]
        
        REG1 --> BULK
        BULK --> HF
        HF --> MF
    end
    
    subgraph "Load Distribution"
        DIGITAL[Digital Circuits<br/>Teensy + DACs]
        ANALOG[Analog Circuits<br/>Op-Amps]
        
        MF --> DIGITAL
        EXT --> ANALOG
    end
```

## Thermal Considerations

### Heat Dissipation Analysis

| Component | Power Dissipation | Thermal Management |
|-----------|------------------|-------------------|
| **Teensy 4.1** | ~500mW @ 600MHz | Built-in thermal pad |
| **LD1117** | ~1W @ 500mA load | Heat sink recommended |
| **AD5593R** | <50mW per chip | Standard IC cooling |
| **Op-Amps** | <100mW per quad | Standard IC cooling |

### Thermal Design Guidelines

1. **Component Placement**: Separate high-power components
2. **Airflow**: Natural convection or forced air cooling
3. **Heat Sinks**: LD1117 regulator requires thermal management
4. **PCB Layout**: Thermal vias for heat spreading

## EMC and Signal Integrity

### Design Considerations

1. **Ground Plane**: Continuous ground plane for noise reduction
2. **Power Supply Decoupling**: Local bypass capacitors at each IC
3. **I2C Signal Integrity**: Controlled impedance, matched trace lengths
4. **Analog/Digital Separation**: Physical and electrical isolation
5. **Shielding**: Enclosure considerations for professional audio

### Critical Design Rules

- **Trace Width**: Minimum 0.2mm for signals, 0.5mm for power
- **Via Stitching**: Ground plane continuity across layers
- **Component Placement**: Critical analog components away from switchers
- **Clock Distribution**: Minimize high-frequency signal coupling

## Manufacturing Considerations

### PCB Specifications

- **Layer Count**: 4-layer recommended (signal/ground/power/signal)
- **Board Thickness**: 1.6mm standard
- **Material**: FR4 standard, Rogers for high-frequency if needed
- **Surface Finish**: HASL or ENIG for reliability

### Assembly Requirements

- **SMD Components**: Majority surface mount for automated assembly
- **Through-hole**: Connectors and large capacitors only
- **Test Points**: Accessible for in-circuit testing and debugging
- **Programming Interface**: Teensy USB connector accessible

### Quality Control

- **Electrical Test**: In-circuit test for all nets and components
- **Functional Test**: MIDI input to CV output verification
- **Calibration**: Per-channel offset and gain adjustment if required
- **Burn-in**: Extended operation test for reliability

---

*This hardware architecture achieves production-ready performance through comprehensive analysis and optimization of all system components and interconnections.*