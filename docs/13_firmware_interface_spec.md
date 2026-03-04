# Firmware Interface Spec

This document defines the controller interface used by the mobile orchestrator and the simulation.

The goal is a replaceable contract: simulated GATT today, ESP32 firmware tomorrow, without rewriting safety logic.

## Transport

Bluetooth Low Energy using three characteristics per jump standard.

Command writes and heartbeat writes are Write Without Response.
Telemetry is Notify.

## Characteristics

Command RX
Used by the orchestrator to request motion and stop.

Heartbeat RX
Used by the orchestrator to prove liveness. Missing heartbeat triggers a controller fault.

Telemetry TX
Used by the controller to publish state and position updates.

## Command RX payload

JSON object with a required field `type`.

Set preset
`{"type":"set_preset","preset_in":60}`

Stop
`{"type":"stop"}`

Reset
`{"type":"reset"}`

Notes
The controller must accept `stop` in all states.
The controller must only accept `set_preset` when idle_ready.

## Heartbeat RX payload

JSON object. Contents are ignored.
`{}`

The orchestrator is expected to send heartbeats continuously while the system is active.

## Telemetry TX payload

JSON object with the following fields.

Required fields
`type` always equals `telemetry`
`controller_id` stable identifier for the standard
`state` one of `idle_ready`, `moving`, `fault`
`position_in` current height position in inches
`target_in` current target position in inches
`fault_reason` null when not faulted, otherwise a short string reason
`seq` monotonically increasing integer sequence number
`ts_ms` controller timestamp in milliseconds

Example
`{"type":"telemetry","controller_id":"L","state":"moving","position_in":42,"target_in":60,"fault_reason":null,"seq":18,"ts_ms":123450}`

## Controller state requirements

States
`idle_ready`
`moving`
`fault`

Transitions
`idle_ready` to `moving` on valid `set_preset`
`moving` to `idle_ready` when target reached
`moving` to `idle_ready` on `stop`
Any state to `fault` on safety trigger
`fault` remains latched until `reset`

## Safety triggers

Heartbeat timeout
If heartbeat is not received within the configured timeout, transition to fault and stop motion.

Limit switch hit
If a limit switch indicates unsafe travel, transition to fault and stop motion.

Encoder error
If encoder feedback is invalid or inconsistent, transition to fault and stop motion.

## Orchestrator expectations

The orchestrator sends the same preset to both standards.
The orchestrator monitors telemetry from both standards.
If the standards diverge beyond desync tolerance, the orchestrator issues stop to both and enters `app_fault`.

## Test mapping

Simulation tests validating these behaviors live under:
`tests/`
`simulation/`

This contract is intended to be implemented in ESP32 firmware without changing the higher level control logic.
