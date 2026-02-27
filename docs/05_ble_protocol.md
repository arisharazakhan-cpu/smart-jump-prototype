# Bluetooth Low Energy Protocol Specification
Smart Jump System

1. Purpose
This document defines the bluetooth low energy protocol used between the mobile application and the two standard controllers. It specifies the connection model, gatt layout, message formats, acknowledgements, timeouts, and failure behavior required for mounted operation.

2. Roles and topology
2.1 Roles
The mobile application acts as the ble central.
Each standard controller acts as a ble peripheral.

2.2 Topology
The mobile application maintains two concurrent ble connections:
one to the left standard controller
one to the right standard controller

There is no direct radio link between standards in version 1. All coordination is driven by the app.

3. Connection lifecycle
3.1 Advertising
Each standard advertises a device name and short metadata:
device name: SmartJump <side> <group>
side is L or R
group is the configured group id

3.2 Pairing and provisioning
Pairing is defined as provisioning a group id and a shared secret key into each standard.

Pairing flow
Step 1. Put each standard into pairing mode using a physical action on the device.
Step 2. App scans for pairable devices and connects.
Step 3. App writes configuration to the device:
group id
side designation
shared secret key
Step 4. Device persists configuration and exits pairing mode.
Step 5. Device rejects future commands not authenticated for the configured group.

3.3 Reconnect
If the app disconnects, it attempts reconnect with exponential backoff.
During active motion, a disconnect triggers a stop timeout on the standard controller.

4. Gatt profile
4.1 Service
Service uuid: 6f1c0001-9d5b-4b43-9a2d-1a2f5f3b0001

4.2 Characteristics
Char A: Device Info, read
uuid: 6f1c0002-9d5b-4b43-9a2d-1a2f5f3b0001
payload fields
firmware_version (uint16)
device_id (uint32)
side (uint8)
group_id (uint8)
battery_percent (uint8)

Char B: Config, read write
uuid: 6f1c0003-9d5b-4b43-9a2d-1a2f5f3b0001
writes require authenticated config packets
payload fields
group_id (uint8)
side (uint8)
step_mm_default (uint16)
telemetry_hz (uint8)

Char C: Command, write without response
uuid: 6f1c0004-9d5b-4b43-9a2d-1a2f5f3b0001
used for time sensitive commands such as stop and move

Char D: Ack, notify
uuid: 6f1c0005-9d5b-4b43-9a2d-1a2f5f3b0001
used to acknowledge commands with a status code and sequence id

Char E: Telemetry, notify
uuid: 6f1c0006-9d5b-4b43-9a2d-1a2f5f3b0001
streams position and safety status at configured frequency

5. Message framing
All command and config messages use the same frame format.

5.1 Frame format
All integers are little endian.

offset  size  field
0       1     preamble, fixed 0xA5
1       1     protocol_version, fixed 0x01
2       1     msg_type
3       1     group_id
4       1     side
5       2     seq
7       4     timestamp_ms
11      1     payload_len
12      N     payload
12+N    8     auth_tag
20+N    1     crc8

5.2 Message types
0x01 command
0x02 config
0x03 status_request

5.3 Side field
0x01 left
0x02 right

6. Authentication and replay protection
6.1 Threat model for v1
The primary goal is preventing accidental control by unrelated devices and preventing replay of old commands in the arena environment.

6.2 Mechanism
Each device stores a shared secret key provisioned during pairing.
Each message includes a seq field.
The device maintains last_seq_accepted in nonvolatile memory or ram with periodic persistence.
A message is accepted only if seq is strictly greater than last_seq_accepted.

auth_tag is computed as:
truncated_hmac_sha256(key, bytes[preamble through payload]) first 8 bytes

crc8 is computed over the full frame excluding the crc byte.

7. Command set
7.1 Command payload format
For msg_type command, payload begins with command_id (uint8) followed by command specific fields.

7.2 Command list
0x10 stop
payload: command_id only

0x11 set_preset
payload:
command_id (0x11)
preset_id (uint8)

preset_id mapping
0x01 2ft0
0x02 2ft3
0x03 2ft6
0x04 2ft9
0x05 3ft0
0x06 3ft3
0x07 3ft6

0x12 move_increment
payload:
command_id (0x12)
axis_mask (uint8)
direction (int8) where 1 is up and -1 is down
steps_mm (uint16)

axis_mask bits
bit0 bottom
bit1 middle
bit2 top
for v1 mounted operation, app uses axis_mask 0b111 so all three stages on a standard move together per the spacing profile for the selected preset

0x13 set_step_default
payload:
command_id (0x13)
step_mm_default (uint16)

0x14 reset_fault
payload:
command_id (0x14)

8. Ack model
Because command writes use write without response, reliability is handled at the application layer with acks.

8.1 Ack packet
Ack notifications are emitted on Char D.

Ack payload fields
seq (uint16)
ack_code (uint8)
detail (uint8)

ack_code values
0x00 ok
0x01 rejected_auth
0x02 rejected_seq
0x03 rejected_group
0x04 rejected_state
0x05 fault_active
0x06 limit_triggered
0x07 overload_detected
0x08 timeout
0x09 internal_error

8.2 Ack timing
The device sends an ack within 100 ms for stop and within 250 ms for other commands.

If the app does not receive an ack within timeout, the app resends once.
If still no ack, the app issues stop to both devices and displays connection fault.

9. Telemetry model
Telemetry is emitted on Char E at telemetry_hz, default 10.

9.1 Telemetry payload
timestamp_ms (uint32)
state (uint8)
fault_code (uint8)
battery_percent (uint8)
position_bottom_mm (int32)
position_middle_mm (int32)
position_top_mm (int32)
target_bottom_mm (int32)
target_middle_mm (int32)
target_top_mm (int32)

state values
0 idle
1 homing
2 moving
3 fault
4 estop

fault_code values
0 none
1 top_limit
2 bottom_limit
3 desync_local
4 overload
5 comm_timeout
6 driver_fault
7 invalid_state

10. Communication loss behavior
10.1 Device side timeout
Each device maintains a watchdog timer while moving.
If no valid command or keepalive is received for comm_timeout_ms, default 800 ms, the device stops motion and enters fault state comm_timeout.

10.2 App side behavior
If either device telemetry stops for more than 400 ms during movement, the app issues stop to both devices and displays comm fault.

11. Stop behavior
Stop has priority over all commands.

Stop handling rules
If stop is received, device disables motor drivers immediately, then emits ack and telemetry state change.
If a physical stop is pressed, device disables motor drivers immediately and enters estop state. In estop, only reset_fault is accepted after physical release.

12. Preset execution contract
When the app sends set_preset, each standard computes target positions for bottom, middle, top based on the spacing profile table and local calibration offsets.

The device shall not begin motion unless:
no fault is active
not in estop
homing has completed

13. Versioning
protocol_version is incremented for breaking changes.
New commands must be backward compatible or gated by protocol_version check.

