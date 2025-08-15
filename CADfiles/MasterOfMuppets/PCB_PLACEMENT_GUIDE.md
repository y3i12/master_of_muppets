# Master of Muppets PCB Component Placement Guide

## Overview
This guide provides optimal component placement for the Master of Muppets 16-channel MIDI-to-CV converter to ensure signal integrity, minimize noise, and maintain stable DAC/OpAmp operation.

## PCB Dimensions
- **Recommended Size**: 100mm × 80mm (standard Eurorack depth)
- **Layers**: 2-layer PCB minimum, 4-layer preferred for better ground plane

## Critical Design Principles

### 1. Signal Flow Organization
Components should follow the signal path:
```
[Power Input] → [Regulators] → [Teensy] → [DACs] → [OpAmps] → [Output Jacks]
```

### 2. Zone Separation
Divide the PCB into three zones:
- **Power Zone** (left side): Power input, regulators, bulk capacitors
- **Digital Zone** (center-left): Teensy, DACs, I2C routing
- **Analog Zone** (center-right to right): OpAmps, output conditioning, jacks

## Component Placement Map

```
+--------------------------------------------------------------------------------+
|  POWER ZONE    |    DIGITAL ZONE        |    ANALOG ZONE                      |
|                |                        |                                      |
| [Terminal]     | [Teensy 4.1]          | [TL074 #1] → [Jack 1-4]             |
| [+12V Reg]     |    ↓                  | [TL074 #2] → [Jack 5-8]             |
| [-12V Reg]     | [DAC1] [DAC2]         | [TL074 #3] → [Jack 9-12]            |
| [+5V Reg]      |  (AD5593R)            | [TL074 #4] → [Jack 13-16]           |
| [Bulk Caps]    |                        |                                      |
+--------------------------------------------------------------------------------+
```

## Detailed Placement Instructions

### Step 1: Place Power Components (Left Edge)
1. **Terminal Block** (J1): Top-left corner, 5mm from edge
2. **Voltage Regulators**: 
   - Place TO-220 packages vertically along left edge
   - Keep 10mm spacing between regulators for heat dissipation
   - Orient heatsink tabs towards board edge if using heatsinks
3. **Bulk Capacitors**: Place close to regulator outputs

### Step 2: Place Teensy 4.1 (Center-Left)
- **Position**: Center of board, 25mm from left edge
- **Orientation**: USB connector facing left (towards power section)
- **Clearance**: Leave 5mm clearance around Teensy for routing
- **Critical**: Keep I2C pins (18, 19 for Wire, 16, 17 for Wire1) facing DACs

### Step 3: Place AD5593R DACs (Center)
- **DAC1**: Place 10mm right of Teensy, centered vertically
- **DAC2**: Place 10mm below DAC1
- **Orientation**: Pin 1 facing left (towards Teensy)
- **Critical Placement Rules**:
  - Maximum 30mm trace length from Teensy I2C pins
  - Keep DACs away from power regulators (minimum 15mm)
  - Place on same side of board as Teensy

### Step 4: Place TL074 OpAmps (Center-Right)
- **Arrangement**: 2×2 grid pattern
  - TL074 #1 (Ch 1-4): Top-left of grid
  - TL074 #2 (Ch 5-8): Top-right of grid  
  - TL074 #3 (Ch 9-12): Bottom-left of grid
  - TL074 #4 (Ch 13-16): Bottom-right of grid
- **Spacing**: 15mm between ICs for routing space
- **Orientation**: All ICs with pin 1 facing same direction (left)

### Step 5: Place Output Jacks (Right Edge)
- **Arrangement**: 4×4 grid or 2×8 columns
- **Spacing**: Standard Eurorack 5.08mm (0.2") HP spacing
- **Order**: Sequential channels 1-16 from top to bottom
- **Distance**: 5mm from right board edge

### Step 6: Place Passive Components

#### Decoupling Capacitors (CRITICAL for stability)
Place these AS CLOSE AS POSSIBLE to IC power pins:

**For each AD5593R:**
- 100nF ceramic (C0603) between VDD (pin 15) and GND (pin 14)
- Place within 3mm of pins, preferably on same layer

**For each TL074:**
- 100nF ceramic (C0603) between V+ (pin 4) and V- (pin 11)
- Place directly adjacent to IC, under 5mm trace length

**For Teensy:**
- 100nF ceramic near 3.3V pin
- 10µF ceramic near VIN pin

#### Pull-up Resistors (I2C)
- Place 4.7kΩ pull-ups near DAC1
- Route from SDA/SCL to 3.3V with minimal trace length
- Keep away from switching noise sources

#### Feedback Resistors (OpAmp gain)
- Place gain-setting resistors within 10mm of OpAmp
- Use symmetrical placement for each channel
- Keep analog traces short and direct

## Routing Guidelines

### Power Routing
1. **Ground Plane**: Use bottom layer as continuous ground plane
2. **Power Traces**:
   - +12V: 0.5mm minimum width
   - -12V: 0.5mm minimum width  
   - +5V: 0.8mm minimum width
   - GND: 1.0mm minimum, prefer ground plane

### I2C Routing
1. Keep SDA/SCL traces parallel and equal length
2. Maximum trace length: 50mm
3. Keep away from power traces (minimum 3mm spacing)
4. Add ground guard trace if possible

### Analog Signal Routing
1. Keep DAC output to OpAmp input traces SHORT (<20mm)
2. Route away from digital signals
3. Use 0.25mm traces for signals
4. Avoid routing under Teensy or near switching regulators

## Critical Checklist

### For DAC Stability:
- [ ] Decoupling cap within 3mm of each DAC power pins
- [ ] I2C pull-ups placed near DACs
- [ ] I2C traces under 50mm length
- [ ] DACs placed away from switching noise
- [ ] Solid ground plane under DACs

### For OpAmp Stability:
- [ ] Decoupling cap directly adjacent to each OpAmp
- [ ] Feedback resistors within 10mm of OpAmp
- [ ] No digital signals crossing under OpAmps
- [ ] Power supply traces adequately sized
- [ ] Output traces routed away from inputs (prevent oscillation)

### General:
- [ ] Star ground point at power input
- [ ] Adequate thermal relief for voltage regulators
- [ ] Test points for +12V, -12V, +5V, GND
- [ ] Mounting holes in corners (3.2mm for M3 screws)

## Implementation Steps in KiCad

1. **Update PCB from Schematic** (F8):
   - This imports all footprints into PCB editor

2. **Set Grid**: 
   - Use 0.635mm (25 mil) for component placement
   - Use 0.127mm (5 mil) for trace routing

3. **Place Components**:
   - Select component with mouse
   - Press 'M' to move
   - Press 'R' to rotate
   - Follow the placement map above

4. **Lock Critical Components**:
   - After placing Teensy, DACs, and OpAmps, right-click → "Lock"
   - This prevents accidental movement

5. **Use Placement Arrays**:
   - For jacks: Place first jack, then Edit → "Create Array" for uniform spacing
   - For OpAmps: Align horizontally/vertically using alignment tools

## Tips for Manual Placement

1. **Start with mechanical constraints**: Jacks, mounting holes, connectors
2. **Place high-speed/sensitive components next**: DACs and OpAmps
3. **Place support components last**: Resistors, capacitors
4. **Use 3D viewer** (Alt+3) to check component clearances
5. **Run DRC frequently** to catch issues early

## Expected Outcome

Following this guide will result in:
- Stable DAC operation with minimal I2C errors
- Low-noise OpAmp operation without oscillation
- Clean 0-10V CV outputs
- Efficient assembly and debugging
- Professional appearance

Remember: Good placement is 50% of good PCB design. Take time to get it right before routing!