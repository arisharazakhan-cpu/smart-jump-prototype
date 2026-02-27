# Firmware Layer

Target platform: ESP32 class BLE microcontroller

Purpose:
Implements the SmartJump controller logic deployed on each jump standard.

Responsibilities:
- Expose BLE GATT profile defined in docs/10_ble_gatt_profile.md
- Maintain deterministic motion state machine
- Enforce heartbeat watchdog timeout
- Latch faults until explicit reset
- Prevent motion unless in idle_ready state

Core subsystems (planned):
- BLE stack (ESP-IDF or equivalent)
- Motor control driver abstraction
- Encoder interface for height tracking
- Limit switch interrupt handling
- Overcurrent detection
- Fault persistence

Real-time considerations:
- Motion loop isolated from BLE ISR
- Watchdog timer independent of app logic
- State machine transitions atomic

The behavior of this firmware is currently modeled in:
ble/gatt_emulator.py

Future milestone:
Replace emulator with real BLE transport layer while keeping orchestrator logic unchanged.
