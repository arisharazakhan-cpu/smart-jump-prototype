# Hardware Layer

This folder represents the mechanical and electrical design for the automated jump standards.

Mechanical System:
- Vertical actuation mechanism (lead screw or geared motor)
- Encoder or linear position sensor
- Hard mechanical stops
- Weather-resistant enclosure
- Manual override capability

Electrical System:
- BLE microcontroller (ESP32 class)
- Motor driver stage (H-bridge or stepper driver)
- Current sensing for stall detection
- Limit switch inputs
- Battery or stable DC power system
- Emergency physical cutoff

Safety Requirements:
- Independent local stop on communication loss
- Mechanical limits beyond software limits
- Overcurrent shutdown
- Redundant failure handling

Software safety assumptions in this repository align with these constraints.
