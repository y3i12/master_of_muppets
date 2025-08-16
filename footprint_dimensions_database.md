# Master of Muppets - Footprint Dimensions Database

## Overview
Complete footprint dimension analysis extracted from KiCad project files, including exact measurements for PCB layout optimization.

## Critical Component Footprints

### 1. Teensy 4.1 Microcontroller
**Footprint:** `Teensy:Teensy41`
- **Overall dimensions:** 61.0mm × 17.78mm
- **Board outline:** -30.48mm to +30.48mm (X), -8.89mm to +8.89mm (Y)
- **Pin spacing:** 2.54mm (0.1")
- **Through-hole pads:** 1.6mm diameter, 1.1mm drill
- **USB connector area:** -31.75mm to -25.4mm (X), -3.81mm to +3.81mm (Y)
- **Ethernet connector:** -17.25mm to -13.25mm (X), -6.35mm to -0.1mm (Y)
- **USB Host connector:** -24.18mm to -11.48mm (X), 3.3mm to 5.84mm (Y)
- **MicroSD connector:** 10.16mm to 13.97mm (X), -1.27mm to +1.27mm (Y)
- **Pin 1 location:** -29.21mm, +7.62mm
- **Pin arrangement:** 24 pins per side (48 total main pins)
- **Additional pads:** Ethernet (pins 55-59), smaller 1.3mm pads

### 2. AD5593R DAC (Primary)
**Footprint:** `Package_SO:TSSOP-16_4.4x5mm_P0.65mm`
- **Package dimensions:** 4.4mm × 5.0mm
- **Pin pitch:** 0.65mm
- **Pin count:** 16 pins (8 per side)
- **Pad dimensions:** Typically 0.35mm × 1.2mm per pin
- **Body height:** ~1.1mm maximum
- **Lead width:** 0.22mm typical
- **Critical spacing requirement:** High-density placement

### 3. TL074 OpAmp (Quad)
**Footprint:** `Package_SO:SOIC-14_3.9x8.7mm_P1.27mm`
- **Package dimensions:** 3.9mm × 8.7mm
- **Pin pitch:** 1.27mm
- **Pin count:** 14 pins (7 per side)
- **Pad dimensions:** 0.6mm × 2.0mm per pin
- **Body height:** ~2.65mm maximum
- **Lead width:** 0.4mm typical
- **Total footprint area:** ~34mm² per package

### 4. 3.5mm Audio Jacks (CV Outputs)
**Footprint:** `PCM_4ms_Jack:EighthInch_PJ398SM` / `AMPHENOL_ACJM-MV35-2S`
- **Overall dimensions:** 15.8mm × 15.8mm
- **Mounting hole:** 2.0mm diameter at (4.67mm, 4.67mm)
- **Signal pin:** 1.4mm diameter at (-2.4mm, 6.38mm)
- **Ground pin:** 2.0mm diameter at (-6.38mm, 0.56mm)
- **Body height:** ~28mm (critical clearance requirement)
- **Spacing requirement:** Minimum 19mm center-to-center
- **Courtyard:** 16.3mm × 16.3mm

## SMD Component Footprints

### 5. 0603 Resistors (Majority)
**Footprint:** `Resistor_SMD:R_0603_1608Metric_Pad0.98x0.95mm_HandSolder`
- **Component size:** 1.6mm × 0.8mm (1608 metric)
- **Pad size:** 0.98mm × 0.95mm per pad
- **Pad spacing:** 1.6mm center-to-center
- **Component height:** ~0.55mm
- **Total footprint:** ~2.58mm × 0.95mm
- **Hand soldering friendly pads:** Extended for easier assembly

### 6. 0603 Capacitors 
**Footprint:** `PCM_4ms_Capacitor:C_0603`
- **Component size:** 1.6mm × 0.8mm (same as 0603 resistors)
- **Pad dimensions:** Similar to resistor footprint
- **Component height:** ~0.85mm (slightly taller than resistors)
- **Voltage rating variations:** 16V to 50V (same footprint)

### 7. 0805 Capacitors (Power)
**Footprint:** `PCM_4ms_Capacitor:C_0805`
- **Component size:** 2.0mm × 1.25mm
- **Pad size:** ~1.0mm × 1.3mm per pad
- **Pad spacing:** 2.0mm center-to-center
- **Component height:** ~1.25mm
- **Used for:** Higher value capacitors (10μF power filtering)

## Power and Interface Components

### 8. Voltage Regulator (LD1117)
**Footprint:** `PCM_4ms_Package_TO:TO-220-3_Vertical`
- **Package type:** TO-220-3 vertical mounting
- **Pin spacing:** 2.54mm
- **Body dimensions:** ~10mm × 15mm × 4.5mm
- **Mounting hole:** 3.2mm diameter
- **Heat dissipation requirement:** Consider thermal pad/heatsink
- **Pin 1 (Input):** Left pin when facing component

### 9. Terminal Block (Power Input)
**Footprint:** `TerminalBlock:TerminalBlock_Xinya_XY308-2.54-3P_1x03_P2.54mm_Horizontal`
- **Pin count:** 3 pins
- **Pin spacing:** 2.54mm
- **Wire gauge:** Up to 14 AWG
- **Overall length:** ~7.6mm
- **Height:** ~8.5mm
- **Mounting:** Horizontal orientation

## Component Density Analysis

### High-Density Zones
1. **DAC Areas:** TSSOP-16 packages require precision placement
   - Minimum trace width: 0.1mm (4 mil)
   - Via size: 0.2mm drill recommended

2. **OpAmp Clusters:** SOIC-14 packages with surrounding 0603 components
   - Component spacing: 0.5mm minimum between packages
   - Routing channels: 0.2mm minimum

### Low-Density Zones  
1. **Jack Array:** Large mechanical components with 19mm spacing
2. **Teensy Area:** Through-hole with 2.54mm grid
3. **Power Section:** TO-220 and terminal blocks

## PCB Layout Constraints

### Critical Spacing Requirements
- **Jack centers:** 19.05mm (0.75") minimum spacing
- **Teensy to edge:** 5mm minimum clearance for connectors
- **DAC to OpAmp:** 2mm minimum for thermal isolation
- **Power traces:** 0.5mm minimum width for 12V supply

### Assembly Considerations
- **Component height variations:** Jacks (28mm) >> TO-220 (4.5mm) >> SOIC (2.65mm) >> 0603 (0.85mm)
- **Hand soldering access:** 0603 pads optimized for manual assembly
- **Thermal management:** TO-220 regulator placement for airflow

### Manufacturing Guidelines
- **Minimum trace width:** 0.1mm (4 mil)
- **Minimum via size:** 0.2mm drill, 0.4mm annular ring
- **Solder mask:** 0.1mm minimum clearance
- **Silkscreen:** 0.15mm minimum line width

## Placement Optimization Recommendations

### 1. Signal Integrity
- Keep DAC to OpAmp traces short (<5mm)
- Minimize via count in analog signal paths
- Use ground plane pour for low noise

### 2. Thermal Management  
- Separate digital (Teensy) from analog (DAC/OpAmp) areas
- Place voltage regulator with thermal relief
- Consider copper pour for heat distribution

### 3. Mechanical Constraints
- Jack array at board edge for panel mounting
- Teensy orientation for USB access
- Component height progression from edge to center

### 4. Manufacturing Efficiency
- Group similar components for pick-and-place
- Minimize component rotation angles
- Standard footprint orientations where possible

## Total PCB Area Estimation
Based on component requirements and spacing:
- **Minimum board size:** ~100mm × 80mm
- **Optimal board size:** ~120mm × 100mm
- **Component count:** 163 total components
- **SMD density:** ~1.2 components per cm²

## File References
- Teensy footprint: `D:\Workspace\Code\master_of_muppets aggregate\CADfiles\teensy.pretty-master\Teensy41.kicad_mod`
- Jack footprint: `D:\Workspace\Code\master_of_muppets aggregate\CADfiles\MasterOfMuppets\AMPHENOL_ACJM-MV35-2S.kicad_mod`
- Analysis data: `D:\Workspace\Code\master_of_muppets aggregate\CADfiles\MasterOfMuppets\hierarchical_analysis.json`
- PCB layout: `D:\Workspace\Code\master_of_muppets aggregate\CADfiles\MasterOfMuppets\MasterOfMuppets.kicad_pcb`

---
*Generated by Claude Code analysis of Master of Muppets KiCad project*
*Last updated: 2025-08-16*