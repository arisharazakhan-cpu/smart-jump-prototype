# Firmware Control Specification
Smart Jump System – Standard Controller

1. Purpose
This document specifies the firmware architecture for a single standard controller (left or right). Each controller manages three actuators (bottom, middle, top) and exposes a BLE interface. The firmware must execute multi-axis motion safely, handle faults deterministically, and provide telemetry suitable for mounted operation.

2. Glossary
axis: one actuator stage, bottom or middle or top
standard: one physical jump side, left or right
app: the mobile control client
preset: a named jump height selection that maps to three target rail heights

3. Top-level architecture
The firmware is partitioned into five modules:

- ble_transport: gatt service, frame parsing, authentication, acks
- supervisor: state machine, command validation, fault handling
- axis_controller[3]: per-axis motion control loops
- safety: estop, limits, watchdog, overload detection
- persistence: calibration offsets, last_seq, configuration

4. Concurrency model
The controller runs a single real-time main loop at fixed tick rate.

Recommended tick: 200 Hz main loop
Telemetry: 10 Hz default

All motion decisions occur inside the tick loop to guarantee determinism.

No blocking operations are allowed inside the tick loop.
BLE events enqueue commands into a ring buffer processed by the supervisor.

5. State machines

5.1 Supervisor states
S0 BOOT
S1 UNPAIRED
S2 IDLE_NOT_HOMED
S3 HOMING
S4 IDLE_READY
S5 MOVING
S6 FAULT
S7 ESTOP

Allowed transitions
BOOT -> UNPAIRED if not configured
BOOT -> IDLE_NOT_HOMED if configured
UNPAIRED -> IDLE_NOT_HOMED after provisioning
IDLE_NOT_HOMED -> HOMING on command or auto-start
HOMING -> IDLE_READY on successful home
IDLE_READY -> MOVING on motion command
MOVING -> IDLE_READY on motion complete
ANY -> FAULT on safety fault
ANY -> ESTOP on physical stop
FAULT -> IDLE_NOT_HOMED on reset_fault
ESTOP -> FAULT on release + reset_fault

State invariants
- In MOVING, watchdog must be active
- In FAULT or ESTOP, motor drivers must be disabled
- In IDLE_READY, all axes must be within hold tolerance of their targets

5.2 Per-axis states
A0 DISABLED
A1 HOLD
A2 MOVING_UP
A3 MOVING_DOWN
A4 FAULT

Per-axis invariants
- In MOVING states, limit switches must be checked every tick
- If limit triggers, axis enters FAULT and requests supervisor fault

6. Safety invariants (must always hold)
I1: stop overrides motion. stop is processed immediately and disables drivers.
I2: no motion begins unless homing completed and no fault active.
I3: if comm watchdog expires during motion, system stops and enters FAULT.
I4: if any axis faults, all axes stop and enter FAULT.
I5: if physical estop active, all drivers disabled regardless of firmware state.

7. Watchdogs and timeouts
7.1 Communication watchdog
comm_timeout_ms default 800 ms
- active only in MOVING
- refreshed on any valid authenticated command or keepalive
- expiration triggers supervisor fault: COMM_TIMEOUT

7.2 Motion watchdog
Each motion command includes a computed max duration.
If motion exceeds duration + margin, enter fault: MOTION_TIMEOUT

8. Height and calibration model
8.1 Coordinate system
Positions are measured in millimeters from each axis home reference.
Home reference is the bottom travel limit position.

8.2 Preset table input
The preset table provides target rail heights above ground in inches.
The controller converts to mm and then to axis target positions using:
- mounting_reference_offset_mm per axis
- calibration_offset_mm per axis

Axis target position formula
target_mm = preset_height_mm - mounting_reference_offset_mm + calibration_offset_mm

mounting_reference_offset_mm accounts for how the actuator is mounted relative to ground and cup height.

calibration_offset_mm corrects per-device manufacturing and installation variation.

8.3 Persistence
calibration_offset_mm is stored in nonvolatile memory.
The preset table itself lives in firmware for v1, with optional override from app config in v2.

9. Multi-axis motion planning
9.1 Goals
- Move all three axes to targets with smooth acceleration and deceleration.
- Keep motion duration similar across axes to avoid visible skew.
- Enforce per-axis max speed and max acceleration.
- Maintain safe behavior under partial lag.

9.2 Planner strategy
Use a synchronized trapezoidal velocity profile:
- compute distance for each axis: di = target_i - current_i
- compute nominal max velocity vmax and acceleration amax
- compute time-to-complete for each axis under limits
- choose global motion duration T = max(Ti) across axes
- scale each axis velocity so all reach target at the same T

This yields coordinated arrival.

9.3 Planner outputs
For each axis:
- direction
- per-tick step schedule or PWM target
- expected end time
- hold tolerance band

9.4 Execution loop
At each tick:
- compute desired position along profile for each axis at time t
- compute delta to current position
- issue motor steps toward desired position subject to jerk-free constraints
- check limits, overcurrent, estop
- update estimated position
- if all axes within tolerance and velocity ~ 0, complete

10. Command handling

10.1 Command validation
Upon receiving a command frame:
- verify preamble and protocol_version
- verify group_id matches
- verify seq is increasing
- verify auth_tag
If any fails, send ack with rejection code and ignore.

10.2 set_preset
Preconditions:
- supervisor state is IDLE_READY
- no fault active
- not estop
Actions:
- look up top, middle, bottom target heights for preset_id
- compute targets in mm using calibration
- start multi-axis motion plan
- transition supervisor state to MOVING
- start comm watchdog

10.3 stop
Preconditions: any
Actions:
- disable all motor drivers immediately
- cancel motion plan
- transition to IDLE_READY if not faulted else remain FAULT
- emit ack and telemetry

10.4 reset_fault
Preconditions:
- supervisor state is FAULT or ESTOP
Actions:
- clear fault if estop physically released
- transition to IDLE_NOT_HOMED
- require homing before motion

11. Telemetry generation
Telemetry is published at telemetry_hz and on key transitions.

Telemetry includes:
- supervisor state
- fault code
- axis positions and targets
- battery percent
- watchdog status bits

12. Fault codes
F0 NONE
F1 TOP_LIMIT
F2 BOTTOM_LIMIT
F3 OVERLOAD
F4 COMM_TIMEOUT
F5 MOTION_TIMEOUT
F6 DRIVER_FAULT
F7 INVALID_STATE
F8 AUTH_REJECTED
F9 DESYNC_GLOBAL

13. Global desync handling (app driven)
The app monitors left and right standard top axis positions.
If |left_top - right_top| > tolerance:
- app sends stop to both
- app flags DESYNC_GLOBAL
Device records DESYNC_GLOBAL fault if stop received while in MOVING and desync flag is present in stop payload (future extension)

14. Testing hooks
Firmware shall include a diagnostic mode:
- simulate limit switches
- simulate current sensing
- log motion plan timings
- dump calibration offsets

