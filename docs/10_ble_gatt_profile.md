# BLE GATT Profile

This is the Bluetooth Low Energy interface contract between the mobile app and a single standard controller.

Goal: allow the app to discover a controller, read its status, command a preset move, and receive telemetry via notifications.

---

## Service

SmartJump service UUID (128 bit)
Replace with real UUIDs before hardware build

SERVICE_UUID = 12345678-1234-5678-1234-56789abcdef0

---

## Characteristics

1. Command RX
UUID = 12345678-1234-5678-1234-56789abcdef1
Properties: Write Without Response
Use: app sends commands to the controller

2. Telemetry TX
UUID = 12345678-1234-5678-1234-56789abcdef2
Properties: Notify
Use: controller streams state updates and faults

3. Heartbeat RX
UUID = 12345678-1234-5678-1234-56789abcdef3
Properties: Write Without Response
Use: app sends keepalive pings so the controller can fail safe if the link drops

4. Device Info
UUID = 12345678-1234-5678-1234-56789abcdef4
Properties: Read
Use: model, firmware version, capabilities

---

## Message Envelope

All payloads are JSON for prototype simplicity.
Later you can switch to CBOR with the same field names.

All messages include
type: string
seq: int
ts_ms: int
controller_id: string

---

## Commands

set_preset
stop
home
reset_fault

Example set_preset
{
  "type": "set_preset",
  "seq": 101,
  "ts_ms": 1700000000000,
  "controller_id": "STD_A",
  "preset_in": 39,
  "speed": "normal"
}

Example stop
{
  "type": "stop",
  "seq": 102,
  "ts_ms": 1700000000100,
  "controller_id": "STD_A"
}

---

## Telemetry

state_update
fault
ack

Example state_update
{
  "type": "state_update",
  "seq": 201,
  "ts_ms": 1700000000123,
  "controller_id": "STD_A",
  "state": "moving",
  "position_in": 27,
  "target_in": 39,
  "fault": null
}

Example fault
{
  "type": "fault",
  "seq": 210,
  "ts_ms": 1700000000456,
  "controller_id": "STD_A",
  "fault": "heartbeat_timeout"
}

---

## Timing Rules

Heartbeat period: 200 ms
Heartbeat timeout: 700 ms
If heartbeat timeout occurs while moving, controller must stop motion and enter fault

Telemetry notify rate
moving: 20 Hz
idle: 2 Hz

