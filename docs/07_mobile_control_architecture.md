# Mobile Control Architecture Specification
Smart Jump System – Mounted Operation Control Authority

1. Purpose
This document defines the mobile application architecture, control authority model, synchronization logic, retry handling, and safety behavior during mounted operation.

The mobile app is the orchestration layer that coordinates two independent standard controllers and enforces inter-standard synchronization.

2. Architectural Overview

The app contains five major subsystems:

- BLE Manager
- Command Orchestrator
- Synchronization Monitor
- Safety Supervisor
- UI State Machine

The app is the authoritative coordinator for cross-standard behavior.

3. Connection Model

3.1 Device Representation

Each connected standard is represented internally as:

StandardDevice:
    device_id
    side (left or right)
    connection_state
    last_telemetry
    last_ack_seq
    last_seen_timestamp
    fault_state

3.2 Connection States

C0 DISCONNECTED
C1 SCANNING
C2 CONNECTING
C3 CONNECTED
C4 READY
C5 ERROR

Transitions:
DISCONNECTED -> SCANNING on user action
SCANNING -> CONNECTING when device selected
CONNECTING -> CONNECTED on BLE link success
CONNECTED -> READY after device info validated
ANY -> ERROR on protocol mismatch or auth failure

4. App Global State Machine

Global states:

A0 STARTUP
A1 NO_DEVICES
A2 PARTIAL_CONNECTED
A3 READY
A4 MOVING
A5 FAULT
A6 ESTOP_LOCKED

State transitions:

STARTUP -> NO_DEVICES after initialization
NO_DEVICES -> PARTIAL_CONNECTED when one standard connected
PARTIAL_CONNECTED -> READY when both standards connected and homed
READY -> MOVING on set_preset
MOVING -> READY when motion complete
ANY -> FAULT if either device reports fault
ANY -> ESTOP_LOCKED if user triggers emergency stop

State invariants:

- In MOVING, both standards must be in MOVING state.
- In READY, both standards must report IDLE_READY.
- In FAULT, motion commands are disabled.
- In ESTOP_LOCKED, only reset actions are allowed.

5. Command Orchestration Model

5.1 Sequence Strategy

The app maintains a global monotonic sequence counter.

Each command to a device includes:
- group_id
- side
- seq
- timestamp

The app tracks pending acks per device.

5.2 set_preset Execution Flow

Step 1: Validate both standards in READY state.
Step 2: Compute preset_id.
Step 3: Generate seq for left and right.
Step 4: Send set_preset to both standards within same event loop tick.
Step 5: Transition app state to MOVING.
Step 6: Start synchronization monitor.

If either ack fails:
- Send stop to both.
- Transition to FAULT.

6. Synchronization Monitor

The app continuously processes telemetry from both standards.

At telemetry rate (default 10 Hz):

left_top = left.telemetry.position_top_mm
right_top = right.telemetry.position_top_mm

delta = abs(left_top - right_top)

If delta > DESYNC_TOLERANCE_MM:
    issue stop to both
    transition to FAULT
    record desync event

DESYNC_TOLERANCE_MM default: 8 mm

7. Retry and Reliability Strategy

7.1 Ack Timeout

For each command sent:
- start timer (default 300 ms)
- if ack not received:
    resend once
- if still no ack:
    issue stop to both
    transition to FAULT

7.2 Telemetry Timeout

If no telemetry from either device for > 400 ms while MOVING:
    issue stop to both
    transition to FAULT

8. Emergency Stop Behavior

8.1 UI Stop

Large stop button always visible in MOVING state.

On press:
- immediately send stop to both devices
- transition to ESTOP_LOCKED
- disable further motion until reset

8.2 Device-Initiated Stop

If a device enters ESTOP or FAULT state:
- app transitions to FAULT
- disable motion commands
- require user acknowledgment

9. Lock Mode for Mounted Safety

During MOVING:
- Disable preset buttons
- Disable incremental controls
- Only stop remains active

After completion:
- Require explicit confirmation before next motion

This prevents accidental double-tap motion while mounted.

10. Preset Mapping

The app does not compute rail geometry.
It sends preset_id only.

Geometry resolution occurs inside each standard firmware based on spacing profile and calibration.

This reduces BLE payload size and avoids mismatched geometry logic.

11. Fault Handling UX

Fault screen displays:
- which standard faulted
- fault code
- recommended action

User must:
- acknowledge fault
- physically inspect hardware if needed
- press reset
- re-home system

12. Future Extensions

- Multi-jump arena mode
- Height history logging
- Training session analytics
- Adjustable spacing curves
- Secure multi-user profiles

