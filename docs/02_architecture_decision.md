# Architecture Decision Record
## ADR-001: Six Independent Actuators (Realistic Differential Spacing)

---

## Decision Summary

The Smart Jump System will use six independent linear actuators:
- Three per standard module (bottom, middle, top rail)
- Two standard modules (left and right)

Total actuators: six

This decision enables realistic rail spacing behavior as height increases and supports mounted operation with improved safety control.

---

## Rationale

### 1. Realistic Geometry

As jump height increases:
- The top rail must move the most
- The middle rail must move moderately
- The bottom rail should move minimally

Using independent actuators allows each rail to be positioned precisely to match expected vertical spacing.

A single-carriage lift would incorrectly raise all rails equally and create unrealistic lower gaps.

---

### 2. Mounted Safety

Independent stages allow:

- Individual stage position monitoring
- Individual stage fault detection
- Immediate halt if any actuator misbehaves
- Reduced mechanical coupling complexity

This reduces risk during mounted adjustment.

---

### 3. Software-Controlled Spacing

Preset heights will map to three target heights per side:

Example (illustrative only):

Preset: 3'0 (36 inches)
Top rail: 36"
Middle rail: ~26–28"
Bottom rail: ~12–16"

Actual spacing values will be defined in calibration tables.

---

### 4. Tradeoff Analysis

Pros:
- True geometric realism
- Easier mechanical fabrication
- Safer failure isolation
- Simplified debugging
- Independent calibration per stage

Cons:
- Increased cost (six actuators instead of two)
- Increased electrical complexity
- More wiring and control channels

---

## Implementation Impact

Mechanical:
- Three vertical guide rails per side or a shared multi-track rail
- Three independent carriages per side
- Six total actuator assemblies

Electrical:
- Six motor drivers
- Expanded IO requirements
- Possible use of multiple microcontrollers or IO expanders

Firmware:
- Multi-axis coordination
- Stage-specific fault monitoring
- Coordinated motion planning

---

## Budget Impact

Estimated increase over 2-actuator design:
+ $800 to $1500 depending on actuator choice

Total target budget remains within $2000–$4000 range.

---

## Status

Approved for Version 1 (Mounted-Capable Build)

