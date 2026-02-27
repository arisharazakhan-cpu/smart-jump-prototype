# System Requirements Specification
## Smart Jump System – Mounted-Operable Vertical Adjustment Platform

---

# 1. Functional Requirements

## 1.1 System Scope

FR-001  
The system shall control one vertical jump consisting of three rails and six cups.

FR-002  
The system shall consist of two synchronized standard modules (left and right), each mechanically and electronically independent but logically paired.

---

## 1.2 Mounted Operation

FR-003  
The system shall allow a rider to initiate height changes while mounted via a mobile application.

FR-004  
Height changes shall occur without requiring manual intervention at the standards during motion.

FR-005  
Motion shall remain stable and controlled under expected training loads.

Acceptance Criteria:  
- Height commands execute successfully while rider remains mounted.  
- No uncontrolled oscillation or visible instability during motion.

---

## 1.3 Height Control

FR-006  
The system shall support preset height selections at minimum:

- 2'0  
- 2'3  
- 2'6  
- 2'9  
- 3'0  
- 3'3  
- 3'6  

FR-007  
Each preset shall correspond to a calibrated and verified physical top-rail height.

FR-008  
The system shall support incremental fine adjustment via configurable movement steps.

FR-009  
The system shall store calibration mappings in non-volatile memory.

Acceptance Criteria:  
- Repeated selection of the same preset results in consistent physical height within defined tolerance.  
- Incremental adjustments produce measurable and repeatable movement.

---

## 1.4 Synchronization

FR-010  
Left and right standard modules shall move in synchronized motion during height adjustment.

FR-011  
The system shall continuously monitor positional difference between modules during active motion.

FR-012  
If positional difference exceeds defined tolerance, both modules shall halt immediately.

Acceptance Criteria:  
- During commanded movement, left/right height difference remains within tolerance band.  
- Artificially induced desynchronization triggers system halt.

---

## 1.5 Communication

FR-013  
The system shall use Bluetooth Low Energy for wireless communication between the mobile application and both standard modules.

FR-014  
Each module shall support a configurable group identifier to ensure only paired modules respond to commands.

FR-015  
Modules shall reject commands that do not match the configured group identifier.

FR-016  
If wireless communication is lost during active motion, both modules shall halt within a defined timeout period.

Acceptance Criteria:  
- Modules do not respond to unauthorized or mismatched control attempts.  
- Communication loss during movement results in safe stop behavior.

---

# 2. Safety Requirements

## 2.1 Emergency Stop

SR-001  
The mobile application shall provide an emergency stop control that halts both modules immediately.

SR-002  
Each standard module shall include a hardware-level emergency stop input that disables motor drive independent of firmware state.

Acceptance Criteria:  
- Stop from app halts both modules within defined response time.  
- Hardware stop disables motion even if firmware is unresponsive.

---

## 2.2 Travel Limits

SR-003  
Each module shall include upper and lower travel limit detection.

SR-004  
Triggering a travel limit shall immediately halt motion and enter a fault state.

Acceptance Criteria:  
- Physical contact with travel limit prevents overtravel.  
- Fault state requires reset before further motion.

---

## 2.3 Fail-Safe Behavior

SR-005  
The mechanical drive system shall prevent uncontrolled descent in the event of power loss.

SR-006  
The system shall default to a non-moving state under any detected fault condition.

SR-007  
The design shall include a mechanical overload release mechanism to mitigate risk under extreme downward force.

Acceptance Criteria:  
- Power removal while holding position does not result in free fall.  
- Overload condition results in controlled release or halt behavior.

---

# 3. Performance Requirements

PR-001  
Motion speed shall be controlled and visibly smooth.

PR-002  
Acceleration and deceleration shall be ramped to prevent abrupt mechanical transitions.

PR-003  
System shall support repeated motion cycles without positional drift exceeding defined tolerance.

Acceptance Criteria:  
- No visible jerk at motion start or stop.  
- Repeatability verified across multiple preset cycles.

---

# 4. Structural Requirements

STR-001  
Standard modules shall mount securely to conventional jump standards.

STR-002  
Structural elements shall resist bending or torsional deformation under expected training loads.

STR-003  
Rail and carriage assemblies shall maintain alignment across full travel range.

Acceptance Criteria:  
- No visible deflection affecting synchronization.  
- Smooth travel across full height range.

---

# 5. Cost Constraints

COST-001  
Total prototype build cost shall remain within $2,000–$4,000.

COST-002  
Major components shall be commercially available and reproducible.

Acceptance Criteria:  
- Bill of materials includes supplier references and unit pricing.  
- Total cost documented within target range.

---

# 6. Out of Scope (Version 1)

- Formal regulatory certification  
- Competition approval compliance  
- Long-term outdoor environmental hardening  
- Multi-fence arena network orchestration  

---

# 7. Definition of Completion

The system is considered complete when:

- Preset heights move both standards reliably  
- Emergency stop behavior is deterministic  
- Desynchronization detection functions correctly  
- Calibration produces consistent measurable heights  
- Mounted operation is demonstrated under controlled conditions  
- All requirements above have documented validation evidence  

