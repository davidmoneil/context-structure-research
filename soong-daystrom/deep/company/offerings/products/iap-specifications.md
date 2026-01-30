# IAP Industrial Automation Platform - Technical Specifications

**Document**: IAP Series Full Technical Specifications
**Version**: 3.1.0
**Classification**: Distribution Authorized
**Publication Date**: February 2124
**Part Number**: SDI-SPEC-IAP-2124-03

---

## Document Overview

This specification document provides comprehensive technical details for the Soong-Daystrom Industries Industrial Automation Platform (IAP) product series. The IAP platform represents SDI's industrial-grade automation solution designed for manufacturing, logistics, and heavy industrial applications.

---

## 1. IAP Platform Architecture

### 1.1 System Philosophy

The IAP platform is built on SDI's Industrial Autonomy Framework (IAF), which emphasizes:

- **Modular Scalability**: Add capabilities without system redesign
- **Graceful Degradation**: Maintain operation during component failures
- **Human-Centric Safety**: Multiple independent safety layers
- **Adaptive Learning**: Continuous optimization within defined parameters
- **Interoperability**: Standard protocols for legacy and modern integration

### 1.2 Platform Tiers

| Tier | Model Range | Application | Max Payload | Base Price |
|------|-------------|-------------|-------------|------------|
| Light Industrial | IAP-100 Series | Assembly, Packaging | 50 kg | 85,000 credits |
| Medium Industrial | IAP-300 Series | Manufacturing, Logistics | 250 kg | 220,000 credits |
| Heavy Industrial | IAP-500 Series | Heavy Manufacturing | 1,000 kg | 480,000 credits |
| Specialized | IAP-700 Series | Hazardous/Extreme | Variable | 750,000+ credits |

### 1.3 Core Components

All IAP units share a common core architecture:

**IAP Central Controller (ICC)**
- Soong Industrial Core SIC-8000 processor
- 10 PB operational memory
- 100 PB extended storage
- Redundant processing paths
- Real-time operating system (RTOS-IAP v8.2)

**Power Management System (PMS)**
- Primary: Grid connection (380-480V 3-phase)
- Backup: Integrated battery (4-hour reserve)
- Emergency: Capacitor bank (safe shutdown guarantee)
- Optional: FC-Industrial fusion cell

**Safety Subsystem (SSS)**
- Independent safety controller
- Hardware interrupt capability
- Multi-zone awareness
- Certified to ISO 13849-1:2120 PLe

**Communication Array (CA)**
- Industrial Ethernet (1 Gbps / 10 Gbps)
- OPC-UA native support
- SDI Industrial Protocol (SIP)
- Legacy fieldbus adapters available

---

## 2. IAP-100 Series Specifications

### 2.1 Overview

The IAP-100 series is designed for light industrial applications requiring precision, speed, and flexibility. Ideal for electronics assembly, packaging, laboratory automation, and light manufacturing.

### 2.2 Models

| Model | Configuration | Reach | Payload | Repeatability |
|-------|---------------|-------|---------|---------------|
| IAP-110 | 6-axis articulated | 850 mm | 10 kg | +/-0.02 mm |
| IAP-120 | 6-axis articulated | 1,200 mm | 25 kg | +/-0.03 mm |
| IAP-130 | 6-axis articulated | 1,500 mm | 50 kg | +/-0.05 mm |
| IAP-150 | SCARA configuration | 700 mm | 15 kg | +/-0.01 mm |
| IAP-160 | Delta configuration | 1,100 mm | 8 kg | +/-0.02 mm |

### 2.3 Physical Specifications (IAP-120 Reference)

| Parameter | Specification |
|-----------|---------------|
| Base Dimensions | 350 mm x 350 mm |
| Height (folded) | 1,100 mm |
| Weight | 145 kg |
| Mounting | Floor, ceiling, wall, rail |
| Footprint (working) | 2.4 m radius |
| Material | Aerospace aluminum, carbon composite |
| IP Rating | IP54 (IP67 optional) |

### 2.4 Performance Specifications

| Parameter | IAP-110 | IAP-120 | IAP-130 |
|-----------|---------|---------|---------|
| Max Speed (J1-J3) | 250 deg/s | 200 deg/s | 150 deg/s |
| Max Speed (J4-J6) | 400 deg/s | 350 deg/s | 300 deg/s |
| Max TCP Speed | 4 m/s | 3.5 m/s | 3 m/s |
| Cycle Time (typical) | 0.4 s | 0.5 s | 0.6 s |
| Payload at Max Speed | 5 kg | 12 kg | 25 kg |
| Continuous Duty Cycle | 100% | 100% | 100% |

### 2.5 Axis Specifications (IAP-120)

| Axis | Range | Max Speed | Max Torque | Resolution |
|------|-------|-----------|------------|------------|
| J1 (Base) | +/-180 deg | 200 deg/s | 180 Nm | 0.001 deg |
| J2 (Shoulder) | +160/-60 deg | 200 deg/s | 180 Nm | 0.001 deg |
| J3 (Elbow) | +180/-120 deg | 250 deg/s | 120 Nm | 0.001 deg |
| J4 (Wrist 1) | +/-360 deg | 350 deg/s | 30 Nm | 0.001 deg |
| J5 (Wrist 2) | +/-130 deg | 350 deg/s | 30 Nm | 0.001 deg |
| J6 (Wrist 3) | +/-360 deg | 500 deg/s | 15 Nm | 0.001 deg |

### 2.6 End Effector Interface

| Parameter | Specification |
|-----------|---------------|
| Mechanical Interface | ISO 9409-1-50-4-M6 |
| Tool Flange Load | 50 kg max |
| Electrical | 8x Digital I/O, 4x Analog |
| Pneumatic | 2x 6mm ports (optional) |
| Communication | EtherCAT, RS-485 |
| Power | 24V DC, 5A max |

---

## 3. IAP-300 Series Specifications

### 3.1 Overview

The IAP-300 series addresses medium industrial requirements including automotive manufacturing, aerospace assembly, logistics handling, and general manufacturing applications.

### 3.2 Models

| Model | Configuration | Reach | Payload | Repeatability |
|-------|---------------|-------|---------|---------------|
| IAP-310 | 6-axis articulated | 2,000 mm | 100 kg | +/-0.05 mm |
| IAP-320 | 6-axis articulated | 2,500 mm | 150 kg | +/-0.06 mm |
| IAP-330 | 6-axis articulated | 3,000 mm | 250 kg | +/-0.08 mm |
| IAP-340 | 7-axis redundant | 2,200 mm | 80 kg | +/-0.05 mm |
| IAP-350 | Dual-arm | 1,800 mm ea | 50 kg ea | +/-0.04 mm |

### 3.3 Physical Specifications (IAP-320 Reference)

| Parameter | Specification |
|-----------|---------------|
| Base Dimensions | 700 mm x 700 mm |
| Height (folded) | 2,200 mm |
| Weight | 890 kg |
| Mounting | Floor (standard), rail (optional) |
| Footprint (working) | 5.0 m radius |
| Material | Steel frame, aluminum links |
| IP Rating | IP65 (IP68 optional) |

### 3.4 Performance Specifications

| Parameter | IAP-310 | IAP-320 | IAP-330 |
|-----------|---------|---------|---------|
| Max Speed (J1-J3) | 150 deg/s | 120 deg/s | 100 deg/s |
| Max Speed (J4-J6) | 250 deg/s | 200 deg/s | 180 deg/s |
| Max TCP Speed | 2.5 m/s | 2.2 m/s | 2.0 m/s |
| Cycle Time (typical) | 0.8 s | 1.0 s | 1.2 s |
| Payload at Max Speed | 50 kg | 75 kg | 125 kg |
| Continuous Duty Cycle | 100% | 100% | 95% |

### 3.5 IAP-350 Dual-Arm Specifications

The IAP-350 features two coordinated arms for complex manipulation tasks:

| Parameter | Specification |
|-----------|---------------|
| Arms | 2x 7-axis |
| Reach (each) | 1,800 mm |
| Payload (each) | 50 kg |
| Combined Payload | 80 kg (coordinated) |
| Repeatability | +/-0.04 mm |
| Coordination Latency | <1 ms |
| Collision Avoidance | Real-time, 1 kHz update |
| Cooperative Modes | Mirror, Complementary, Independent |

### 3.6 Power Requirements (IAP-300 Series)

| Parameter | IAP-310 | IAP-320 | IAP-330 |
|-----------|---------|---------|---------|
| Input Voltage | 380-480V 3ph | 380-480V 3ph | 380-480V 3ph |
| Frequency | 50/60 Hz | 50/60 Hz | 50/60 Hz |
| Power (peak) | 12 kVA | 18 kVA | 25 kVA |
| Power (typical) | 4 kW | 6 kW | 9 kW |
| Power Factor | >0.95 | >0.95 | >0.95 |

---

## 4. IAP-500 Series Specifications

### 4.1 Overview

The IAP-500 series handles heavy industrial applications including heavy equipment manufacturing, shipbuilding, large structure assembly, and material handling in foundries and steel mills.

### 4.2 Models

| Model | Configuration | Reach | Payload | Repeatability |
|-------|---------------|-------|---------|---------------|
| IAP-510 | 6-axis heavy | 3,500 mm | 500 kg | +/-0.10 mm |
| IAP-520 | 6-axis heavy | 4,000 mm | 750 kg | +/-0.15 mm |
| IAP-530 | 6-axis heavy | 4,500 mm | 1,000 kg | +/-0.20 mm |
| IAP-540 | Gantry | 10,000+ mm | 2,000 kg | +/-0.25 mm |
| IAP-550 | Parallel kinematics | 2,500 mm | 500 kg | +/-0.05 mm |

### 4.3 Physical Specifications (IAP-520 Reference)

| Parameter | Specification |
|-----------|---------------|
| Base Dimensions | 1,200 mm x 1,200 mm |
| Height (folded) | 3,500 mm |
| Weight | 3,800 kg |
| Mounting | Floor (reinforced foundation) |
| Footprint (working) | 8.0 m radius |
| Material | High-strength steel |
| IP Rating | IP66 |

### 4.4 Performance Specifications

| Parameter | IAP-510 | IAP-520 | IAP-530 |
|-----------|---------|---------|---------|
| Max Speed (J1-J3) | 80 deg/s | 65 deg/s | 50 deg/s |
| Max Speed (J4-J6) | 120 deg/s | 100 deg/s | 80 deg/s |
| Max TCP Speed | 1.5 m/s | 1.2 m/s | 1.0 m/s |
| Cycle Time (typical) | 2.0 s | 2.5 s | 3.0 s |
| Payload at Max Speed | 250 kg | 375 kg | 500 kg |
| Moment of Inertia (J6) | 500 kg*m2 | 800 kg*m2 | 1,200 kg*m2 |

### 4.5 IAP-540 Gantry System

| Parameter | Specification |
|-----------|---------------|
| Travel X | 10,000 mm (extendable) |
| Travel Y | 5,000 mm standard |
| Travel Z | 3,000 mm |
| Max Speed X/Y | 2 m/s |
| Max Speed Z | 1 m/s |
| Payload | 2,000 kg |
| Repeatability | +/-0.25 mm |
| Wrist | Optional 3-axis |
| Structure | Modular rail segments |

### 4.6 Foundation Requirements (IAP-500 Series)

| Model | Minimum Slab | Anchor Points | Dynamic Load |
|-------|--------------|---------------|--------------|
| IAP-510 | 400 mm | 8x M24 | 50 kN |
| IAP-520 | 500 mm | 12x M30 | 80 kN |
| IAP-530 | 600 mm | 16x M36 | 120 kN |
| IAP-540 | Per design | Custom | Per span |

---

## 5. IAP-700 Series Specifications

### 5.1 Overview

The IAP-700 series addresses specialized and extreme environment applications including hazardous material handling, radioactive environments, underwater operations, and space-rated systems.

### 5.2 Models

| Model | Specialization | Environment | Certification |
|-------|---------------|-------------|---------------|
| IAP-710 | Cleanroom | ISO Class 1-3 | ISO 14644 |
| IAP-720 | Explosive Atmosphere | Zone 0/1/2 | ATEX/IECEx |
| IAP-730 | Radiation Hardened | Nuclear | NQA-1 |
| IAP-740 | Underwater | 500m depth | ABS/DNV |
| IAP-750 | Space Rated | Vacuum/Thermal | NASA-STD |

### 5.3 IAP-710 Cleanroom Specifications

| Parameter | Specification |
|-----------|---------------|
| Base Platform | IAP-120 or IAP-310 |
| ISO Class Rating | Class 1 (ISO 14644-1) |
| Particle Generation | <100 particles/min @ 0.1um |
| Outgassing | <0.01% TML |
| Lubricants | Ultra-low vapor pressure |
| Sealing | Positive pressure capable |
| Surface Finish | Electropolished stainless |
| Compatible Processes | Semiconductor, pharmaceutical, biotech |

### 5.4 IAP-720 Explosion-Proof Specifications

| Parameter | Specification |
|-----------|---------------|
| Base Platform | IAP-120 or IAP-310 |
| ATEX Category | II 2G/D |
| Zone Rating | Gas Zone 1, Dust Zone 21 |
| Temperature Class | T4 (135C max) |
| Enclosure | Ex d (flameproof) |
| Motor Type | Ex-rated brushless |
| Cables | Armored, rated for zone |
| Certification | ATEX, IECEx, NEC 500/505 |

### 5.5 IAP-730 Radiation Hardened Specifications

| Parameter | Specification |
|-----------|---------------|
| Base Platform | IAP-310 modified |
| Total Dose Tolerance | 1 MRad (Si) |
| Single Event Upset | Immune to 100 MeV*cm2/mg |
| Decontaminable | Full washdown capable |
| Cable Routing | Radiation-resistant PEEK |
| Electronics | Rad-hard components |
| Operating Life | 15 years in 100 kRad/year |
| Standards | NQA-1, 10CFR50 Appendix B |

### 5.6 IAP-740 Underwater Specifications

| Parameter | Specification |
|-----------|---------------|
| Base Platform | Custom heavy duty |
| Depth Rating | 500 m (5,000 m special order) |
| Pressure Housing | Titanium Grade 5 |
| Seals | Multi-stage, field replaceable |
| Hydraulics | Biodegradable fluid |
| Communication | Fiber optic tether |
| Power | External via umbilical |
| Buoyancy | Neutral (adjustable) |
| Certification | ABS, DNV-GL, Lloyd's |

---

## 6. Control System Specifications

### 6.1 IAP Control Cabinet (ICC)

| Parameter | Specification |
|-----------|---------------|
| Enclosure | NEMA 4X / IP66 |
| Dimensions | 800 x 600 x 2000 mm (Series 100/300) |
| Cooling | Forced air / Closed loop chiller |
| Power Input | 380-480V 3ph + 24V DC auxiliary |
| I/O Capacity | 256 digital / 64 analog (expandable) |
| Motion Axes | 12 interpolated (24 max) |
| Communication | EtherNet/IP, PROFINET, EtherCAT |

### 6.2 Software Platform

**Operating System**: RTOS-IAP v8.2
- Deterministic real-time kernel
- 250 us motion cycle time
- Sub-microsecond jitter
- Dual-redundant execution option

**Programming Environment**: SDI Studio Professional
- IEC 61131-3 compliant (Ladder, Structured Text, Function Block)
- Robot-specific extensions (RobotScript)
- 3D simulation and offline programming
- Automatic path optimization
- Collision detection and avoidance

**Motion Control**: SDI MotionCore v6
- Multi-axis interpolation
- Conveyor tracking
- Force/torque control
- Vibration suppression
- Predictive maintenance integration

### 6.3 Human-Machine Interface

**Standard HMI**: SDI TouchPanel TP-15
- 15" capacitive touchscreen
- Industrial-grade (IP65 front)
- 3D visualization
- Multi-language support (47 languages)

**Optional Interfaces**:
- Teach pendant (wireless capable)
- Voice command module
- AR/VR programming interface
- Mobile device integration

### 6.4 Safety System

| Component | Specification |
|-----------|---------------|
| Safety PLC | Dual-channel, Category 4 |
| E-Stop | Hardwired, monitored |
| Light Curtains | Type 4, 14 mm resolution |
| Area Scanners | 5.5 m range, 275 deg FOV |
| Safety Mats | Zone selectable |
| Safe Torque Off | STO per IEC 61800-5-2 |
| Safe Speed | SS1, SS2, SLS, SLI, SLP |
| Response Time | <20 ms to safe state |

---

## 7. Integration Specifications

### 7.1 Communication Protocols

| Protocol | Support Level | Cycle Time |
|----------|---------------|------------|
| EtherNet/IP | Native | 1-100 ms |
| PROFINET IRT | Native | 250 us |
| EtherCAT | Native | 100 us |
| OPC-UA | Native | Variable |
| Modbus TCP | Adapter | 10 ms |
| DeviceNet | Adapter | 5 ms |
| PROFIBUS DP | Adapter | 1 ms |
| CC-Link IE | Adapter | 31.25 us |

### 7.2 Vision System Integration

| Feature | Specification |
|---------|---------------|
| Camera Support | GigE Vision, USB3 Vision |
| Image Processing | Onboard GPU (optional) |
| 2D Guidance | Part location, inspection |
| 3D Guidance | Point cloud processing |
| AI Vision | Neural network inference |
| Calibration | Automatic hand-eye |
| Update Rate | Up to 120 fps |

### 7.3 Force/Torque Sensing

| Parameter | Specification |
|-----------|---------------|
| Sensor Type | 6-axis strain gauge |
| Force Range | +/-500 N (Series 100) to +/-5000 N (Series 500) |
| Torque Range | +/-50 Nm to +/-500 Nm |
| Resolution | 0.1 N / 0.01 Nm |
| Bandwidth | 7 kHz |
| Overload Protection | 300% rated |
| Applications | Assembly, polishing, testing |

### 7.4 Tool Changers

| Type | Payload | Utilities | Change Time |
|------|---------|-----------|-------------|
| TC-50 | 50 kg | 8 pneumatic, 24 electric | 1.5 s |
| TC-150 | 150 kg | 12 pneumatic, 32 electric | 2.0 s |
| TC-500 | 500 kg | 16 pneumatic, 48 electric | 3.0 s |
| TC-1000 | 1000 kg | Custom | 5.0 s |

---

## 8. Environmental Specifications

### 8.1 Operating Environment (Standard)

| Parameter | Specification |
|-----------|---------------|
| Temperature | 5C to 45C |
| Humidity | 10-90% RH non-condensing |
| Altitude | 0-2,000 m (derate above) |
| Vibration | 0.5g, 10-55 Hz |
| EMC | EN 61000-6-2, EN 61000-6-4 |
| Noise | <70 dB(A) typical |

### 8.2 Extended Environment Options

| Option | Temperature Range | Additional Certification |
|--------|-------------------|-------------------------|
| Cold Storage | -30C to +20C | IEC 60721-3-3 |
| High Temperature | +20C to +60C | IEC 60721-3-3 |
| Washdown | Standard + spray protection | NSF/3-A |
| Corrosive | Standard + coating | NEMA 4X |

---

## 9. Ordering Information

### 9.1 Model Numbering

**Format**: IAP-XYZ-AABBCC

- X: Series (1=Light, 3=Medium, 5=Heavy, 7=Specialized)
- Y: Base configuration
- Z: Variant
- AA: Reach code
- BB: Payload code
- CC: Options package

**Example**: IAP-320-25150-EX
- Series 300 (Medium Industrial)
- Configuration 2 (Standard 6-axis)
- Variant 0 (Base)
- 2500mm reach
- 150kg payload
- EX: Explosion-proof option

### 9.2 Lead Times

| Series | Standard | Configured | Custom |
|--------|----------|------------|--------|
| IAP-100 | 4 weeks | 8 weeks | 16 weeks |
| IAP-300 | 6 weeks | 12 weeks | 20 weeks |
| IAP-500 | 8 weeks | 16 weeks | 24 weeks |
| IAP-700 | Quote | Quote | Quote |

### 9.3 Warranty

**Standard Warranty**: 24 months parts and labor

**Extended Warranty Options**:
- Year 3-5: 15,000 credits/year (Series 100), 35,000 credits/year (Series 300), 75,000 credits/year (Series 500)
- Preventive maintenance included
- Priority support response

### 9.4 Training

| Course | Duration | Location | Price |
|--------|----------|----------|-------|
| Operator Fundamentals | 3 days | Customer site | 5,000 credits |
| Programming Level 1 | 5 days | SDI Training Center | 8,000 credits |
| Programming Level 2 | 5 days | SDI Training Center | 10,000 credits |
| Maintenance Certification | 5 days | SDI Training Center | 12,000 credits |
| Integration Specialist | 10 days | SDI Training Center | 25,000 credits |

---

## 10. Compliance and Certifications

### 10.1 Regulatory Compliance

| Region | Standard | Status |
|--------|----------|--------|
| Global | ISO 10218-1:2121 | Certified |
| Global | ISO 10218-2:2121 | Compliant |
| Global | ISO 13849-1:2120 PLe | Certified |
| North America | NRTL (UL/CSA) | Listed |
| Europe | CE Machinery Directive | Declared |
| China | GB/T 15706 | Certified |
| Korea | KC Mark | Certified |
| Japan | JIS B 8433 | Certified |

### 10.2 Industry-Specific Certifications

| Certification | Applicable Models | Purpose |
|---------------|-------------------|---------|
| SEMI S2/S8 | IAP-100, IAP-710 | Semiconductor |
| 21 CFR Part 11 | All | Pharmaceutical |
| ISO 13485 | IAP-100 | Medical device mfg |
| IATF 16949 | All | Automotive |
| AS9100D | All | Aerospace |

---

*Document Part Number: SDI-SPEC-IAP-2124-03*
*Version 3.1.0 - February 2124*
*Copyright 2124 Soong-Daystrom Industries. All rights reserved.*

*Specifications subject to change without notice. Contact SDI Industrial Sales for current specifications and pricing.*
