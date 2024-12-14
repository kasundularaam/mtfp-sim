# Solid Tyre Manufacturing Factory Simulation Documentation

## Project Overview
This project implements a SimPy-based simulation of a solid tyre manufacturing factory. The simulation models the complete manufacturing process for solid tyres including Press-On Tyres and two variants of Resilient Tyres (with and without soft compound).

## Manufacturing Process

### Process Flow
The manufacturing process is divided into two main phases:

1. Building Process
2. Curing Process

#### Building Stations
The factory has the following building stations:
1. Wrap Inner Heal Station
2. Apply Bead Station
3. Wrap Heal Station
4. Resilient Tyre Bond Wrap Station
5. Press-On Tyre Bond Wrap Station
6. Wrap Soft Station
7. Wrap Tread Station
8. Press Station

#### Process Variations by Tyre Type

**Resilient Tyres (With Soft & Bond)**
- Building Steps Sequence:
  1. Wrap Inner Heal
  2. Apply Bead
  3. Wrap Heal
  4. Wrap Resilient Bond
  5. Wrap Soft
  6. Wrap Tread
  7. Press

**Resilient Tyres (Without Soft & Bond)**
- Building Steps Sequence:
  1. Wrap Inner Heal
  2. Apply Bead
  3. Wrap Heal
  4. Wrap Tread
  5. Press

**Press-On Tyres**
- Building Steps Sequence:
  1. Wrap Press-On Bond
  2. Wrap Soft
  3. Wrap Tread
  4. Press

## Time and Temperature Parameters

### Building Process Timing
- Most building steps duration: < 1 minute (variable due to manual labor)
- Press step duration: 2-5 minutes
- Examples of step durations:
  - Wrap Inner Heal: 40-50 seconds
  - Wrap Bond: 45-55 seconds
  - Wrap Soft: 45-55 seconds
  - Press: 2-5 minutes depending on tyre size and type

### Curing Process Parameters

#### Temperature Requirements

**Resilient Tyres (With Soft & Bond)**
- Heal Temperature Range: 70°C - 100°C
  - Optimal: 90°C - 100°C
  - Acceptable: 80°C - 89°C
  - Minimum: 70°C - 79°C
- Soft Temperature Range: 80°C - 110°C
  - Optimal: 100°C - 110°C
  - Acceptable: 90°C - 99°C
  - Minimum: 80°C - 89°C

**Resilient Tyres (Without Soft & Bond)**
- Heal Temperature Range: 70°C - 100°C
  - Optimal: 90°C - 100°C
  - Acceptable: 80°C - 89°C
  - Minimum: 70°C - 79°C

**Press-On Tyres**
- Soft Temperature Range: 80°C - 110°C
  - Optimal: 100°C - 110°C
  - Acceptable: 90°C - 99°C
  - Minimum: 80°C - 89°C

#### Curing Duration Rules

**Base Curing Times**
- Resilient Tyres (With Soft & Bond): 120 minutes at optimal temperature
- Resilient Tyres (Without Soft & Bond): 100 minutes at optimal temperature
- Press-On Tyres: 90 minutes at optimal temperature

**Temperature-Based Adjustments**
1. At Optimal Temperature Range:
   - Use base curing time
   
2. At Acceptable Temperature Range:
   - Add 20 minutes to base curing time
   - Example: Resilient tyre with soft at 85°C heal temperature = 140 minutes

3. At Minimum Temperature Range:
   - Add 40 minutes to base curing time
   - Example: Press-On tyre at 82°C soft temperature = 130 minutes

**Size-Based Adjustments**
- Small size: Base time
- Medium size: Base time + 15 minutes
- Large size: Base time + 30 minutes

**Combined Time Calculation Example**
For a large Resilient tyre with soft & bond at acceptable temperature:
- Base time: 120 minutes
- Temperature adjustment (Acceptable range): +20 minutes
- Size adjustment (Large): +30 minutes
- Total curing time: 170 minutes

## Resource Capacity

### Building Process Resources
- Each building station has a capacity of 1 unit
- Separate bond wrapping stations for:
  - Press-On Tyre Bond Wrapping
  - Resilient Tyre Bond Wrapping (used only for Resilient tyres with soft)

### Curing Process Resources
- Number of curing ovens: 12 units

## Order Management

### Order CSV Structure
The order data is stored in a CSV file with the following columns:
- PID: Product Identifier (format: xxx.xxx.xxx.xxx)
- TyreType: Type of tyre (Resilient With Soft & Bond, Resilient Without Soft & Bond, or Press-On)
- Brand: Brand name
- TreadPattern: Pattern identifier
- Size: Size category
- Quantity: Number of tyres to produce for this PID

### Sample Order Data
```csv
PID,TyreType,Brand,TreadPattern,Size,Quantity
101.201.301.401,Resilient-SoftBond,BrandA,Pattern1,Small,150
103.202.302.402,Resilient-Basic,BrandB,Pattern2,Medium,180
102.203.303.403,Press-On,BrandC,Pattern3,Large,165
```

### PID Structure
The PID consists of four sets of numbers separated by periods:
1. First set (xxx): Tyre Type Identifier
   - 101: Resilient with Soft & Bond
   - 102: Press-On
   - 103: Resilient Basic (without Soft & Bond)
2. Second set (xxx): Brand Identifier
   - 201: BrandA
   - 202: BrandB
   - 203: BrandC
3. Third set (xxx): Tread Pattern Identifier
   - 301: Pattern1
   - 302: Pattern2
   - 303: Pattern3
   - 304: Pattern4
4. Fourth set (xxx): Size Identifier
   - 401: Small
   - 402: Medium
   - 403: Large

## Production Tracking

### Serial Number System
- Serial Numbers (UUIDs) are generated when a tyre starts the building process
- Each Serial Number is unique and never repeated
- Format: UUID Version 4 (e.g., "0707dbd4-3da1-496e-b839-f2b71f945fd0")
- Used to track individual tyres through the production process

### Implementation Notes
1. Orders (CSV file) specify what needs to be produced
2. When production starts for a tyre:
   - Generate new UUID as Serial Number
   - Associate it with the corresponding PID
   - Track the tyre through the production process using this Serial Number
3. Serial Numbers should be stored in a separate production tracking system
4. Each Serial Number should appear only once in the entire system

## Technical Implementation Notes

### Resource Management
- Building stations operate as single-capacity resources
- Curing ovens operate as a pooled resource
- Bond wrapping stations are specific to tyre type and variant:
  - Press-On Bond Station: Used only for Press-On tyres
  - Resilient Bond Station: Used only for Resilient tyres with soft & bond

### Temperature Monitoring
- Continuous monitoring of compound temperatures required
- Different monitoring requirements for each tyre type and variant
- Temperature directly affects curing duration

### Process Flow Control
- Sequential processing through building steps
- Parallel processing possible in curing phase
- Temperature-dependent routing and timing logic
- Process flow varies based on tyre type and variant:
  - Full process for Resilient tyres with soft & bond
  - Simplified process for Resilient tyres without soft & bond
  - Press-On tyre specific process

## Future Enhancements and Considerations
1. Implementation of detailed temperature monitoring system
2. Addition of quality control checkpoints
3. Integration of maintenance schedules
4. Development of resource optimization algorithms
5. Implementation of order prioritization logic