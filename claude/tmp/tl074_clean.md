TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072,](https://www.ti.com/product/TL072) [TL072A](https://www.ti.com/product/TL072A), [TL072B,](https://www.ti.com/product/TL072B) [TL072H](https://www.ti.com/product/TL072H), [TL072M](https://www.ti.com/product/TL072M) [TL074,](https://www.ti.com/product/TL074) [TL074A](https://www.ti.com/product/TL074A), [TL074B,](https://www.ti.com/product/TL074B) [TL074H](https://www.ti.com/product/TL074H), [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023
# **TL07xx Low-Noise FET-Input Operational Amplifiers**
#### **1 Features**
- High slew rate: 20 V/μs (TL07xH, typ)
- Low offset voltage: 1 mV (TL07xH, typ)
- Low offset voltage drift: 2 μV/°C
- Low power consumption: 940 μA/ch (TL07xH, typ)
- Wide common-mode and differential voltage ranges
  - Common-mode input voltage range includes VCC+
- Low input bias and offset currents
- Low noise:
- Vn = 18 nV/√Hz (typ) at f = 1 kHz
- Output short-circuit protection
- Low total harmonic distortion: 0.003% (typ)
- Wide supply voltage: ±2.25 V to ±20 V, 4.5 V to 40 V
## **2 Applications**
- [Solar energy: string and central inverter](https://www.ti.com/solution/string-inverter)
- [Motor drives: AC and servo drive control and](https://www.ti.com/applications/industrial/motor-drives/overview.html)  [power stage modules](https://www.ti.com/applications/industrial/motor-drives/overview.html)
- [Single phase online UPS](https://www.ti.com/solution/single-phase-offline-ups)
- [Three phase UPS](https://www.ti.com/solution/three-phase-ups)
- [Pro audio mixers](https://www.ti.com/solution/professional-audio-mixer-control-surface)
- [Battery test equipment](https://www.ti.com/solution/battery-test)
## **3 Description**
The TL07xH (TL071H, TL072H, and TL074H) family of devices are the next-generation versions of the industry-standard TL07x (TL071, TL072, and TL074) devices. These devices provide outstanding value for cost-sensitive applications, with features including low offset (1 mV, typical), high slew rate (20 V/μs), and common-mode input to the positive supply. High ESD
(1.5 kV, HBM), integrated EMI and RF filters, and operation across the full –40°C to 125°C enable the TL07xH devices to be used in the most rugged and demanding applications.
|                | Package Information |                    |
|----------------|---------------------|--------------------|
| PART NUMBER(1) | PACKAGE             | BODY SIZE (NOM)    |
|                | P (PDIP, 8)         | 9.59 mm × 6.35 mm  |
|                | DCK (SC70, 5)       | 2.00 mm × 1.25 mm  |
| TL071x         | PS (SO, 8)          | 6.20 mm × 5.30 mm  |
|                | D (SOIC, 8)         | 4.90 mm × 3.90 mm  |
|                | DBV (SOT-23, 5)     | 1.60 mm × 1.20 mm  |
|                | P (PDIP, 8)         | 9.59 mm × 6.35 mm  |
|                | PS (SO, 8)          | 6.20 mm × 5.30 mm  |
| TL072x         | D (SOIC, 8)         | 4.90 mm × 3.90 mm  |
|                | P (SOT-23, 8)       | 2.90 mm × 1.60 mm  |
|                | PW (TSSOP, 8)       | 4.40 mm × 3.00 mm  |
|                | JG (CDIP , 8)       | 9.59 mm × 6.67 mm  |
| TL072M         | W (CFP, 10)         | 6.12 mm × 3.56 mm  |
|                | FK (LCCC, 20)       | 8.89 mm × 8.89 mm  |
|                | N (PDIP, 14)        | 19.30 mm × 6.35 mm |
|                | NS (SO, 14)         | 10.30 mm × 5.30 mm |
|                | D (SOIC, 14)        | 8.65 mm × 3.91 mm  |
| TL074x         | DYY (SOT-23, 14)    | 4.20 mm × 2.00 mm  |
|                | DB (SSOP, 14)       | 6.20 mm × 5.30 mm  |
|                | PW (TSSOP, 14)      | 5.00 mm × 4.40 mm  |
|                | J (CDIP, 14)        | 19.56 mm × 6.92 mm |
| TL074M         | W (CFP, 14)         | 9.21 mm × 6.29 mm  |
|                | FK (LCCC, 20)       | 8.89 mm × 8.89 mm  |
(1) For all available packages, see the orderable addendum at the end of the data sheet.
**OFFSET N2** Copyright © 2017, Texas Instruments Incorporated
**Logic Symbols**
## **Table of Contents**
| 1 Features1                                      |  |
|--------------------------------------------------|--|
| 2 Applications1                                  |  |
| 3 Description1                                   |  |
| 4 Revision History 2                             |  |
| 5 Pin Configuration and Functions5               |  |
| 6 Specifications 12                              |  |
| 6.1 Absolute Maximum Ratings 12                  |  |
| 6.2 ESD Ratings 12                               |  |
| 6.3 Recommended Operating Conditions12           |  |
| 6.4 Thermal Information for Single Channel 13    |  |
| 6.5 Thermal Information for Dual Channel13       |  |
| 6.6 Thermal Information for Quad Channel 14      |  |
| 6.7 Electrical Characteristics: TL07xH15         |  |
| 6.8 Electrical Characteristics (DC): TL07xC,     |  |
| TL07xAC, TL07xBC, TL07xI, TL07xM 17              |  |
| 6.9 Electrical Characteristics (AC): TL07xC,     |  |
| TL07xAC, TL07xBC, TL07xI, TL07xM 19              |  |
| 6.10 Typical Characteristics: TL07xH 20          |  |
| 6.11 Typical Characteristics: All Devices Except |  |
| TL07xH27                                         |  |
| 7 Parameter Measurement Information31            |  |
| 8 Detailed Description32                               |  |
|--------------------------------------------------------|--|
| 8.1 Overview32                                         |  |
| 8.2 Functional Block Diagram32                         |  |
| 8.3 Feature Description32                              |  |
| 8.4 Device Functional Modes32                          |  |
| 9 Application and Implementation33                     |  |
| 9.1 Application Information 33                         |  |
| 9.2 Typical Application 33                             |  |
| 9.3 Unity Gain Buffer34                                |  |
| 9.4 System Examples 35                                 |  |
| 9.5 Power Supply Recommendations36                     |  |
| 9.6 Layout 36                                          |  |
| 10 Device and Documentation Support38                  |  |
| 10.1 Receiving Notification of Documentation Updates38 |  |
| 10.2 Support Resources 38                              |  |
| 10.3 Trademarks38                                      |  |
| 10.4 Electrostatic Discharge Caution38                 |  |
| 10.5 Glossary38                                        |  |
| 11 Mechanical, Packaging, and Orderable                |  |
| Information 38                                         |  |
|                                                        |  |
#### **4 Revision History**
NOTE: Page numbers for previous revisions may differ from page numbers in the current version.
| Changes from Revision U (December 2022) to Revision V (April 2023) |                                                                                                                                                                                                                                                                  | Page |  |
|--------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------|--|
| •                                                                  | Updated Overview, Functional Block Diagram, and Feature Description sections 32                                                                                                                                                                                  |      |  |
|                                                                    | Changes from Revision T (December 2021) to Revision U (December 2022)                                                                                                                                                                                            | Page |  |
| •<br>•                                                             | Changed Absolute Maximum Ratings, ESD Ratings, Recommended Operating Conditions, and Thermal<br>Information sections by merging TL07xH and TL07xx specifications12<br>Changed Electrical Characteristics tables by merging TL07xC, TL07xAC, TL07xBC, TL07xI, and |      |  |
| •                                                                  | TL07xM specifications17<br>Changed gain bandwidth value of all non-NS/non-PS packages and non-TL07xM devices from 3 MHz to 5.25<br>MHz                                                                                                                           | 17   |  |
| •                                                                  | Changed TL07xC, TL07xAC, TL07xBC, TL07xI, and TL07xM Switching Characteristics tables by renaming<br>to Electrical Characteristics (AC)<br>19                                                                                                                    |      |  |
| •                                                                  | Changed input voltage noise density at 1 kHz for all non-PS/non-NS packages and all non-TL07xM devices<br>to 37 nV/√Hz<br>19                                                                                                                                     |      |  |
| •                                                                  | Changed THD+N for all non-PS/non-NS packages and all non-TL07xM devices to 0.00012%19                                                                                                                                                                            |      |  |
|                                                                    | Changes from Revision S (July 2021) to Revision T (December 2021)                                                                                                                                                                                                | Page |  |
| •                                                                  | Corrected DCK pinout diagram and table in Pin Configurations and Functions section5                                                                                                                                                                              |      |  |
#### **Changes from Revision R (June 2021) to Revision S (July 2021) Page**
• Deleted preview note from TL071H SOIC (8), SOT-23 (5) and SC70 (5) packages throughout the data sheet[1](#page-0-0)
|   | Changes from Revision Q (June 2021) to Revision R (June 2021)                                    | Page |
|---|--------------------------------------------------------------------------------------------------|------|
| • | Deleted preview note from TL072H SOIC (8), SOT-23 (8) and TSSOP (8) packages throughout the data |      |
sheet...................................................................................................................................................................[1](#page-0-0)
2 *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* Copyright © 2023 Texas Instruments Incorporated
| • | Added ESD information for TL072H12 |  |
|---|------------------------------------|--|
| • | Added IQ spec for TL072H15         |  |
|   | Changes from Revision P (November 2020) to Revision Q (June 2021)                                   |    |  |
|---|-----------------------------------------------------------------------------------------------------|----|--|
| • | Deleted VSSOP (8) package from the Device Information section1                                      |    |  |
| • | Added DBV, DCK, and D Package,s to TL071H in Pin Configuration and Functions section5               |    |  |
| • | Deleted DGK Package, from TL072x in Pin Configuration and Functions section5                        |    |  |
| • | Deleted tables with duplicate information from the Specifications section                           | 12 |  |
| • | Added D, DCK, and DBV package thermal information in Thermal Information for Single Channel: TL071H |    |  |
|   | section                                                                                             | 13 |  |
| • | Added D, DDF, and PW package thermal information in Thermal Information for Dual Channel: TL072H    |    |  |
|   | section                                                                                             | 13 |  |
| • | Added IB and IOS specification for single channel DCK and DBV package                               | 15 |  |
| • | Added IQ spec for TL071H15                                                                          |    |  |
| • | Deleted Related Links section from the Device and Documentation Support section38                   |    |  |
|   | Changes from Revision O (October 2020) to Revision P (November 2020)                             | Page |
|---|--------------------------------------------------------------------------------------------------|------|
| • | Added SOIC and TSSOP package thermal information in Thermal Information for Quad Channel: TL074H |      |
|   | section<br>                                                                                      | 14   |
| • | Added Typical Characteristics:TL07xH section in Specifications section20                         |      |
|   | Changes from Revision N (July 2017) to Revision O (October 2020)                                      | Page |
|---|-------------------------------------------------------------------------------------------------------|------|
| • | Updated the numbering format for tables, figures, and cross-references throughout the document        | 1    |
| • | Features of TL07xH added to the Features section1                                                     |      |
| • | Added link to applications in the Applications section1                                               |      |
| • | Added TL07xH in the Description section                                                               | 1    |
| • | Added TL07xH device in the Device Information section1                                                |      |
| • | Added SOT-23 (14), VSSOP (8), SOT-23 (8), SC70 (5), and SOT-23 (5) packages to the Device Information |      |
|   | section                                                                                               | 1    |
| • | Added TSSOP, VSSOP and DDF Package,s to TL072x in Pin Configuration and Functions section5            |      |
| • | Added DYY Package, to TL074x in Pin Configuration and Functions section5                              |      |
| • | Removed Table of Graphs from the Typical Characteistics section27                                     |      |
| • | Deleted reference to obsolete documentation in Layout Guidelines section36                            |      |
|   |                                                                                                       |      |
• Removed *Related Documentation* section....................................................................................................... [38](#page-37-0)
|   | Updated data sheet text to latest documentation and translation standards1                           |    |
|---|------------------------------------------------------------------------------------------------------|----|
| • |                                                                                                      |    |
| • | Added TL072M and TL074M devices to data sheet 1                                                      |    |
| • | Rewrote text in Description section 1                                                                |    |
| • | Changed TL07x 8-pin PDIP package to 8-pin CDIP package in Device Information table 1                 |    |
| • | Deleted 20-pin LCCC package from Device Information table 1                                          |    |
| • | Added 2017 copyright statement to front page schematic                                               | 1  |
| • | Deleted TL071x FK (LCCC) pinout drawing and pinout table in Pin Configurations and Functions section | 5  |
| • | Updated pinout diagrams and pinout tables in Pin Configurations and Functions section 5              |    |
| • | Added Figure 6-59 to Typical Characteristics section27                                               |    |
| • | Added second Typical Application section application curves 34                                       |    |
| • | Changed document references in Layout Guidelines section                                             | 36 |
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 3
| Changes from Revision L (February 2014) to Revision M (February 2014) |                                                                                                                                                                                                                                                       |  |  |
|-----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| •                                                                     | Added Device Information table, Pin Configuration and Functions section, ESD Ratings table, Feature<br>Description section, Device Functional Modes, Application and Implementation section, Power Supply<br>Recommendations section, Layout section1 |  |  |
### **5 Pin Configuration and Functions**
**8-Pin SOIC (Top View)** 
|  | Table 5-1. Pin Functions: TL071H |  |
|--|----------------------------------|--|
|  |                                  |  |
| PIN  |     |     |   |     |                    |
|------|-----|-----|---|-----|--------------------|
| NAME | DBV | DCK | D | I/O | DESCRIPTION        |
| IN–  | 4   | 3   | 2 | I   | Inverting input    |
| IN+  | 3   | 1   | 3 | I   | Noninverting input |
| NC   | —   | —   | 8 | —   | Do not connect     |
| NC   | —   | —   | 1 | —   | Do not connect     |
| NC   | —   | —   | 5 | —   | Do not connect     |
| OUT  | 1   | 4   | 6 | O   | Output             |
| VCC– | 2   | 2   | 4 | —   | Power supply       |
| VCC+ | 5   | 5   | 7 | —   | Power supply       |
#### TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072](https://www.ti.com/product/TL072), [TL072A,](https://www.ti.com/product/TL072A) [TL072B](https://www.ti.com/product/TL072B), [TL072H,](https://www.ti.com/product/TL072H) [TL072M](https://www.ti.com/product/TL072M) [TL074](https://www.ti.com/product/TL074), [TL074A,](https://www.ti.com/product/TL074A) [TL074B](https://www.ti.com/product/TL074B), [TL074H,](https://www.ti.com/product/TL074H) [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023 **[www.ti.com](https://www.ti.com)**
NC- no internal connection
#### **Figure 5-4. TL071x D, P, and PS Package, 8-Pin SOIC, PDIP, and SO (Top View)**
#### **Table 5-2. Pin Functions: TL071x**
| PIN       |     |     |                         |  |
|-----------|-----|-----|-------------------------|--|
| NAME      | NO. | I/O | DESCRIPTION             |  |
| IN–       | 2   | I   | Inverting input         |  |
| IN+       | 3   | I   | Noninverting input      |  |
| NC        | 8   | —   | Do not connect          |  |
| OFFSET N1 | 1   | —   | Input offset adjustment |  |
| OFFSET N2 | 5   | —   | Input offset adjustment |  |
| OUT       | 6   | O   | Output                  |  |
| VCC–      | 4   | —   | Power supply            |  |
| VCC+      | 7   | —   | Power supply            |  |
6 *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* Copyright © 2023 Texas Instruments Incorporated
#### **Figure 5-5. TL072x D, DDF, JG, P, PS, and PW Package, 8-Pin SOIC, SOT-23, CDIP, PDIP, SO, and TSSOP (Top View)**
#### **Table 5-3. Pin Functions: TL072x**
| PIN  |     |     |                    |
|------|-----|-----|--------------------|
| NAME | NO. | I/O | DESCRIPTION        |
| 1IN– | 2   | I   | Inverting input    |
| 1IN+ | 3   | I   | Noninverting input |
| 1OUT | 1   | O   | Output             |
| 2IN– | 6   | I   | Inverting input    |
| 2IN+ | 5   | I   | Noninverting input |
| 2OUT | 7   | O   | Output             |
| VCC– | 4   | —   | Power supply       |
| VCC+ | 8   | —   | Power supply       |
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 7
#### TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072](https://www.ti.com/product/TL072), [TL072A,](https://www.ti.com/product/TL072A) [TL072B](https://www.ti.com/product/TL072B), [TL072H,](https://www.ti.com/product/TL072H) [TL072M](https://www.ti.com/product/TL072M) [TL074](https://www.ti.com/product/TL074), [TL074A,](https://www.ti.com/product/TL074A) [TL074B](https://www.ti.com/product/TL074B), [TL074H,](https://www.ti.com/product/TL074H) [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023 **[www.ti.com](https://www.ti.com)**
NC- no internal connection
#### **Figure 5-6. TL072x U Package, 10-Pin CFP (Top View)**
#### **Table 5-4. Pin Functions: TL072x**
| PIN  |       |     |                    |  |
|------|-------|-----|--------------------|--|
| NAME | NO.   | I/O | DESCRIPTION        |  |
| 1IN– | 3     | I   | Inverting input    |  |
| 1IN+ | 4     | I   | Noninverting input |  |
| 1OUT | 2     | O   | Output             |  |
| 2IN– | 7     | I   | Inverting input    |  |
| 2IN+ | 6     | I   | Noninverting input |  |
| 2OUT | 8     | O   | Output             |  |
| NC   | 1, 10 | —   | Do not connect     |  |
| VCC– | 5     | —   | Power supply       |  |
| VCC+ | 9     | —   | Power supply       |  |
NC- no internal connection
#### **Figure 5-7. TL072 FK Package, 20-Pin LCCC (Top View)**
#### **Table 5-5. Pin Functions: TL072x**
| PIN  |                                                |     |                    |  |
|------|------------------------------------------------|-----|--------------------|--|
| NAME | NO.                                            | I/O | DESCRIPTION        |  |
| 1IN– | 5                                              | I   | Inverting input    |  |
| 1IN+ | 7                                              | I   | Noninverting input |  |
| 1OUT | 2                                              | O   | Output             |  |
| 2IN– | 15                                             | I   | Inverting input    |  |
| 2IN+ | 12                                             | I   | Noninverting input |  |
| 2OUT | 17                                             | O   | Output             |  |
| NC   | 1, 3, 4, 6, 8,<br>9, 11, 13, 14,<br>16, 18, 19 | —   | Do not connect     |  |
| VCC– | 10                                             | —   | Power supply       |  |
| VCC+ | 20                                             | —   | Power supply       |  |
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 9
#### **Figure 5-8. TL074x D, N, NS, PW, J, DYY, and W Package, 14-Pin SOIC, PDIP, SO, TSSOP, CDIP, SOT-23, and CFP (Top View)**
|  | Table 5-6. Pin Functions: TL074x |  |
|--|----------------------------------|--|
|  |                                  |  |
| PIN  |     |     |                    |  |  |
|------|-----|-----|--------------------|--|--|
| NAME | NO. | I/O | DESCRIPTION        |  |  |
| 1IN– | 2   | I   | Inverting input    |  |  |
| 1IN+ | 3   | I   | Noninverting input |  |  |
| 1OUT | 1   | O   | Output             |  |  |
| 2IN– | 6   | I   | Inverting input    |  |  |
| 2IN+ | 5   | I   | Noninverting input |  |  |
| 2OUT | 7   | O   | Output             |  |  |
| 3IN– | 9   | I   | Inverting input    |  |  |
| 3IN+ | 10  | I   | Noninverting input |  |  |
| 3OUT | 8   | O   | Output             |  |  |
| 4IN– | 13  | I   | Inverting input    |  |  |
| 4IN+ | 12  | I   | Noninverting input |  |  |
| 4OUT | 14  | O   | Output             |  |  |
| VCC– | 11  | —   | Power supply       |  |  |
| VCC+ | 4   | —   | Power supply       |  |  |
NC- no internal connection
#### Figure 5-9. TL074 FK Package, 20-Pin LCCC (Top View)
#### Table 5-7. Pin Functions: TL074x
| PIN    |                        | I/O | DESCRIPTION        |  |  |  |
|--------|------------------------|-----|--------------------|--|--|--|
| NAME   | NO.                    |     |                    |  |  |  |
| 1IN-   | 3                      |     | Inverting input    |  |  |  |
| $1IN+$ | 4                      |     | Noninverting input |  |  |  |
| 10UT   | 2                      | О   | Output             |  |  |  |
| $2IN-$ | 9                      |     | Inverting input    |  |  |  |
| $2IN+$ | 8                      |     | Noninverting input |  |  |  |
| 2OUT   | 10                     | 0   | Output             |  |  |  |
| 3IN-   | 13                     |     | Inverting input    |  |  |  |
| $3IN+$ | 14                     |     | Noninverting input |  |  |  |
| 3OUT   | 12                     | О   | Output             |  |  |  |
| 4IN-   | 19                     |     | Inverting input    |  |  |  |
| $4IN+$ | 18                     |     | Noninverting input |  |  |  |
| 4OUT   | 20                     | 0   | Output             |  |  |  |
| NC     | 1, 5, 7, 11, 15,<br>17 |     | Do not connect     |  |  |  |
| VCC-   | 16                     |     | Power supply       |  |  |  |
| VCC+   | 6                      |     | Power supply       |  |  |  |
Copyright © 2023 Texas Instruments Incorporated
11 Submit Document Feedback
## **6 Specifications**
#### **6.1 Absolute Maximum Ratings**
over operating ambient temperature range (unless otherwise noted) (1)
|                                                              |                          |                                                   | MIN        | MAX        | UNIT |
|--------------------------------------------------------------|--------------------------|---------------------------------------------------|------------|------------|------|
| Supply voltage, VS = (V+) – (V–)                             |                          | All NS and PS packages; All TL07xM devices        | –0.3       | 36         | V    |
|                                                              |                          | All other devices                                 | 0          | 42         | V    |
|                                                              | Common-mode voltage (3)  | All NS and PS packages; All TL07xM devices        | (V–) – 0.3 | (V–) + 36  | V    |
|                                                              |                          | All other devices                                 | (V–) – 0.5 | (V+) + 0.5 | V    |
| Signal input pins                                            | Differential voltage (3) | All NS and PS packages; All TL07xM devices<br>(4) | (V–) – 0.3 | (V–) + 36  | V    |
|                                                              |                          | All other devices                                 |            | VS + 0.2   | V    |
|                                                              | Current (3)              | All NS and PS packages; All TL07xM devices        |            | 50         | mA   |
|                                                              |                          | All other devices                                 | –10        | 10         | mA   |
| Output short-circuit (2)                                     |                          |                                                   | Continuous |            |      |
| Operating ambient temperature, TA                            |                          |                                                   | –55        | 150        | °C   |
| Junction temperature, TJ                                     |                          |                                                   |            | 150        | °C   |
| Case temperature for 60 seconds - FK package                 |                          |                                                   |            | 260        | °C   |
| Lead temperature 1.8 mm (1/16 inch) from case for 10 seconds |                          |                                                   |            | 300        | °C   |
| Storage temperature, Tstg                                    |                          |                                                   | –65        | 150        | °C   |
(1) Stresses beyond those listed under *Absolute Maximum Ratings* may cause permanent damage to the device. These are stress ratings only, which do not imply functional operation of the device at these or any other conditions beyond those indicated under *Recommended Operating Conditions*. Exposure to absolute-maximum-rated conditions for extended periods may affect device reliability.
(2) Short-circuit to ground, one amplifier per package.
(3) Input pins are diode-clamped to the power-supply rails. Input signals that can swing more than 0.5 V beyond the supply rails must be current limited to 10 mA or less.
(4) Differential voltage only limited by input voltage.
### **6.2 ESD Ratings**
|        |                         |                                                                     | VALUE | UNIT |
|--------|-------------------------|---------------------------------------------------------------------|-------|------|
| V(ESD) | Electrostatic discharge | Human-body model (HBM), per ANSI/ESDA/JEDEC JS-001(1)               |       |      |
|        |                         | Charged-device model (CDM), per JEDEC specification JESD22-C101 (2) | ±1000 | V    |
(1) JEDEC document JEP155 states that 500-V HBM allows safe manufacturing with a standard ESD control process.
(2) JEDEC document JEP157 states that 250-V CDM allows safe manufacturing with a standard ESD control process.
## **6.3 Recommended Operating Conditions**
over operating ambient temperature range (unless otherwise noted)
|    |                             |                                                  | MIN      | MAX        | UNIT |
|----|-----------------------------|--------------------------------------------------|----------|------------|------|
| VS | Supply voltage, (V+) – (V–) | All NS and PS packages; All TL07xM<br>devices(1) | 10       | 30         | V    |
|    |                             | All other devices                                | 4.5      | 40         | V    |
| VI | Input voltage range         | All NS and PS packages; All TL07xM<br>devices    | (V–) + 2 | (V+) + 0.1 | V    |
|    |                             | All other devices                                | (V–) + 4 | (V+) + 0.1 | V    |
| TA |                             | TL07xM                                           | –55      | 125        | °C   |
|    | Specified temperature       | TL07xH                                           | –40      | 125        | °C   |
|    |                             | TL07xI                                           | –40      | 85         | °C   |
|    |                             | TL07xC                                           | 0        | 70         | °C   |
(1) V+ and V– are not required to be of equal magnitude, provided that the total VS (V+ – V–) is between 10 V and 30 V.
## 6.4 Thermal Information for Single Channel
| THERMAL METRIC (1)    |                                              | TL071xx     |               |                 |             |            |      |
|-----------------------|----------------------------------------------|-------------|---------------|-----------------|-------------|------------|------|
|                       |                                              | D<br>(SOIC) | DCK<br>(SC70) | DBV<br>(SOT-23) | D<br>(PDIP) | PS<br>(SO) | UNIT |
|                       |                                              | 8 PINS      | 5 PINS        | 5 PINS          | 8 PINS      | 8 PINS     |      |
| $R_{\theta JA}$       | Junction-to-ambient thermal resistance       | 158.8       | 217.5         | 212.2           | 85          | 95         | °C/W |
| $R_{\theta JC(top)}$  | Junction-to-case (top) thermal resistance    | 98.6        | 113.1         | 111.1           |             |            | °C/W |
| $R_{\theta J B}$      | Junction-to-board thermal resistance         | 102.3       | 63.8          | 79.4            |             |            | °C/W |
| $\Psi_{JT}$           | Junction-to-top characterization parameter   | 45.8        | 34.8          | 51.8            |             |            | °C/W |
| $\Psi_{JB}$           | Junction-to-board characterization parameter | 101.5       | 63.5          | 79.0            |             |            | °C/W |
| $R_{\theta JC (bot)}$ | Junction-to-case (bottom) thermal resistance | N/A         | N/A           | N/A             | N/A         | N/A        | °C/W |
(1) For more information about traditional and new thermal metrics, see the *Semiconductor and IC Package Thermal Metrics* application report, SPRA953.
#### 6.5 Thermal Information for Dual Channel
|                            |                                                    | TL072xx     |                 |              |              |             |            |               |            |      |  |
|----------------------------|----------------------------------------------------|-------------|-----------------|--------------|--------------|-------------|------------|---------------|------------|------|--|
| THERMAL METRIC (1)         |                                                    | D<br>(SOIC) | DDF<br>(SOT-23) | FK<br>(LCCC) | JG<br>(CDIP) | Ρ<br>(PDIP) | PS<br>(SO) | PW<br>(TSSOP) | u<br>(CFP) | UNIT |  |
|                            |                                                    | 8 PINS      | 8 PINS          | 20 PINS      | 8 PINS       | 8 PINS      | 8 PINS     | 8 PINS        | 10 PINS    |      |  |
| $R_{\theta JA}$            | Junction-to-ambient<br>thermal resistance          | 147.8       | 181.5           | -            | -            | 85          | 95         | 200.3         | 169.8      | °C/W |  |
| $R_{\theta JC(top)}$       | Junction-to-case (top)<br>thermal resistance       | 88.2        | 112.5           | 5.61         | 15.05        |             | $-$        | 89.4          | 62.1       | °C/W |  |
| $R_{\theta J B}$           | Junction-to-board<br>thermal resistance            | 91.4        | 98.2            | -            | -            |             | $-$        | 131.0         | 176.2      | °C/W |  |
| $\Psi_{JT}$                | Junction-to-top<br>characterization<br>parameter   | 36.8        | 17.2            | $-$          | $-$          |             | $-$        | 22.2          | 48.4       | °C/W |  |
| $\Psi_{JB}$                | Junction-to-board<br>characterization<br>parameter | 90.6        | 97.6            | -            | -            |             | -          | 129.3         | 144.1      | °C/W |  |
| $\mid R_{\theta JC (bot)}$ | Junction-to-case<br>(bottom) thermal<br>resistance | N/A         | N/A             | -            | -            |             |            | N/A           | 5.4        | °C/W |  |
(1) For more information about traditional and new thermal metrics, see the *Semiconductor and IC Package Thermal Metrics* application report, SPRA953.
Copyright © 2023 Texas Instruments Incorporated
13 Submit Document Feedback
#### **6.6 Thermal Information for Quad Channel**
|                           |                                                 | TL074xx     |                 |               |         |              |               |               |              |      |
|---------------------------|-------------------------------------------------|-------------|-----------------|---------------|---------|--------------|---------------|---------------|--------------|------|
|                           | THERMAL METRIC (1)                              | D<br>(SOIC) | DYY<br>(SOT-23) | FK<br>(TSSOP) | (TSSOP) | Ν<br>(TSSOP) | NS<br>(TSSOP) | PW<br>(TSSOP) | W<br>(TSSOP) | UNIT |
|                           |                                                 | 14 PINS     | 14 PINS         | 20 PINS       | 14 PINS | 14 PINS      | 14 PINS       | 14 PINS       | 14 PINS      |      |
| $R_{\theta JA}$           | Junction-to-ambient thermal<br>resistance       | 114.2       | 153.2           |               |         | 80           | 76            |               | 128.8        | °C/W |
| $R_{\theta}$<br>JC(top)   | Junction-to-case (top) thermal<br>resistance    | 70.3        | 88.7            | 5.61          | 14.5    |              |               | 14.5          | 56.1         | °C/W |
| $R_{\theta J B}$          | Junction-to-board thermal<br>resistance         | 70.2        | 65.4            |               |         |              |               |               | 127.6        | °C/W |
| ΨЈТ                       | Junction-to-top<br>characterization parameter   | 28.8        | 9.5             |               |         |              |               |               | 29           | °C/W |
| $\Psi_{JB}$               | Junction-to-board<br>characterization parameter | 69.8        | 65.0            |               |         |              |               |               | 106.1        | °C/W |
| $R_{\text{A}}$<br>JC(bot) | Junction-to-case (bottom)<br>thermal resistance | N/A         | N/A             |               |         |              |               |               | 0.5          | °C/W |
(1) For more information about traditional and new thermal metrics, see the Semiconductor and IC Package Thermal Metrics application report, SPRA953.
### **6.7 Electrical Characteristics: TL07xH**
For VS = (VCC+) – (VCC–) = 4.5 V to 40 V (±2.25 V to ±20 V) at T<sup>A</sup> = 25°C, RL = 10 kΩ connected to VS / 2, VCM = VS / 2, and V<sup>O</sup> UT = VS / 2, unless otherwise noted.
|                    | PARAMETER                            | TEST CONDITIONS                                                                |                                            | MIN          | TYP      | MAX    | UNIT     |
|--------------------|--------------------------------------|--------------------------------------------------------------------------------|--------------------------------------------|--------------|----------|--------|----------|
| OFFSET VOLTAGE     |                                      |                                                                                |                                            |              |          |        |          |
|                    |                                      |                                                                                |                                            |              | ±1       | ±4     |          |
| VOS                | Input offset voltage                 |                                                                                |                                            |              |          | ±5     | mV       |
| dVOS/dT            | Input offset voltage drift           |                                                                                | TA = –40°C to 125°C<br>TA = –40°C to 125°C |              | ±2       |        | µV/℃     |
|                    | Input offset voltage versus          | VS = 5 V to 40 V, VCM = VS /                                                   |                                            |              |          |        |          |
| PSRR               | power supply                         | 2                                                                              | TA = –40°C to 125°C                        |              | ±1       | ±10    | μV/V     |
|                    | Channel separation                   | f = 0 Hz                                                                       |                                            |              | 10       |        | µV/V     |
| INPUT BIAS CURRENT |                                      |                                                                                |                                            |              |          |        |          |
|                    |                                      |                                                                                |                                            |              | ±1       | ±120   | pA       |
| IB                 | Input bias current                   |                                                                                | DCK and DBV packages                       |              | ±1       | ±300   | pA       |
|                    |                                      |                                                                                | TA = –40°C to 125°C (1)                    |              |          | ±5     | nA       |
|                    |                                      |                                                                                |                                            |              | ±0.5     | ±120   | pA       |
| IOS                | Input offset current                 |                                                                                | DCK and DBV packages                       |              | ±0.5     | ±250   | pA       |
|                    |                                      |                                                                                | TA = –40°C to 125°C (1)                    |              |          | ±5     | nA       |
| NOISE              |                                      |                                                                                |                                            |              |          |        |          |
|                    |                                      | f = 0.1 Hz to 10 Hz                                                            |                                            |              | 9.2      |        | μVPP     |
| EN                 | Input voltage noise                  |                                                                                |                                            | 1.4          |          | µVRMS  |          |
|                    |                                      |                                                                                |                                            | 37           |          |        |          |
| eN                 | Input voltage noise density          | f = 10 kHz                                                                     |                                            |              | 21       |        | nV/√Hz   |
| iN                 | Input current noise                  | f = 1 kHz                                                                      |                                            | 80           |          | fA/√Hz |          |
|                    | INPUT VOLTAGE RANGE                  |                                                                                |                                            |              |          |        |          |
| VCM                | Common-mode voltage<br>range         |                                                                                |                                            | (VCC–) + 1.5 |          | (VCC+) | V        |
|                    |                                      | VS = 40 V, (VCC–) + 2.5 V <                                                    |                                            | 100          | 105      |        | dB       |
|                    | Common-mode rejection<br>ratio       | VCM < (VCC+) – 1.5 V                                                           | TA = –40°C to 125°C                        | 95           |          |        | dB       |
| CMRR               |                                      |                                                                                |                                            | 90           | 105      |        | dB       |
|                    |                                      | VS = 40 V, (VCC–) + 2.5 V <<br>VCM < (VCC+)                                    | TA = –40°C to 125°C                        | 80           |          |        | dB       |
| INPUT CAPACITANCE  |                                      |                                                                                |                                            |              |          |        |          |
| ZID                | Differential                         |                                                                                |                                            |              | 100    2 |        | MΩ    pF |
| ZICM               | Common-mode                          |                                                                                |                                            |              | 6    1   |        | TΩ    pF |
| OPEN-LOOP GAIN     |                                      |                                                                                |                                            |              |          |        |          |
|                    |                                      | VS = 40 V, VCM = VS / 2,                                                       |                                            |              |          |        |          |
| AOL                | Open-loop voltage gain               | (VCC–) + 0.3 V < VO < (VCC+)<br>– 0.3 V                                        | TA = –40°C to 125°C                        | 118          | 125      |        | dB       |
| AOL                | Open-loop voltage gain               | VS = 40 V, VCM = VS / 2, RL =<br>2 kΩ, (VCC–) + 1.2 V < VO <<br>(VCC+) – 1.2 V | TA = –40°C to 125°C                        | 115          | 120      |        | dB       |
|                    | FREQUENCY RESPONSE                   |                                                                                |                                            |              |          |        |          |
| GBW                | Gain-bandwidth product               |                                                                                |                                            |              | 5.25     |        | MHz      |
| SR                 | Slew rate                            | VS = 40 V, G = +1, CL = 20 pF                                                  |                                            |              | 20       |        | V/μs     |
|                    |                                      | To 0.1%, VS = 40 V, VSTEP = 10 V , G = +1, CL = 20 pF                          |                                            | 0.63         |          |        |          |
|                    | Settling time                        | To 0.1%, VS = 40 V, VSTEP = 2 V , G = +1, CL = 20 pF                           |                                            | 0.56         |          | μs     |          |
| tS                 |                                      | To 0.01%, VS = 40 V, VSTEP = 10 V , G = +1, CL = 20 pF                         |                                            |              | 0.91     |        |          |
|                    |                                      | To 0.01%, VS = 40 V, VSTEP = 2 V , G = +1, CL = 20 pF                          |                                            | 0.48         |          |        |          |
|                    | Phase margin                         | G = +1, RL = 10 kΩ, CL = 20 pF                                                 |                                            |              | 56       |        | °        |
|                    | Overload recovery time               | VIN × gain > VS                                                                |                                            |              | 300      |        | ns       |
| THD+N              | Total harmonic distortion +<br>noise | VS = 40 V, VO = 6 VRMS, G = +1, f = 1 kHz                                      |                                            |              | 0.00012  |        | %        |
| EMIRR              | EMI rejection ratio                  | f = 1 GHz                                                                      |                                            |              | 53       |        | dB       |
| OUTPUT             |                                      |                                                                                |                                            |              |          |        |          |
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 15
## **6.7 Electrical Characteristics: TL07xH (continued)**
For VS = (VCC+) – (VCC–) = 4.5 V to 40 V (±2.25 V to ±20 V) at TA = 25°C, RL = 10 kΩ connected to VS / 2, VCM = VS / 2, and V<sup>O</sup> UT = VS / 2, unless otherwise noted.
|                                   | PARAMETER                          |                                                  | TEST CONDITIONS       | MIN | TYP   | MAX  | UNIT |
|-----------------------------------|------------------------------------|--------------------------------------------------|-----------------------|-----|-------|------|------|
|                                   |                                    |                                                  | VS = 40 V, RL = 10 kΩ |     | 115   | 210  |      |
| Voltage output swing from<br>rail |                                    | Positive rail headroom                           | VS = 40 V, RL = 2 kΩ  |     | 520   | 965  |      |
|                                   |                                    | VS = 40 V, RL = 10 kΩ                            |                       | 105 | 215   | mV   |      |
|                                   |                                    | Negative rail headroom                           | VS = 40 V, RL = 2 kΩ  |     | 500   | 1030 |      |
| ISC                               | Short-circuit current              |                                                  |                       |     | ±26   |      | mA   |
| CLOAD                             | Capacitive load drive              |                                                  |                       |     | 300   |      | pF   |
| ZO                                | Open-loop output<br>impedance      | f = 1 MHz, IO = 0 A                              |                       | 125 |       | Ω    |      |
| POWER SUPPLY                      |                                    |                                                  |                       |     |       |      |      |
|                                   | Quiescent current per<br>amplifier | IO = 0 A                                         |                       |     | 937.5 | 1125 |      |
|                                   |                                    | IO = 0 A, (TL071H)                               |                       |     | 960   | 1156 |      |
| IQ                                |                                    | IO = 0 A                                         |                       |     |       | 1130 | µA   |
|                                   |                                    | IO = 0 A, (TL072H)                               | TA = –40°C to 125°C   |     |       | 1143 |      |
|                                   |                                    | IO = 0 A, (TL071H)                               |                       |     |       | 1160 |      |
|                                   | Turn-On Time                       | At TA = 25°C, VS = 40 V, VS ramp rate > 0.3 V/µs |                       | 60  |       | μs   |      |
(1) Max IB and Ios data is specified based on characterization results.
### 6.8 Electrical Characteristics (DC): TL07xC, TL07xAC, TL07xBC, TL07xI, TL07xM
|                           | PARAMETER                            |                                                             | For $V_S = (V_{CC+}) - (V_{CC-}) = \pm 15 \text{ V}$ at $T_A = 25^{\circ}\text{C}$ , unless otherwise noted<br>TEST CONDITIONS <sup>(1) (2)</sup> |                          | MIN      | TYP                | MAX | UNIT          |
|---------------------------|--------------------------------------|-------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------|----------|--------------------|-----|---------------|
|                           |                                      |                                                             |                                                                                                                                                   |                          |          |                    |     |               |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 3                  | 10  |               |
|                           |                                      |                                                             | TL07xC                                                                                                                                            | $T_A$ = Full range       |          |                    | 13  |               |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 3                  | 6   |               |
|                           |                                      |                                                             | TL07xAC                                                                                                                                           | $T_A$ = Full range       |          |                    | 7.5 |               |
| $\mathsf{V}_{\text{OS}}$  |                                      |                                                             |                                                                                                                                                   |                          |          | 2                  | 3   |               |
|                           |                                      |                                                             | TL07xBC                                                                                                                                           | $T_A$ = Full range       |          |                    | 5   |               |
|                           | Input offset voltage                 | $V_0 = 0 V$<br>$R_S = 50 \Omega$                            |                                                                                                                                                   |                          |          | 3                  | 6   | mV            |
|                           |                                      |                                                             | TL07xl                                                                                                                                            | $T_A$ = Full range       |          |                    | 8   |               |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 3                  | 6   |               |
|                           |                                      |                                                             | TL071M, TL072M                                                                                                                                    | $T_A$ = Full range       |          |                    | 9   |               |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 3                  | 9   |               |
|                           |                                      |                                                             | TL074M                                                                                                                                            | $T_A$ = Full range       |          |                    | 15  |               |
|                           | Input offset voltage                 |                                                             |                                                                                                                                                   |                          |          |                    |     |               |
| $\rm dV_{OS}/\rm dT$      | drift                                | $V_{O} = 0 \text{ V}, R_{S} = 50 \Omega$                    | $T_A$ = Full range                                                                                                                                |                          |          | $\pm 18$           |     | µV/°C         |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 5                  | 100 | рA            |
|                           |                                      | $V_0 = 0 V$                                                 | TL07xC                                                                                                                                            | $T_A$ = Full range       |          |                    | 10  | nΑ            |
| los                       | Input offset current                 |                                                             | TL07xAC, TL07xBC,<br>TL07xl                                                                                                                       |                          |          | 5                  | 100 | рA            |
|                           |                                      |                                                             |                                                                                                                                                   | $T_A$ = Full range       |          |                    | 2   | nΑ            |
|                           |                                      |                                                             | TL07xM                                                                                                                                            |                          |          | 5                  | 100 | рA            |
|                           |                                      |                                                             |                                                                                                                                                   | $T_A$ = Full range       |          |                    | 20  | nΑ            |
|                           |                                      |                                                             | TL07xC, TL07xAC,                                                                                                                                  |                          |          | 65                 | 200 | рA            |
|                           |                                      | $V_0 = 0 V$                                                 | TL07xBC, TL07xl                                                                                                                                   | $T_A$ = Full range       |          |                    | 7   | nΑ            |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 65                 | 200 | рA            |
| $\mathsf{I}_{\mathsf{B}}$ | Input bias current                   |                                                             | TL071M, TL072M                                                                                                                                    | $T_A$ = Full range       |          |                    | 50  | nΑ            |
|                           |                                      |                                                             |                                                                                                                                                   |                          |          | 65                 | 200 | рA            |
|                           |                                      |                                                             | TL074M                                                                                                                                            | $T_A$ = Full range       |          |                    | 20  | nΑ            |
| $V_{CM}$                  | Common-mode                          |                                                             |                                                                                                                                                   |                          |          | $\pm 11$ –12 to 15 |     | V             |
|                           | voltage range                        |                                                             |                                                                                                                                                   |                          |          |                    |     |               |
|                           |                                      | $R_L = 10 \text{ k}\Omega$                                  |                                                                                                                                                   |                          | $\pm 12$ | $\pm 13.5$         |     |               |
| VOM                       | Maximum peak output<br>voltage swing | $R_L \ge 10 \text{ k}\Omega$                                | $T_A$ = Full range                                                                                                                                | $\pm 12$                 |          |                    | V   |               |
|                           |                                      | $R_L \ge 2 k\Omega$                                         |                                                                                                                                                   |                          | $\pm 10$ |                    |     |               |
|                           |                                      |                                                             | TL07xC                                                                                                                                            |                          | 25       | 200                |     |               |
|                           |                                      |                                                             |                                                                                                                                                   | $T_A$ = Full range       | 15       |                    |     |               |
| $A_{OL}$                  | Open-loop voltage                    | $V_0 = 0 V$                                                 | TL07xAC, TL07xBC,                                                                                                                                 |                          | 50       | 200                |     | V/mV          |
|                           | gain                                 |                                                             | TL07xI                                                                                                                                            | $T_A$ = Full range       | 25       |                    |     |               |
|                           |                                      |                                                             | TL07xM                                                                                                                                            |                          | 35       | 200                |     |               |
|                           |                                      |                                                             |                                                                                                                                                   | $T_A$ = Full range       | 15       |                    |     |               |
| GBW                       | Gain-bandwidth                       | All NS and PS packages; All TL07xM devices                  |                                                                                                                                                   |                          |          | 3                  |     | MHz           |
|                           | product                              | All other devices                                           |                                                                                                                                                   |                          |          | 5.25               |     |               |
| $R_{ID}$                  | Common-mode input<br>resistance      |                                                             |                                                                                                                                                   |                          |          | 1                  |     | ΤΩ            |
|                           |                                      |                                                             | TL07xC                                                                                                                                            |                          | 70       | 100                |     |               |
| CMRR                      | Common-mode                          | $V_{IC} = V_{ICR(min)}$<br>$V_0 = 0 \text{ V}$              |                                                                                                                                                   | TL07xAC, TL07xBC, TL07xI |          |                    |     | $\mathsf{dB}$ |
|                           | rejection ratio                      | $R_S = 50 \Omega$                                           | TL07xM                                                                                                                                            | 80                       | 86       |                    |     |               |
|                           |                                      |                                                             | TL07xC                                                                                                                                            |                          | 70       | 100                |     |               |
| PSRR                      | Input offset voltage                 | $V_S = \pm 9 \text{ V to } \pm 18 \text{ V}$<br>$V_0 = 0 V$ | TL07xAC, TL07xBC, TL07xI                                                                                                                          |                          | 80       | 100                |     | $\mathsf{dB}$ |
|                           | versus power supply                  | $R_S = 50 \Omega$                                           | TL07xM                                                                                                                                            | 80                       | 86       |                    |     |               |
| lQ                        | Quiescent current per                | $V_O = 0 V$ ; no load                                       |                                                                                                                                                   |                          |          | 1.4                | 2.5 | mΑ            |
|                           | amplifier                            |                                                             |                                                                                                                                                   |                          |          |                    |     |               |
Copyright © 2023 Texas Instruments Incorporated
17 Submit Document Feedback
### **6.8 Electrical Characteristics (DC): TL07xC, TL07xAC, TL07xBC, TL07xI, TL07xM (continued)**
For VS = (VCC+) – (VCC–) = ±15 V at TA = 25°C, unless otherwise noted
| PARAMETER          | TEST CONDITIONS(1) (2) | MIN | TYP | MAX | UNIT |
|--------------------|------------------------|-----|-----|-----|------|
| Channel separation | f = 0 Hz               |     | 1   |     | µV/V |
(1) All characteristics are measured under open-loop conditions with zero common-mode voltage, unless otherwise specified.
(2) Full range is TA = 0°C to 70°C for the TL07xC, TL07xAC, and TL07xBC; TA = –40°C to 85°C for the TL07xI; and TA = –55°C to 125°C for the TL07xM.
## **6.9 Electrical Characteristics (AC): TL07xC, TL07xAC, TL07xBC, TL07xI, TL07xM**
For VS = (VCC+) – (VCC–) = ±15 V at T<sup>A</sup> = 25°C, unless otherwise noted.
|       | PARAMETER                     |                                               | TEST CONDITIONS                                         | MIN     | TYP   | MAX    | UNIT   |
|-------|-------------------------------|-----------------------------------------------|---------------------------------------------------------|---------|-------|--------|--------|
|       |                               |                                               |                                                         |         |       |        |        |
|       |                               |                                               | TL07xM                                                  | 5       | 20    |        | V/μs   |
| SR    | Slew rate                     | VI<br>= 10 V, CL = 100 pF, RL =<br>2 kΩ       | TL07xC, TL07xAC,<br>TL07xBC, TL07xI                     | 8       | 20    |        | V/μs   |
|       |                               |                                               |                                                         |         | 0.1   |        | μs     |
| tS    | Settling time                 | VI<br>= 20 V, CL = 100 pF, RL = 2 kΩ          |                                                         |         | 20%   |        |        |
|       |                               | All PS and NS packages; All<br>TL07xM devices | RS = 20 Ω, f = 1 kHz                                    |         | 18    |        | nV/√Hz |
| eN    | Input voltage noise density   |                                               | f = 1 kHz                                               |         | 37    |        |        |
|       | All other devices             | f = 10 kHz                                    |                                                         | 21      |       | nV/√Hz |        |
| EN    | Input voltage noise           | All PS and NS packages; All<br>TL07xM devices | RS = 20 Ω, f = 10 Hz to 10<br>kHz                       |         | 4     |        | μVRMS  |
|       |                               | All other devices                             | f = 0.1 Hz to 10 Hz                                     |         | 1.4   |        | µVRMS  |
| iN    | Input current noise           | RS = 20 Ω, f = 1 kHz                          |                                                         |         | 10    |        | fA/√Hz |
|       | Phase margin                  | TL07xC, TL07xAC,<br>TL07xBC, TL07xI           | G = +1, RL = 10 kΩ, CL = 20<br>pF                       |         | 56    |        | °      |
|       | Overload recovery time        | VIN × gain > VS                               |                                                         |         | 300   |        | ns     |
|       | Total harmonic distortion +   | All PS and NS packages; All<br>TL07xM devices | VO = 6 VRMS, RL ≥ 2 kΩ, f =<br>1 kHz, G = +1, RS ≤ 1 kΩ |         | 0.003 |        | %      |
| THD+N | noise                         | All other devices                             | VS = 40 V, VO = 6 VRMS, G =<br>+1, f = 1 kHz            | 0.00012 |       |        | %      |
| EMIRR | EMI rejection ratio           | TL07xC, TL07xAC,<br>TL07xBC, TL07xI           | f = 1 GHz                                               |         | 53    |        | dB     |
| ZO    | Open-loop output<br>impedance | TL07xC, TL07xAC,<br>TL07xBC, TL07xI           | f = 1 MHz, IO = 0 A                                     |         | 125   |        | Ω      |
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 19
#### TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072](https://www.ti.com/product/TL072), [TL072A,](https://www.ti.com/product/TL072A) [TL072B](https://www.ti.com/product/TL072B), [TL072H,](https://www.ti.com/product/TL072H) [TL072M](https://www.ti.com/product/TL072M) [TL074](https://www.ti.com/product/TL074), [TL074A,](https://www.ti.com/product/TL074A) [TL074B](https://www.ti.com/product/TL074B), [TL074H,](https://www.ti.com/product/TL074H) [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023 **[www.ti.com](https://www.ti.com)**
#### **6.10 Typical Characteristics: TL07xH**
## **6.10 Typical Characteristics: TL07xH (continued)**
#### TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072](https://www.ti.com/product/TL072), [TL072A,](https://www.ti.com/product/TL072A) [TL072B](https://www.ti.com/product/TL072B), [TL072H,](https://www.ti.com/product/TL072H) [TL072M](https://www.ti.com/product/TL072M) [TL074](https://www.ti.com/product/TL074), [TL074A,](https://www.ti.com/product/TL074A) [TL074B](https://www.ti.com/product/TL074B), [TL074H,](https://www.ti.com/product/TL074H) [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023 **[www.ti.com](https://www.ti.com)**
## **6.10 Typical Characteristics: TL07xH (continued)**
## **6.10 Typical Characteristics: TL07xH (continued)**
at TA = 25°C, VS = 40 V ( ±20 V), VCM = VS / 2, RLOAD = 10 kΩ connected to VS / 2, and CL = 20 pF (unless otherwise noted)
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 23
#### TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072](https://www.ti.com/product/TL072), [TL072A,](https://www.ti.com/product/TL072A) [TL072B](https://www.ti.com/product/TL072B), [TL072H,](https://www.ti.com/product/TL072H) [TL072M](https://www.ti.com/product/TL072M) [TL074](https://www.ti.com/product/TL074), [TL074A,](https://www.ti.com/product/TL074A) [TL074B](https://www.ti.com/product/TL074B), [TL074H,](https://www.ti.com/product/TL074H) [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023 **[www.ti.com](https://www.ti.com)**
## **6.10 Typical Characteristics: TL07xH (continued)**
at TA = 25°C, VS = 40 V ( ±20 V), VCM = VS / 2, RLOAD = 10 kΩ connected to VS / 2, and CL = 20 pF (unless otherwise noted)
24 *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* Copyright © 2023 Texas Instruments Incorporated
## **6.10 Typical Characteristics: TL07xH (continued)**
#### TL071, [TL071A,](https://www.ti.com/product/TL071A) [TL071B](https://www.ti.com/product/TL071B), [TL071H](https://www.ti.com/product/TL071H) [TL072](https://www.ti.com/product/TL072), [TL072A,](https://www.ti.com/product/TL072A) [TL072B](https://www.ti.com/product/TL072B), [TL072H,](https://www.ti.com/product/TL072H) [TL072M](https://www.ti.com/product/TL072M) [TL074](https://www.ti.com/product/TL074), [TL074A,](https://www.ti.com/product/TL074A) [TL074B](https://www.ti.com/product/TL074B), [TL074H,](https://www.ti.com/product/TL074H) [TL074M](https://www.ti.com/product/TL074M)** [SLOS080V](https://www.ti.com/lit/pdf/SLOS080) – SEPTEMBER 1978 – REVISED APRIL 2023 **[www.ti.com](https://www.ti.com)**
## **6.10 Typical Characteristics: TL07xH (continued)**
### 6.11 Typical Characteristics: All Devices Except TL07xH
### 6.11 Typical Characteristics: All Devices Except TL07xH (continued)
Copyright © 2023 Texas Instruments Incorporated
### 6.11 Typical Characteristics: All Devices Except TL07xH (continued)
#### **6.11 Typical Characteristics: All Devices Except TL07xH (continued)**
### **7 Parameter Measurement Information**
**Figure 7-1. Unity-Gain Amplifier**
**Figure 7-2. Gain-of-10 Inverting Amplifier**
**Figure 7-3. Input Offset-Voltage Null Circuit**
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 31
## **8 Detailed Description**
### **8.1 Overview**
The TL07xH (TL071H, TL072H, and TL074H) family of devices are the next-generation versions of the industrystandard TL07x (TL071, TL072, and TL074) devices. These devices provide outstanding value for cost-sensitive applications, with features including low offset (1 mV, typical), high slew rate (20 V/μs, typical), and commonmode input to the positive supply. High ESD (2 kV, HBM), integrated EMI and RF filters, and operation across the full –40°C to 125°C enable the TL07xH devices to be used in the most rugged and demanding applications.
The C-suffix devices are characterized for operation from 0°C to 70°C. The I-suffix devices are characterized for operation from −40°C to +85°C. The M-suffix devices are characterized for operation over the full military temperature range of −55°C to +125°C.
### **8.2 Functional Block Diagram**
### **8.3 Feature Description**
The TL07xH family of devices improve many specifications as compared to the industry-standard TL07x family. Several comparisons of key specifications between these families are included in the following sections to show the advantages of the TL07xH family.
### **8.3.1 Total Harmonic Distortion**
Harmonic distortions to an audio signal are created by electronic components in a circuit. Total harmonic distortion (THD) is a measure of harmonic distortions accumulated by a signal in an audio system. These devices have a very low THD of 0.003% meaning that the TL07x device adds little harmonic distortion when used in audio signal applications.
### **8.3.2 Slew Rate**
The slew rate is the rate at which an operational amplifier can change the output when there is a change on the input. These devices have a 20-V/μs slew rate.
## **8.4 Device Functional Modes**
These devices are powered on when the supply is connected. These devices can be operated as a single-supply operational amplifier or dual-supply amplifier depending on the application.
### **9 Application and Implementation**
#### **Note**
Information in the following applications sections is not part of the TI component specification, and TI does not warrant its accuracy or completeness. TI's customers are responsible for determining suitability of components for their purposes, as well as validating and testing their design implementation to confirm system functionality.
### **9.1 Application Information**
A typical application for an operational amplifier is an inverting amplifier. This amplifier takes a positive voltage on the input, and makes the voltage a negative voltage. In the same manner, the amplifier makes negative voltages positive.
#### **9.2 Typical Application**
**Figure 9-1. Inverting Amplifier**
#### **9.2.1 Design Requirements**
The supply voltage must be selected so the supply voltage is larger than the input voltage range and output range. For instance, this application scales a signal of ±0.5 V to ±1.8 V. Setting the supply at ±12 V is sufficient to accommodate this application.
#### **9.2.2 Detailed Design Procedure**
$$V_o = (V_i + V_{io}) \times \left(1 + \frac{1M\Omega}{1k\Omega}\right) \tag{1}$$
Determine the gain required by the inverting amplifier:
$$A_V = \frac{VOUT}{VIN} \tag{2}$$
$$A_V = \frac{1.8}{-0.5} = -3.6 \tag{3}$$
Once the desired gain is determined, select a value for RI or RF. Selecting a value in the kilohm range is desirable because the amplifier circuit uses currents in the milliamp range. This ensures the part does not draw too much current. This example uses 10 kΩ for RI which means 36 kΩ is used for RF. This is determined by Equation 4.
$$A_V = -\frac{RF}{RI} \tag{4}$$
#### Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 33
#### **9.2.3 Application Curve**
**Figure 9-2. Input and Output Voltages of the Inverting Amplifier**
#### **9.3 Unity Gain Buffer**
**Figure 9-3. Single-Supply Unity Gain Amplifier**
#### **9.3.1 Design Requirements**
- VCC must be within valid range per *[Recommended Operating Conditions](#page-11-0)*. This example uses a value of 12 V for VCC.
- Input voltage must be within the recommended common-mode range, as shown in *[Recommended Operating](#page-11-0)  [Conditions](#page-11-0)*. The valid common-mode range is 4 V to 12 V (VCC– + 4 V to VCC+).
- Output is limited by output range, which is typically 1.5 V to 10.5 V, or VCC– + 1.5 V to VCC+ 1.5 V.
#### **9.3.2 Detailed Design Procedure**
- Avoid input voltage values below 1 V to prevent phase reversal where output goes high.
- Avoid input values below 4 V to prevent degraded VIO that results in an apparent gain greater than 1. This may cause instability in some second-order filter designs.
#### 9.3.3 Application Curves
#### **9.4 System Examples**
Figure 9-6. 0.5-Hz Square-Wave Oscillator
Figure 9-7. High-Q Notch Filter
Figure 9-9. AC Amplifier
Copyright © 2023 Texas Instruments Incorporated
#### **9.5 Power Supply Recommendations**
#### **CAUTION**
Supply voltages larger than 36 V for a single-supply or outside the range of ±18 V for a dual-supply can permanently damage the device (see [Section 6.1](#page-11-0)).
Place 0.1-μF bypass capacitors close to the power-supply pins to reduce errors coupling in from noisy or high-impedance power supplies. For more detailed information on bypass capacitor placement, see Section 9.6.
#### **9.6 Layout**
#### **9.6.1 Layout Guidelines**
For best operational performance of the device, use good PCB layout practices, including:
- Noise can propagate into analog circuitry through the power pins of the circuit as a whole, as well as the operational amplifier. Bypass capacitors are used to reduce the coupled noise by providing low impedance power sources local to the analog circuitry.
  - Connect low-ESR, 0.1-μF ceramic bypass capacitors between each supply pin and ground, placed as close to the device as possible. A single bypass capacitor from VCC+ to ground is applicable for singlesupply applications.
- Separate grounding for analog and digital portions of circuitry is one of the simplest and most-effective methods of noise suppression. One or more layers on multilayer PCBs are usually devoted to ground planes. A ground plane helps distribute heat and reduces EMI noise pickup. Take care to physically separate digital and analog grounds, paying attention to the flow of the ground current.
- To reduce parasitic coupling, run the input traces as far away from the supply or output traces as possible. If it is not possible to keep them separate, it is much better to cross the sensitive trace perpendicular as opposed to in parallel with the noisy trace.
- Place the external components as close to the device as possible. Keeping RF and RG close to the inverting input minimizes parasitic capacitance. For more information, see [Section 9.6.2](#page-36-0).
- Keep the length of input traces as short as possible. Always remember that the input traces are the most sensitive part of the circuit.
- Consider a driven, low-impedance guard ring around the critical traces. A guard ring can significantly reduce leakage currents from nearby traces that are at different potentials.
#### **9.6.2 Layout Example**
**Figure 9-10. Operational Amplifier Board Layout for Noninverting Configuration**
**Figure 9-11. Operational Amplifier Schematic for Noninverting Configuration**
Copyright © 2023 Texas Instruments Incorporated *[Submit Document Feedback](https://www.ti.com/feedbackform/techdocfeedback?litnum=SLOS080V&partnum=TL071)* 37
## **10 Device and Documentation Support**
### **10.1 Receiving Notification of Documentation Updates**
To receive notification of documentation updates, navigate to the device product folder on [ti.com.](https://www.ti.com) Click on *Subscribe to updates* to register and receive a weekly digest of any product information that has changed. For change details, review the revision history included in any revised document.
#### **10.2 Support Resources**
TI E2E™ [support forums](https://e2e.ti.com) are an engineer's go-to source for fast, verified answers and design help — straight from the experts. Search existing answers or ask your own question to get the quick design help you need.
Linked content is provided "AS IS" by the respective contributors. They do not constitute TI specifications and do not necessarily reflect TI's views; see TI's [Terms of Use.](https://www.ti.com/corp/docs/legal/termsofuse.shtml)
### **10.3 Trademarks**
TI E2E™ is a trademark of Texas Instruments.
All trademarks are the property of their respective owners.
#### **10.4 Electrostatic Discharge Caution**
This integrated circuit can be damaged by ESD. Texas Instruments recommends that all integrated circuits be handled with appropriate precautions. Failure to observe proper handling and installation procedures can cause damage.
ESD damage can range from subtle performance degradation to complete device failure. Precision integrated circuits may be more susceptible to damage because very small parametric changes could cause the device not to meet its published specifications.
## **10.5 Glossary**
[TI Glossary](https://www.ti.com/lit/pdf/SLYZ022) This glossary lists and explains terms, acronyms, and definitions.
## **11 Mechanical, Packaging, and Orderable Information**
The following pages include mechanical packaging and orderable information. This information is the most current data available for the designated devices. This data is subject to change without notice and revision of this document. For browser based versions of this data sheet, refer to the left hand navigation.
## **PACKAGING INFORMATION**
| Orderable Device | Status<br>(1) | Package Type | Package<br>Drawing | Pins | Package<br>Qty | Eco Plan<br>(2)     | Lead finish/<br>Ball material<br>(6) | MSL Peak Temp<br>(3) | Op Temp (°C) | Device Marking<br>(4/5) | Samples |
|------------------|---------------|--------------|--------------------|------|----------------|---------------------|--------------------------------------|----------------------|--------------|-------------------------|---------|
| 81023052A        | ACTIVE        | LCCC         | FK                 | 20   | 55             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 81023052A<br>TL072MFKB  | Samples |
| 8102305HA        | ACTIVE        | CFP          | U                  | 10   | 25             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 8102305HA<br>TL072M     | Samples |
| 8102305PA        | ACTIVE        | CDIP         | JG                 | 8    | 50             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 8102305PA<br>TL072M     | Samples |
| 81023062A        | ACTIVE        | LCCC         | FK                 | 20   | 55             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 81023062A<br>TL074MFKB  | Samples |
| 8102306CA        | ACTIVE        | CDIP         | J                  | 14   | 25             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 8102306CA<br>TL074MJB   | Samples |
| 8102306DA        | ACTIVE        | CFP          | W                  | 14   | 25             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 8102306DA<br>TL074MWB   | Samples |
| JM38510/11905BPA | ACTIVE        | CDIP         | JG                 | 8    | 50             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | JM38510<br>/11905BPA    | Samples |
| M38510/11905BPA  | ACTIVE        | CDIP         | JG                 | 8    | 50             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | JM38510<br>/11905BPA    | Samples |
| TL071ACDR        | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | 071AC                   | Samples |
| TL071ACP         | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL071ACP                | Samples |
| TL071BCDR        | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | 071BC                   | Samples |
| TL071BCP         | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL071BCP                | Samples |
| TL071CDR         | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | TL071C                  | Samples |
| TL071CDRE4       | ACTIVE        | SOIC         | D                  | 8    | 2500           | TBD                 | Call TI                              | Call TI              | 0 to 70      |                         | Samples |
| TL071CDRG4       | ACTIVE        | SOIC         | D                  | 8    | 2500           | TBD                 | Call TI                              | Call TI              | 0 to 70      |                         | Samples |
| TL071CP          | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL071CP                 | Samples |
| TL071CPE4        | ACTIVE        | PDIP         | P                  | 8    | 50             | TBD                 | Call TI                              | Call TI              | 0 to 70      |                         | Samples |
| TL071CPSR        | ACTIVE        | SO           | PS                 | 8    | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | T071                    | Samples |
| Orderable Device | Status<br>(1) | Package Type | Package<br>Drawing | Pins | Package<br>Qty | Eco Plan<br>(2) | Lead finish/<br>Ball material | MSL Peak Temp<br>(3) | Op Temp (°C) | Device Marking<br>(4/5) | Samples |
|------------------|---------------|--------------|--------------------|------|----------------|-----------------|-------------------------------|----------------------|--------------|-------------------------|---------|
| TL071HIDBVR      | ACTIVE        | SOT-23       | DBV                | 5    | 3000           | RoHS & Green    | (6)<br>NIPDAU                 | Level-1-260C-UNLIM   | -40 to 125   | T71V                    |         |
|                  |               |              |                    |      |                |                 |                               |                      |              |                         | Samples |
| TL071HIDCKR      | ACTIVE        | SC70         | DCK                | 5    | 3000           | RoHS & Green    | SN                            | Level-1-260C-UNLIM   | -40 to 125   | 1IO                     | Samples |
| TL071HIDR        | ACTIVE        | SOIC         | D                  | 8    | 3000           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 125   | TL071D                  | Samples |
| TL071IDR         | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 85    | TL071I                  | Samples |
| TL071IDRG4       | ACTIVE        | SOIC         | D                  | 8    | 2500           | TBD             | Call TI                       | Call TI              | -40 to 85    |                         | Samples |
| TL071IP          | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green    | NIPDAU                        | N / A for Pkg Type   | -40 to 85    | TL071IP                 | Samples |
| TL072ACDR        | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | 072AC                   | Samples |
| TL072ACDRE4      | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | 072AC                   | Samples |
| TL072ACDRG4      | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | 072AC                   | Samples |
| TL072ACP         | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green    | NIPDAU                        | N / A for Pkg Type   | 0 to 70      | TL072ACP                | Samples |
| TL072ACPE4       | ACTIVE        | PDIP         | P                  | 8    | 50             | TBD             | Call TI                       | Call TI              | 0 to 70      |                         | Samples |
| TL072ACPS        | ACTIVE        | SO           | PS                 | 8    | 80             | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | T072A                   | Samples |
| TL072BCDR        | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | 072BC                   | Samples |
| TL072BCP         | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green    | NIPDAU                        | N / A for Pkg Type   | 0 to 70      | TL072BCP                | Samples |
| TL072CDR         | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL072C                  | Samples |
| TL072CDRE4       | LIFEBUY       | SOIC         | D                  | 8    | 2500           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL072C                  |         |
| TL072CP          | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green    | NIPDAU                        | N / A for Pkg Type   | 0 to 70      | TL072CP                 | Samples |
| TL072CPE4        | LIFEBUY       | PDIP         | P                  | 8    | 50             | RoHS & Green    | NIPDAU                        | N / A for Pkg Type   | 0 to 70      | TL072CP                 |         |
| TL072CPS         | ACTIVE        | SO           | PS                 | 8    | 80             | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | T072                    | Samples |
| TL072CPSR        | ACTIVE        | SO           | PS                 | 8    | 2000           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | T072                    | Samples |
| TL072CPSRG4      | ACTIVE        | SO           | PS                 | 8    | 2000           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | T072                    | Samples |
| TL072CPWR        | ACTIVE        | TSSOP        | PW                 | 8    | 2000           | RoHS & Green    | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | T072                    | Samples |
| Orderable Device | Status<br>(1) | Package Type | Package<br>Drawing | Pins | Package<br>Qty | Eco Plan<br>(2)     | Lead finish/<br>Ball material | MSL Peak Temp<br>(3) | Op Temp (°C) | Device Marking<br>(4/5) | Samples |
|------------------|---------------|--------------|--------------------|------|----------------|---------------------|-------------------------------|----------------------|--------------|-------------------------|---------|
|                  |               |              |                    |      |                |                     | (6)                           |                      |              |                         |         |
| TL072CPWRE4      | ACTIVE        | TSSOP        | PW                 | 8    | 2000           | TBD                 | Call TI                       | Call TI              | 0 to 70      |                         | Samples |
| TL072CPWRG4      | ACTIVE        | TSSOP        | PW                 | 8    | 2000           | TBD                 | Call TI                       | Call TI              | 0 to 70      |                         | Samples |
| TL072HIDDFR      | ACTIVE        | SOT-23-THIN  | DDF                | 8    | 3000           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 125   | O72F                    | Samples |
| TL072HIDR        | ACTIVE        | SOIC         | D                  | 8    | 3000           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 125   | TL072D                  | Samples |
| TL072HIPWR       | ACTIVE        | TSSOP        | PW                 | 8    | 3000           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 125   | 072HPW                  | Samples |
| TL072IDR         | ACTIVE        | SOIC         | D                  | 8    | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 85    | TL072I                  | Samples |
| TL072IDRE4       | LIFEBUY       | SOIC         | D                  | 8    | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 85    | TL072I                  |         |
| TL072IDRG4       | LIFEBUY       | SOIC         | D                  | 8    | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | -40 to 85    | TL072I                  |         |
| TL072IP          | ACTIVE        | PDIP         | P                  | 8    | 50             | RoHS & Green        | NIPDAU                        | N / A for Pkg Type   | -40 to 85    | TL072IP                 | Samples |
| TL072IPE4        | ACTIVE        | PDIP         | P                  | 8    | 50             | TBD                 | Call TI                       | Call TI              | -40 to 85    |                         | Samples |
| TL072MFKB        | ACTIVE        | LCCC         | FK                 | 20   | 55             | Non-RoHS<br>& Green | SNPB                          | N / A for Pkg Type   | -55 to 125   | 81023052A<br>TL072MFKB  | Samples |
| TL072MJG         | ACTIVE        | CDIP         | JG                 | 8    | 50             | Non-RoHS<br>& Green | SNPB                          | N / A for Pkg Type   | -55 to 125   | TL072MJG                | Samples |
| TL072MJGB        | ACTIVE        | CDIP         | JG                 | 8    | 50             | Non-RoHS<br>& Green | SNPB                          | N / A for Pkg Type   | -55 to 125   | 8102305PA<br>TL072M     | Samples |
| TL072MUB         | ACTIVE        | CFP          | U                  | 10   | 25             | Non-RoHS<br>& Green | SNPB                          | N / A for Pkg Type   | -55 to 125   | 8102305HA<br>TL072M     | Samples |
| TL074ACDR        | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL074AC                 | Samples |
| TL074ACDRE4      | LIFEBUY       | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL074AC                 |         |
| TL074ACN         | ACTIVE        | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                        | N / A for Pkg Type   | 0 to 70      | TL074ACN                | Samples |
| TL074ACNE4       | LIFEBUY       | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                        | N / A for Pkg Type   | 0 to 70      | TL074ACN                |         |
| TL074ACNSR       | ACTIVE        | SO           | NS                 | 14   | 2000           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL074A                  | Samples |
| TL074BCDR        | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL074BC                 | Samples |
| TL074BCDRE4      | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                        | Level-1-260C-UNLIM   | 0 to 70      | TL074BC                 | Samples |
| Orderable Device | Status<br>(1) | Package Type | Package<br>Drawing | Pins | Package<br>Qty | Eco Plan<br>(2)     | Lead finish/<br>Ball material<br>(6) | MSL Peak Temp<br>(3) | Op Temp (°C) | Device Marking<br>(4/5) | Samples |
|------------------|---------------|--------------|--------------------|------|----------------|---------------------|--------------------------------------|----------------------|--------------|-------------------------|---------|
| TL074BCDRG4      | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | TL074BC                 | Samples |
| TL074BCN         | ACTIVE        | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL074BCN                | Samples |
| TL074BCNE4       | LIFEBUY       | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL074BCN                |         |
| TL074CDBR        | ACTIVE        | SSOP         | DB                 | 14   | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | T074                    | Samples |
| TL074CDR         | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU   SN                          | Level-1-260C-UNLIM   | 0 to 70      | TL074C                  | Samples |
| TL074CDRG4       | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | TL074C                  | Samples |
| TL074CN          | ACTIVE        | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL074CN                 | Samples |
| TL074CNE4        | LIFEBUY       | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | 0 to 70      | TL074CN                 |         |
| TL074CNSR        | ACTIVE        | SO           | NS                 | 14   | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | TL074                   | Samples |
| TL074CPWR        | ACTIVE        | TSSOP        | PW                 | 14   | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | T074                    | Samples |
| TL074CPWRE4      | ACTIVE        | TSSOP        | PW                 | 14   | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | T074                    | Samples |
| TL074CPWRG4      | ACTIVE        | TSSOP        | PW                 | 14   | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | 0 to 70      | T074                    | Samples |
| TL074HIDR        | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | -40 to 125   | TL074HID                | Samples |
| TL074HIDYYR      | ACTIVE        | SOT-23-THIN  | DYY                | 14   | 3000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | -40 to 125   | T074HDYY                | Samples |
| TL074HIPWR       | ACTIVE        | TSSOP        | PW                 | 14   | 2000           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | -40 to 125   | TL074PW                 | Samples |
| TL074IDR         | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | -40 to 85    | TL074I                  | Samples |
| TL074IDRE4       | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | -40 to 85    | TL074I                  | Samples |
| TL074IDRG4       | ACTIVE        | SOIC         | D                  | 14   | 2500           | RoHS & Green        | NIPDAU                               | Level-1-260C-UNLIM   | -40 to 85    | TL074I                  | Samples |
| TL074IN          | ACTIVE        | PDIP         | N                  | 14   | 25             | RoHS & Green        | NIPDAU                               | N / A for Pkg Type   | -40 to 85    | TL074IN                 | Samples |
| TL074MFK         | ACTIVE        | LCCC         | FK                 | 20   | 55             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | TL074MFK                | Samples |
| TL074MFKB        | ACTIVE        | LCCC         | FK                 | 20   | 55             | Non-RoHS<br>& Green | SNPB                                 | N / A for Pkg Type   | -55 to 125   | 81023062A<br>TL074MFKB  | Samples |
| Orderable Device | Status | Package Type | Package | Pins | Package | Eco Plan            | Lead finish/  | MSL Peak Temp      | Op Temp (°C) | Device Marking        | Samples |
|------------------|--------|--------------|---------|------|---------|---------------------|---------------|--------------------|--------------|-----------------------|---------|
|                  | (1)    |              | Drawing |      | Qty     | (2)                 | Ball material | (3)                |              | (4/5)                 |         |
|                  |        |              |         |      |         |                     | (6)           |                    |              |                       |         |
| TL074MJ          | ACTIVE | CDIP         | J       | 14   | 25      | Non-RoHS<br>& Green | SNPB          | N / A for Pkg Type | -55 to 125   | TL074MJ               | Samples |
| TL074MJB         | ACTIVE | CDIP         | J       | 14   | 25      | Non-RoHS<br>& Green | SNPB          | N / A for Pkg Type | -55 to 125   | 8102306CA<br>TL074MJB | Samples |
| TL074MWB         | ACTIVE | CFP          | W       | 14   | 25      | Non-RoHS<br>& Green | SNPB          | N / A for Pkg Type | -55 to 125   | 8102306DA<br>TL074MWB | Samples |
**(1)** The marketing status values are defined as follows:
**ACTIVE:** Product device recommended for new designs.
**LIFEBUY:** TI has announced that the device will be discontinued, and a lifetime-buy period is in effect.
**NRND:** Not recommended for new designs. Device is in production to support existing customers, but TI does not recommend using this part in a new design.
**PREVIEW:** Device has been announced but is not in production. Samples may or may not be available.
**OBSOLETE:** TI has discontinued the production of the device.
**(2) RoHS:** TI defines "RoHS" to mean semiconductor products that are compliant with the current EU RoHS requirements for all 10 RoHS substances, including the requirement that RoHS substance do not exceed 0.1% by weight in homogeneous materials. Where designed to be soldered at high temperatures, "RoHS" products are suitable for use in specified lead-free processes. TI may reference these types of products as "Pb-Free".
**RoHS Exempt:** TI defines "RoHS Exempt" to mean products that contain lead but are compliant with EU RoHS pursuant to a specific EU RoHS exemption.
**Green:** TI defines "Green" to mean the content of Chlorine (Cl) and Bromine (Br) based flame retardants meet JS709B low halogen requirements of <=1000ppm threshold. Antimony trioxide based flame retardants must also meet the <=1000ppm threshold requirement.
**(3)** MSL, Peak Temp. - The Moisture Sensitivity Level rating according to the JEDEC industry standard classifications, and peak solder temperature.
**(4)** There may be additional marking, which relates to the logo, the lot trace code information, or the environmental category on the device.
**(5)** Multiple Device Markings will be inside parentheses. Only one Device Marking contained in parentheses and separated by a "~" will appear on a device. If a line is indented then it is a continuation of the previous line and the two combined represent the entire Device Marking for that device.
**(6)** Lead finish/Ball material - Orderable Devices may have multiple material finish options. Finish options are separated by a vertical ruled line. Lead finish/Ball material values may wrap to two lines if the finish value exceeds the maximum column width.
**Important Information and Disclaimer:**The information provided on this page represents TI's knowledge and belief as of the date that it is provided. TI bases its knowledge and belief on information provided by third parties, and makes no representation or warranty as to the accuracy of such information. Efforts are underway to better integrate information from third parties. TI has taken and continues to take reasonable steps to provide representative and accurate information but may not have conducted destructive testing or chemical analysis on incoming materials and chemicals. TI and TI suppliers consider certain information to be proprietary, and thus CAS numbers and other limited information may not be available for release.
In no event shall TI's liability arising out of such information exceed the total purchase price of the TI part(s) at issue in this document sold by TI to Customer on an annual basis.
#### **OTHER QUALIFIED VERSIONS OF TL072, TL072M, TL074, TL074M :**
• Catalog : [TL072](http://focus.ti.com/docs/prod/folders/print/tl072.html), [TL074](http://focus.ti.com/docs/prod/folders/print/tl074.html)
- Enhanced Product : [TL072-EP](http://focus.ti.com/docs/prod/folders/print/tl072-ep.html), [TL072-EP](http://focus.ti.com/docs/prod/folders/print/tl072-ep.html), [TL074-EP, TL074-EP](http://focus.ti.com/docs/prod/folders/print/tl074-ep.html)
- Military : [TL072M,](http://focus.ti.com/docs/prod/folders/print/tl072m.html) [TL074M](http://focus.ti.com/docs/prod/folders/print/tl074m.html)
NOTE: Qualified Version Definitions:
#### • Catalog - TI's standard catalog product
- Enhanced Product - Supports Defense, Aerospace and Medical Applications
- Military - QML certified for Military and Defense Applications
www.ti.com 6-Apr-2024
### **TAPE AND REEL INFORMATION**
#### **QUADRANT ASSIGNMENTS FOR PIN 1 ORIENTATION IN TAPE**
| *All dimensions are nominal |                 |                    |      |      |                          |                          |            |            |            |            |           |                  |
|-----------------------------|-----------------|--------------------|------|------|--------------------------|--------------------------|------------|------------|------------|------------|-----------|------------------|
| Device                      | Package<br>Type | Package<br>Drawing | Pins | SPQ  | Reel<br>Diameter<br>(mm) | Reel<br>Width<br>W1 (mm) | A0<br>(mm) | B0<br>(mm) | K0<br>(mm) | P1<br>(mm) | W<br>(mm) | Pin1<br>Quadrant |
| TL071ACDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071ACDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071BCDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071BCDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071CDR                    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071CDR                    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071CPSR                   | SO              | PS                 | 8    | 2000 | 330.0                    | 16.4                     | 8.35       | 6.6        | 2.4        | 12.0       | 16.0      | Q1               |
| TL071HIDBVR                 | SOT-23          | DBV                | 5    | 3000 | 180.0                    | 8.4                      | 3.2        | 3.2        | 1.4        | 4.0        | 8.0       | Q3               |
| TL071HIDCKR                 | SC70            | DCK                | 5    | 3000 | 178.0                    | 9.0                      | 2.4        | 2.5        | 1.2        | 4.0        | 8.0       | Q3               |
| TL071HIDR                   | SOIC            | D                  | 8    | 3000 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL071IDR                    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072ACDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072ACDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072BCDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072BCDR                   | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072CDR                    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
## **PACKAGE MATERIALS INFORMATION**
www.ti.com 6-Apr-2024
| Device      | Package<br>Type | Package<br>Drawing | Pins | SPQ  | Reel<br>Diameter<br>(mm) | Reel<br>Width<br>W1 (mm) | A0<br>(mm) | B0<br>(mm) | K0<br>(mm) | P1<br>(mm) | W<br>(mm) | Pin1<br>Quadrant |
|-------------|-----------------|--------------------|------|------|--------------------------|--------------------------|------------|------------|------------|------------|-----------|------------------|
| TL072CDR    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072CDR    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072CPSR   | SO              | PS                 | 8    | 2000 | 330.0                    | 16.4                     | 8.35       | 6.6        | 2.4        | 12.0       | 16.0      | Q1               |
| TL072CPWR   | TSSOP           | PW                 | 8    | 2000 | 330.0                    | 12.4                     | 7.0        | 3.6        | 1.6        | 8.0        | 12.0      | Q1               |
| TL072CPWR   | TSSOP           | PW                 | 8    | 2000 | 330.0                    | 12.4                     | 7.0        | 3.6        | 1.6        | 8.0        | 12.0      | Q1               |
| TL072HIDDFR | SOT-23-<br>THIN | DDF                | 8    | 3000 | 180.0                    | 8.4                      | 3.2        | 3.2        | 1.4        | 4.0        | 8.0       | Q3               |
| TL072HIDR   | SOIC            | D                  | 8    | 3000 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072HIPWR  | TSSOP           | PW                 | 8    | 3000 | 330.0                    | 12.4                     | 7.0        | 3.6        | 1.6        | 8.0        | 12.0      | Q1               |
| TL072IDR    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072IDR    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL072IDR    | SOIC            | D                  | 8    | 2500 | 330.0                    | 12.4                     | 6.4        | 5.2        | 2.1        | 8.0        | 12.0      | Q1               |
| TL074ACDR   | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074ACDR   | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074ACNSR  | SO              | NS                 | 14   | 2000 | 330.0                    | 16.4                     | 8.2        | 10.5       | 2.5        | 12.0       | 16.0      | Q1               |
| TL074BCDR   | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074BCDR   | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074CDBR   | SSOP            | DB                 | 14   | 2000 | 330.0                    | 16.4                     | 8.35       | 6.6        | 2.4        | 12.0       | 16.0      | Q1               |
| TL074CDR    | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074CDR    | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074CDRG4  | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074CNSR   | SO              | NS                 | 14   | 2000 | 330.0                    | 16.4                     | 8.2        | 10.5       | 2.5        | 12.0       | 16.0      | Q1               |
| TL074CPWR   | TSSOP           | PW                 | 14   | 2000 | 330.0                    | 12.4                     | 6.9        | 5.6        | 1.6        | 8.0        | 12.0      | Q1               |
| TL074CPWR   | TSSOP           | PW                 | 14   | 2000 | 330.0                    | 12.4                     | 6.9        | 5.6        | 1.6        | 8.0        | 12.0      | Q1               |
| TL074HIDR   | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074HIDYYR | SOT-23-<br>THIN | DYY                | 14   | 3000 | 330.0                    | 12.4                     | 4.8        | 3.6        | 1.6        | 8.0        | 12.0      | Q3               |
| TL074HIPWR  | TSSOP           | PW                 | 14   | 2000 | 330.0                    | 12.4                     | 6.9        | 5.6        | 1.6        | 8.0        | 12.0      | Q1               |
| TL074IDR    | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
| TL074IDR    | SOIC            | D                  | 14   | 2500 | 330.0                    | 16.4                     | 6.5        | 9.0        | 2.1        | 8.0        | 16.0      | Q1               |
www.ti.com 6-Apr-2024
# **PACKAGE MATERIALS INFORMATION**
| *All dimensions are nominal<br>Device | Package Type | Package Drawing | Pins | SPQ  | Length (mm) | Width (mm) | Height (mm) |
|---------------------------------------|--------------|-----------------|------|------|-------------|------------|-------------|
|                                       |              |                 |      |      |             |            |             |
| TL071ACDR                             | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL071ACDR                             | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL071BCDR                             | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL071BCDR                             | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL071CDR                              | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL071CDR                              | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL071CPSR                             | SO           | PS              | 8    | 2000 | 356.0       | 356.0      | 35.0        |
| TL071HIDBVR                           | SOT-23       | DBV             | 5    | 3000 | 210.0       | 185.0      | 35.0        |
| TL071HIDCKR                           | SC70         | DCK             | 5    | 3000 | 190.0       | 190.0      | 30.0        |
| TL071HIDR                             | SOIC         | D               | 8    | 3000 | 356.0       | 356.0      | 35.0        |
| TL071IDR                              | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL072ACDR                             | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL072ACDR                             | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL072BCDR                             | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL072BCDR                             | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL072CDR                              | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL072CDR                              | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL072CDR                              | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
## **PACKAGE MATERIALS INFORMATION**
www.ti.com 6-Apr-2024
| Device      | Package Type | Package Drawing | Pins | SPQ  | Length (mm) | Width (mm) | Height (mm) |
|-------------|--------------|-----------------|------|------|-------------|------------|-------------|
| TL072CPSR   | SO           | PS              | 8    | 2000 | 356.0       | 356.0      | 35.0        |
| TL072CPWR   | TSSOP        | PW              | 8    | 2000 | 356.0       | 356.0      | 35.0        |
| TL072CPWR   | TSSOP        | PW              | 8    | 2000 | 356.0       | 356.0      | 35.0        |
| TL072HIDDFR | SOT-23-THIN  | DDF             | 8    | 3000 | 210.0       | 185.0      | 35.0        |
| TL072HIDR   | SOIC         | D               | 8    | 3000 | 356.0       | 356.0      | 35.0        |
| TL072HIPWR  | TSSOP        | PW              | 8    | 3000 | 356.0       | 356.0      | 35.0        |
| TL072IDR    | SOIC         | D               | 8    | 2500 | 340.5       | 338.1      | 20.6        |
| TL072IDR    | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL072IDR    | SOIC         | D               | 8    | 2500 | 356.0       | 356.0      | 35.0        |
| TL074ACDR   | SOIC         | D               | 14   | 2500 | 333.2       | 345.9      | 28.6        |
| TL074ACDR   | SOIC         | D               | 14   | 2500 | 356.0       | 356.0      | 35.0        |
| TL074ACNSR  | SO           | NS              | 14   | 2000 | 356.0       | 356.0      | 35.0        |
| TL074BCDR   | SOIC         | D               | 14   | 2500 | 356.0       | 356.0      | 35.0        |
| TL074BCDR   | SOIC         | D               | 14   | 2500 | 340.5       | 336.1      | 32.0        |
| TL074CDBR   | SSOP         | DB              | 14   | 2000 | 356.0       | 356.0      | 35.0        |
| TL074CDR    | SOIC         | D               | 14   | 2500 | 356.0       | 356.0      | 35.0        |
| TL074CDR    | SOIC         | D               | 14   | 2500 | 333.2       | 345.9      | 28.6        |
| TL074CDRG4  | SOIC         | D               | 14   | 2500 | 340.5       | 336.1      | 32.0        |
| TL074CNSR   | SO           | NS              | 14   | 2000 | 356.0       | 356.0      | 35.0        |
| TL074CPWR   | TSSOP        | PW              | 14   | 2000 | 356.0       | 356.0      | 35.0        |
| TL074CPWR   | TSSOP        | PW              | 14   | 2000 | 356.0       | 356.0      | 35.0        |
| TL074HIDR   | SOIC         | D               | 14   | 2500 | 356.0       | 356.0      | 35.0        |
| TL074HIDYYR | SOT-23-THIN  | DYY             | 14   | 3000 | 336.6       | 336.6      | 31.8        |
| TL074HIPWR  | TSSOP        | PW              | 14   | 2000 | 356.0       | 356.0      | 35.0        |
| TL074IDR    | SOIC         | D               | 14   | 2500 | 333.2       | 345.9      | 28.6        |
| TL074IDR    | SOIC         | D               | 14   | 2500 | 356.0       | 356.0      | 35.0        |
www.ti.com 6-Apr-2024
## **TUBE**
## **B - Alignment groove width**
| Device     | Package Name | Package Type | Pins | SPQ | L (mm) | W (mm) | T (µm) | B (mm) |
|------------|--------------|--------------|------|-----|--------|--------|--------|--------|
| 81023052A  | FK           | LCCC         | 20   | 55  | 506.98 | 12.06  | 2030   | NA     |
| 8102305HA  | U            | CFP          | 10   | 25  | 506.98 | 26.16  | 6220   | NA     |
| 81023062A  | FK           | LCCC         | 20   | 55  | 506.98 | 12.06  | 2030   | NA     |
| 8102306DA  | W            | CFP          | 14   | 25  | 506.98 | 26.16  | 6220   | NA     |
| TL071ACP   | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL071BCP   | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL071CP    | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL071IP    | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL072ACP   | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL072ACPS  | PS           | SOP          | 8    | 80  | 530    | 10.5   | 4000   | 4.1    |
| TL072BCP   | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL072CP    | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL072CPE4  | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL072CPS   | PS           | SOP          | 8    | 80  | 530    | 10.5   | 4000   | 4.1    |
| TL072IP    | P            | PDIP         | 8    | 50  | 506    | 13.97  | 11230  | 4.32   |
| TL072MFKB  | FK           | LCCC         | 20   | 55  | 506.98 | 12.06  | 2030   | NA     |
| TL072MUB   | U            | CFP          | 10   | 25  | 506.98 | 26.16  | 6220   | NA     |
| TL074ACN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074ACN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074ACN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074ACNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074ACNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074ACNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074BCN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074BCN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074BCN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074BCNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074BCNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074BCNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
## **PACKAGE MATERIALS INFORMATION**
www.ti.com 6-Apr-2024
| Device    | Package Name | Package Type | Pins | SPQ | L (mm) | W (mm) | T (µm) | B (mm) |
|-----------|--------------|--------------|------|-----|--------|--------|--------|--------|
| TL074CN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074CN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074CN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074CNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074CNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074CNE4 | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074IN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074IN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074IN   | N            | PDIP         | 14   | 25  | 506    | 13.97  | 11230  | 4.32   |
| TL074MFK  | FK           | LCCC         | 20   | 55  | 506.98 | 12.06  | 2030   | NA     |
| TL074MFKB | FK           | LCCC         | 20   | 55  | 506.98 | 12.06  | 2030   | NA     |
| TL074MWB  | W            | CFP          | 14   | 25  | 506.98 | 26.16  | 6220   | NA     |
# JG0008A
# PACKAGE OUTLINE
## CDIP - 5.08 mm max height
CERAMIC DUAL IN-LINE PACKAGE
NOTES:
- 1. All linear dimensions are in millimeters. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing This drawing is subject to change without notice.
   This package can be hermetically sealed with a ceramic lid using glass frit.
- Index point is provided on cap for terminal identification.
   Falls within MIL STD 1835 GDIP1-T8
# **EXAMPLE BOARD LAYOUT**
## **JG0008A CDIP - 5.08 mm max height**
CERAMIC DUAL IN-LINE PACKAGE
# **PACKAGE OUTLINE**
# **U0010A CFP - 2.03 mm max height**
CERAMIC FLATPACK
1. All linear dimensions are in inches. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing per ASME Y14.5M.
2. This drawing is subject to change without notice.
# **PACKAGE OUTLINE**
# **DDF0008A SOT-23 - 1.1 mm max height**
PLASTIC SMALL OUTLINE
NOTES:
- 1. All linear dimensions are in millimeters. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing per ASME Y14.5M.
- 2. This drawing is subject to change without notice.
- 3. This dimension does not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed 0.15 mm per side.
# **DDF0008A**
# EXAMPLE BOARD LAYOUT
## SOT-23 - 1.1 mm max height
PLASTIC SMALL OUTLINE
NOTES: (continued)
4. Publication IPC-7351 may have alternate designs.
5. Solder mask tolerances between and around signal pads can vary based on board fabrication site.
# **EXAMPLE STENCIL DESIGN**
## **DDF0008A SOT-23 - 1.1 mm max height**
PLASTIC SMALL OUTLINE
NOTES: (continued)
- 6. Laser cutting apertures with trapezoidal walls and rounded corners may offer better paste release. IPC-7525 may have alternate design recommendations.
- 7. Board assembly site may have different recommendations for stencil design.
# DYY0014A
# PACKAGE OUTLINE SOT-23-THIN - 1.1 mm max height
PLASTIC SMALL OUTLINE
#### NOTES:
- All linear dimensions are in millimeters. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing 1. per ASME Y14.5M.
- 2. This drawing is subject to change without notice.
- This dimension does not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed 3. 0.15 per side.
- 4. This dimension does not include interlead flash. Interlead flash shall not exceed 0.50 per side.
- Reference JEDEC Registration MO-345, Variation AB 5.
# DYY0014A
# **EXAMPLE BOARD LAYOUT** SOT-23-THIN - 1.1 mm max height
PLASTIC SMALL OUTLINE
NOTES: (continued)
- Publication IPC-7351 may have alternate designs. 6.
- Solder mask tolerances between and around signal pads can vary based on board fabrication site. 7.
# DYY0014A
# **EXAMPLE STENCIL DESIGN** SOT-23-THIN - 1.1 mm max height
PLASTIC SMALL OUTLINE
NOTES: (continued)
- Laser cutting apertures with trapezoidal walls and rounded corners may offer better paste release. IPC-7525 may have alternate 8. design recommendations.
- 9. Board assembly site may have different recommendations for stencil design.
W (R-GDFP-F14)
CERAMIC DUAL FLATPACK
- A. All linear dimensions are in inches (millimeters).
  - B. This drawing is subject to change without notice.
  - C. This package can be hermetically sealed with a ceramic lid using glass frit.
  - D. Index point is provided on cap for terminal identification only.
  - E. Falls within MIL STD 1835 GDFP1-F14
# **GENERIC PACKAGE VIEW**
## **FK 20 LCCC - 2.03 mm max height**
**8.89 x 8.89, 1.27 mm pitch** LEADLESS CERAMIC CHIP CARRIER
This image is a representation of the package family, actual package may vary. Refer to the product data sheet for package details.
# **GENERIC PACKAGE VIEW**
# CDIP - 5.08 mm max height
CERAMIC DUAL IN LINE PACKAGE
Images above are just a representation of the package family, actual package may vary. Refer to the product data sheet for package details.
# J0014A
# PACKAGE OUTLINE
## CDIP - 5.08 mm max height
CERAMIC DUAL IN LINE PACKAGE
NOTES:
- 1. All controlling linear dimensions are in inches. Dimensions in brackets are in millimeters. Any dimension in brackets or parenthesis are for reference only. Dimensioning and tolerancing per ASME Y14.5M.
- 2. This drawing is subject to change without notice.
- 3. This package is hermitically sealed with a ceramic lid using glass frit.
- 4. Index point is provided on cap for terminal identification only and on press ceramic glass frit seal only.
  5. Falls within MIL-STD-1835 and GDIP1-T14.
# **EXAMPLE BOARD LAYOUT**
## **J0014A CDIP - 5.08 mm max height**
CERAMIC DUAL IN LINE PACKAGE
# **PACKAGE OUTLINE**
# **DBV0005A SOT-23 - 1.45 mm max height**
SMALL OUTLINE TRANSISTOR
NOTES:
- 1. All linear dimensions are in millimeters. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing per ASME Y14.5M.
- 2. This drawing is subject to change without notice.
- 3. Refernce JEDEC MO-178.
- 4. Body dimensions do not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed 0.25 mm per side.
- 5. Support pin may differ or may not be present.
# DBV0005A
# EXAMPLE BOARD LAYOUT
## SOT-23 - 1.45 mm max height
SMALL OUTLINE TRANSISTOR
NOTES: (continued)
6. Publication IPC-7351 may have alternate designs.
7. Solder mask tolerances between and around signal pads can vary based on board fabrication site.
# **EXAMPLE STENCIL DESIGN**
## **DBV0005A SOT-23 - 1.45 mm max height**
SMALL OUTLINE TRANSISTOR
NOTES: (continued)
8. Laser cutting apertures with trapezoidal walls and rounded corners may offer better paste release. IPC-7525 may have alternate design recommendations.
9. Board assembly site may have different recommendations for stencil design.
# DCK0005A
# PACKAGE OUTLINE
## SOT - 1.1 max height
SMALL OUTLINE TRANSISTOR
NOTES:
- 1. All linear dimensions are in millimeters. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing 2. This drawing is subject to change without notice.
  3. Reference JEDEC MO-203.
- 4. Support pin may differ or may not be present.5. Lead width does not comply with JEDEC.
# DCK0005A
# EXAMPLE BOARD LAYOUT
## SOT - 1.1 max height
SMALL OUTLINE TRANSISTOR
NOTES: (continued)
6. Publication IPC-7351 may have alternate designs.
7. Solder mask tolerances between and around signal pads can vary based on board fabrication site.
# **EXAMPLE STENCIL DESIGN**
## **DCK0005A SOT - 1.1 max height**
SMALL OUTLINE TRANSISTOR
NOTES: (continued)
8. Laser cutting apertures with trapezoidal walls and rounded corners may offer better paste release. IPC-7525 may have alternate design recommendations.
9. Board assembly site may have different recommendations for stencil design.
D (R-PDSO-G14)
PLASTIC SMALL OUTLINE
NOTES: A. All linear dimensions are in inches (millimeters).
- B. This drawing is subject to change without notice.
- 🛆 Body length does not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed 0.006 (0,15) each side.
- D Body width does not include interlead flash. Interlead flash shall not exceed 0.017 (0,43) each side.
- E. Reference JEDEC MS-012 variation AB.
NOTES: A. All linear dimensions are in millimeters.
- B. This drawing is subject to change without notice.
- C. Publication IPC-7351 is recommended for alternate designs.
- D. Laser cutting apertures with trapezoidal walls and also rounding corners will offer better paste release. Customers should contact their board assembly site for stencil design recommendations. Refer to IPC-7525 for other stencil recommendations. E. Customers should contact their board fabrication site for solder mask tolerances between and around signal pads.
PW (R-PDSO-G14)
PLASTIC SMALL OUTLINE
This drawing is subject to change without notice.  $\;$ В.
🛆 Body length does not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed 0,15 each side.
🛆 Body width does not include interlead flash. Interlead flash shall not exceed 0,25 each side.
E. Falls within JEDEC MO $-153$ 
# **PACKAGE OUTLINE**
# **D0008A SOIC - 1.75 mm max height**
SMALL OUTLINE INTEGRATED CIRCUIT
NOTES:
1. Linear dimensions are in inches [millimeters]. Dimensions in parenthesis are for reference only. Controlling dimensions are in inches. Dimensioning and tolerancing per ASME Y14.5M.
- 2. This drawing is subject to change without notice.
- 3. This dimension does not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed .006 [0.15] per side.
- 4. This dimension does not include interlead flash.
- 5. Reference JEDEC registration MS-012, variation AA.
# **EXAMPLE BOARD LAYOUT**
## **D0008A SOIC - 1.75 mm max height**
SMALL OUTLINE INTEGRATED CIRCUIT
NOTES: (continued)
6. Publication IPC-7351 may have alternate designs.
7. Solder mask tolerances between and around signal pads can vary based on board fabrication site.
# **EXAMPLE STENCIL DESIGN**
## **D0008A SOIC - 1.75 mm max height**
SMALL OUTLINE INTEGRATED CIRCUIT
NOTES: (continued)
8. Laser cutting apertures with trapezoidal walls and rounded corners may offer better paste release. IPC-7525 may have alternate design recommendations.
9. Board assembly site may have different recommendations for stencil design.
#### MECHANICAL DATA
#### PS (R-PDSO-G8)
PLASTIC SMALL-OUTLINE PACKAGE
A. All linear dimensions are in millimeters.
 $\mathsf{B}. \quad \mathsf{This} \ \mathsf{drawing} \ \mathsf{is} \ \mathsf{subject} \ \mathsf{to} \ \mathsf{change} \ \mathsf{without} \ \mathsf{notice}.$ 
C. Body dimensions do not include mold flash or protrusion, not to exceed 0,15.
NOTES:
- А. All linear dimensions are in millimeters.
- В. This drawing is subject to change without notice.
- Publication IPC-7351 is recommended for alternate designs. С.
- D. Laser cutting apertures with trapezoidal walls and also rounding corners will offer better paste release. Customers should contact their board assembly site for stencil design recommendations. Refer to IPC-7525 for other stencil recommendations. E. Customers should contact their board fabrication site for solder mask tolerances between and around signal pads.
ÈXAS NSTRUMENTS www.ti.com
P (R-PDIP-T8)
PLASTIC DUAL-IN-LINE PACKAGE
- B. This drawing is subject to change without notice.
- C. Falls within JEDEC MS-001 variation BA.
#### N (R-PDIP-T\*\*) 16 PINS SHOWN
PLASTIC DUAL-IN-LINE PACKAGE
NOTES:
- A. All linear dimensions are in inches (millimeters). B. This drawing is subject to change without notice.
- C Falls within JEDEC MS-001, except 18 and 20 pin minimum body length (Dim A).
- 🛆 The 20 pin end lead shoulder width is a vendor option, either half or full width.
# **PACKAGE OUTLINE**
# **PW0008A TSSOP - 1.2 mm max height**
SMALL OUTLINE PACKAGE
NOTES:
- 1. All linear dimensions are in millimeters. Any dimensions in parenthesis are for reference only. Dimensioning and tolerancing per ASME Y14.5M.
- 2. This drawing is subject to change without notice.
- 3. This dimension does not include mold flash, protrusions, or gate burrs. Mold flash, protrusions, or gate burrs shall not exceed 0.15 mm per side.
- 4. This dimension does not include interlead flash. Interlead flash shall not exceed 0.25 mm per side.
- 5. Reference JEDEC registration MO-153, variation AA.
# PW0008A
# EXAMPLE BOARD LAYOUT
# TSSOP - 1.2 mm max height
SMALL OUTLINE PACKAGE
NOTES: (continued)
6. Publication IPC-7351 may have alternate designs.
7. Solder mask tolerances between and around signal pads can vary based on board fabrication site.
# **EXAMPLE STENCIL DESIGN**
# **PW0008A TSSOP - 1.2 mm max height**
SMALL OUTLINE PACKAGE
NOTES: (continued)
- 8. Laser cutting apertures with trapezoidal walls and rounded corners may offer better paste release. IPC-7525 may have alternate design recommendations.
- 9. Board assembly site may have different recommendations for stencil design.
# MECHANICAL DATA
MSSO002E - JANUARY 1995 - REVISED DECEMBER 2001
# DB (R-PDSO-G\*\*)
#### PLASTIC SMALL-OUTLINE
**28 PINS SHOWN** 
NOTES: A. All linear dimensions are in millimeters.
- B. This drawing is subject to change without notice.
- C. Body dimensions do not include mold flash or protrusion not to exceed 0,15.
- D. Falls within JEDEC MO-150
#### MECHANICAL DATA
#### PLASTIC SMALL-OUTLINE PACKAGE
#### NS (R-PDSO-G\*\*) **14-PINS SHOWN**
All linear dimensions are in millimeters. А.
- $\mbox{B.}$   $\mbox{ This drawing is subject to change without notice.}$
- C. Body dimensions do not include mold flash or protrusion, not to exceed 0,15.
#### **IMPORTANT NOTICE AND DISCLAIMER**
TI PROVIDES TECHNICAL AND RELIABILITY DATA (INCLUDING DATA SHEETS), DESIGN RESOURCES (INCLUDING REFERENCE DESIGNS), APPLICATION OR OTHER DESIGN ADVICE, WEB TOOLS, SAFETY INFORMATION, AND OTHER RESOURCES "AS IS" AND WITH ALL FAULTS, AND DISCLAIMS ALL WARRANTIES, EXPRESS AND IMPLIED, INCLUDING WITHOUT LIMITATION ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE OR NON-INFRINGEMENT OF THIRD PARTY INTELLECTUAL PROPERTY RIGHTS.
These resources are intended for skilled developers designing with TI products. You are solely responsible for (1) selecting the appropriate TI products for your application, (2) designing, validating and testing your application, and (3) ensuring your application meets applicable standards, and any other safety, security, regulatory or other requirements.
These resources are subject to change without notice. TI grants you permission to use these resources only for development of an application that uses the TI products described in the resource. Other reproduction and display of these resources is prohibited. No license is granted to any other TI intellectual property right or to any third party intellectual property right. TI disclaims responsibility for, and you will fully indemnify TI and its representatives against, any claims, damages, costs, losses, and liabilities arising out of your use of these resources.
TI's products are provided subject to [TI's Terms of Sale](https://www.ti.com/legal/terms-conditions/terms-of-sale.html) or other applicable terms available either on [ti.com](https://www.ti.com) or provided in conjunction with such TI products. TI's provision of these resources does not expand or otherwise alter TI's applicable warranties or warranty disclaimers for TI products.
TI objects to and rejects any additional or different terms you may have proposed. IMPORTANT NOTICE
Mailing Address: Texas Instruments, Post Office Box 655303, Dallas, Texas 75265 Copyright © 2024, Texas Instruments Incorporated