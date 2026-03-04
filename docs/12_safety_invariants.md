# Safety Invariants

This document lists the core safety invariants enforced by the Smart Jump control architecture.

These invariants ensure that the system halts safely whenever synchronization or communication guarantees are violated.

## Invariant 1 — Stop Is Always Accepted

A stop command must be honored immediately regardless of the current controller state.

This ensures riders or trainers can always halt motion without delay.

## Invariant 2 — Motion Only Starts From idle_ready

Movement commands are only accepted when the controller state is `idle_ready`.

This prevents unexpected actuator motion from transitional states.

## Invariant 3 — Heartbeat Loss Triggers Fault

If the orchestrator heartbeat is not received within the allowed interval, the controller transitions to a fault state and halts motion.

This protects against communication loss.

## Invariant 4 — Faults Are Latched

Once a fault occurs, the controller remains in the fault state until an explicit reset command is issued.

Automatic recovery is intentionally disabled to prevent unsafe restart.

## Invariant 5 — Desynchronization Stops Both Standards

If the difference between the two standards exceeds the configured tolerance, the orchestrator enters `app_fault` and issues stop commands to both devices.

This prevents uneven jump height during movement.

## Validation

These invariants are validated through deterministic simulation tests:

- tests/test_orchestrator.py
- tests/test_gatt_emulator.py

The simulation environment allows safety behavior to be verified before hardware integration.