# Solid Tyre Manufacturing Factory Simulation Documentation

## Project Overview
This project implements a SimPy-based simulation of a solid tyre manufacturing factory. The simulation models the complete manufacturing process for two types of solid tyres: Resilient Tyres and Press-On Tyres, including both building and curing processes.

## Manufacturing Process

### Process Flow
The manufacturing process is divided into two main phases:

1. Building Process
2. Curing Process

#### Building Process Steps
The complete building process sequence includes:
1. Wrap Inner Heal
2. Apply Bead
3. Wrap Heal
4. Wrap Bond
5. Wrap Soft
6. Wrap Tread
7. Press

#### Process Variations by Tyre Type

**Resilient Tyres**
- Follows the complete building process sequence
- Building Steps: Wrap Inner Heal → Apply Bead → Wrap Heal → Wrap Bond → Wrap Soft → Wrap Tread → Press

**Press-On Tyres**
- Follows a shortened building process
- Building Steps: Wrap Bond → Wrap Soft → Wrap Tread → Press

## Time and Temperature Parameters

### Building Process Timing
- Each building step duration: < 1 minute
- Variable duration due to manual labor (e.g., Wrap Inner Heal: 40-50 seconds per tyre)

### Curing Process Parameters

#### Temperature Requirements

**Resilient Tyres**
- Heal Temperature Range: 70°C - 100°C
- Soft Temperature Range: 80°C - 110°C

**Press-On Tyres**
- Soft Temperature Range: 80°C - 110°C

#### Curing Duration Rules
- Minimum duration: 40 minutes (at maximum healthy compound temperature)
- Duration increase: +10 minutes for every 10°C decrease in temperature

## Resource Capacity
- Building Process: 1 unit capacity per step
- Curing Process: 32 ovens available

## Order Management

### Order CSV Structure
The order data is stored in a CSV file with the following columns:
- PID: Product Identifier (format: xxx.xxx.xxx.xxx)
- TyreType: Type of tyre (Resilient or Press-On)
- Brand: Brand name
- TreadPattern: Pattern identifier
- Size: Size category
- Quantity: Number of tyres to produce for this PID

### Sample Order Data
```csv
PID,TyreType,Brand,TreadPattern,Size,Quantity
101.202.301.401,Resilient,BrandB,Pattern1,Small,186
101.203.302.401,Resilient,BrandC,Pattern2,Small,189
102.203.304.401,Press-On,BrandC,Pattern4,Small,167
```

### PID Structure
The PID consists of four sets of numbers separated by periods:
1. First set (xxx): Tyre Type Identifier
   - 101: Resilient
   - 102: Press-On
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
- Curing ovens operate as a pooled resource (32 units)

### Temperature Monitoring
- Continuous monitoring of compound temperatures required
- Different monitoring requirements for each tyre type
- Temperature directly affects curing duration

### Process Flow Control
- Sequential processing through building steps
- Parallel processing possible in curing phase
- Temperature-dependent routing and timing logic

## Future Enhancements and Considerations
1. Implementation of detailed temperature monitoring system
2. Addition of quality control checkpoints
3. Integration of maintenance schedules
4. Development of resource optimization algorithms
5. Implementation of order prioritization logic