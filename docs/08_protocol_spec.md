# Smart Jump Protocol Specification
Mounted-Operable Dual-Standard Control System

## 1. Purpose
This document defines the application-layer protocol between the mobile control authority and two standard controllers. It specifies message types, sequencing, acknowledgments, telemetry, safety timeouts, and versioning. The protocol is designed to support mounted operation, where communication failures must fail safe.

This protocol is transport-agnostic at the message level. The intended transport for v1 is Bluetooth Low Energy (BLE) using GATT characteristics. The message contract below remains valid if later migrated to Wi-Fi or another link.

## 2. System Roles and Control Model
2.1 Roles
Mobile App: control authority, coordinator, safety supervisor.
Standard Controller: real-time executor for one standard, owns three axes.

2.2 Topology
The app maintains two independent links:
App ↔ Left Standard
App ↔ Right Standard

No direct device-to-device synchronization is required in v1. Cross-standard synchronization is enforced by the app based on telemetry.

## 3. Safety and Correctness Goals
G1 Stop has highest priority and is always accepted.
G2 Any uncertainty results in safe stop (fault/estop), not continued motion.
G3 Commands are idempotent or safely repeatable.
G4 Replay protection prevents stale commands from being accepted.
G5 Motion is bounded by watchdogs and limit enforcement.

## 4. Timing Model
All timing values are defaults and configurable within safe bounds.

Keepalive interval (app to device): 100 ms to 250 ms
Device communication watchdog timeout: 800 ms
Telemetry emission rate: 10 Hz (every 100 ms) nominal
App telemetry timeout while moving: 400 ms
Ack timeout (app waiting for device): 250 ms to 400 ms

Safety contract
If the device does not receive a valid message (command or keepalive) within the watchdog timeout while moving, it must stop and enter fault state.

## 5. Transport Mapping (BLE v1)
This section defines the GATT characteristic intent without binding to specific UUIDs.

Device Info characteristic (read)
- static metadata: device id, firmware version, side, group id, battery

Command characteristic (write, low latency)
- carries Command Frames

Ack characteristic (notify)
- carries Ack Frames (one per accepted or rejected command)

Telemetry characteristic (notify)
- carries Telemetry Frames at configured rate

Config characteristic (read/write, authenticated)
- provisioning: group id, side, shared secret, tuning parameters

## 6. Protocol Versioning
The protocol includes protocol_version in every frame.

Version policy
- increment major version for breaking changes
- add new message types as backward compatible extensions where possible
- devices reject frames with unsupported protocol_version

## 7. Frame Format
All frames use a common envelope.

All integers are little-endian.

Envelope fields
- preamble: uint8 fixed 0xA5
- protocol_version: uint8
- frame_type: uint8
- group_id: uint8
- side: uint8 (1 left, 2 right)
- seq: uint16 (monotonic per device link)
- ts_ms: uint32 (sender local time, ms)
- payload_len: uint8
- payload: bytes[payload_len]
- auth_tag: bytes[8] truncated hmac
- crc8: uint8

Acceptance rules
- preamble must match
- protocol_version supported
- group_id must match configured group
- seq must be strictly greater than last accepted seq
- auth_tag must validate
- crc must validate

## 8. Authentication and Replay Protection
Threat objective
Prevent accidental control and replay of previously valid commands.

Mechanism
- shared secret provisioned during pairing
- auth_tag = first 8 bytes of hmac_sha256(secret, envelope_without_auth_and_crc)
- seq is monotonic; device stores last_seq_accepted
- device rejects frames with seq <= last_seq_accepted

## 9. Frame Types
frame_type values

0x01 COMMAND
0x02 CONFIG
0x03 STATUS_REQUEST
0x04 TELEMETRY (notify only)
0x05 ACK (notify only)

## 10. Command Payloads
COMMAND payload begins with command_id (uint8) then command-specific fields.

10.1 STOP (0x10)
Purpose
Immediate motion halt.

Payload
- command_id: 0x10

Device behavior
- disable motor drivers immediately
- cancel active motion plan
- transition to idle_ready if no fault, else remain fault
- emit ack ok

10.2 KEEPALIVE (0x11)
Purpose
Refresh comm watchdog while moving without changing targets.

Payload
- command_id: 0x11

Device behavior
- refresh watchdog timer
- emit ack optional (implementation choice)
Recommended
No ack required to reduce traffic.

10.3 SET_PRESET (0x12)
Purpose
Move axes to preset targets defined by device spacing profile and calibration offsets.

Payload
- command_id: 0x12
- preset_id: uint8

preset_id mapping
1 2ft0
2 2ft3
3 2ft6
4 2ft9
5 3ft0
6 3ft3
7 3ft6

Device behavior
- validate state is idle_ready
- compute targets from preset table and calibration
- start motion planner
- transition to moving
- emit ack ok or reject_state

10.4 MOVE_INCREMENT (0x13)
Purpose
Manual adjustment by step size for selected axes.

Payload
- command_id: 0x13
- axis_mask: uint8 (bit0 bottom, bit1 middle, bit2 top)
- direction: int8 (1 up, -1 down)
- step_mm: uint16

Device behavior
- compute targets as current + direction * step_mm for each selected axis
- enforce bounds
- execute motion plan

10.5 RESET_FAULT (0x14)
Purpose
Clear fault and require re-home before motion.

Payload
- command_id: 0x14

Device behavior
- if estop is active, reject_state
- clear fault
- transition to idle_not_homed

## 11. Ack Frame
ACK payload fields
- seq: uint16 (seq of the triggering command)
- ack_code: uint8
- detail: uint8 (optional)

ack_code values
0 ok
1 rejected_auth
2 rejected_seq
3 rejected_group
4 rejected_state
5 fault_active
6 limit_triggered
7 overload_detected
8 timeout
9 internal_error

Timing requirement
- stop: ack within 100 ms
- other commands: ack within 250 ms

## 12. Telemetry Frame
TELEMETRY payload fields
- ts_ms: uint32
- state: uint8
- fault_code: uint8
- battery_percent: uint8
- pos_bottom_mm: int32
- pos_middle_mm: int32
- pos_top_mm: int32
- tgt_bottom_mm: int32
- tgt_middle_mm: int32
- tgt_top_mm: int32

state values
0 idle_ready
1 moving
2 fault
3 estop
4 homing
5 idle_not_homed

fault_code values
0 none
1 top_limit
2 bottom_limit
3 overload
4 comm_timeout
5 motion_timeout
6 driver_fault
7 invalid_state
8 auth_rejected
9 desync_global

## 13. Global Synchronization Contract
The app enforces inter-standard synchronization.

During moving:
delta_mm = abs(left.pos_top_mm - right.pos_top_mm)

If delta_mm > desync_tolerance_mm:
- app sends stop to both
- app transitions to fault
- app records event in trace logs

Device handling
- device treats stop as highest priority
- device may optionally latch desync_global fault if stop includes a desync flag in future versions

## 14. Failure Handling Requirements
Communication loss while moving
- device watchdog expires, device enters comm_timeout fault
- app issues stop if telemetry missing beyond timeout

Command rejection
- device emits ack with rejection code
- app stops both on any unexpected rejection during moving

## 15. Compliance Checklist
An implementation is compliant if it meets:
- stop priority and immediate disable
- keepalive refreshes watchdog
- strict seq monotonicity enforcement
- telemetry timing and state accuracy
- ack emission and codes
- fault states latch and require reset

