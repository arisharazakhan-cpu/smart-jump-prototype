# Smart Jump Prototype

![Status](https://img.shields.io/badge/status-prototype-blue)
![CI](https://img.shields.io/badge/ci-passing-brightgreen)
![Language](https://img.shields.io/badge/python-3.10+-blue)
![Architecture](https://img.shields.io/badge/architecture-layered-informational)
![Safety Model](https://img.shields.io/badge/safety-deterministic-critical)

Mounted Bluetooth Control System for Automated Jump Standards

A safety-focused, deterministic prototype modeling dual jump standards controlled via Bluetooth Low Energy from a mounted rider interface.

---

## System Overview

This project models a dual-actuator jump system where height is adjusted remotely without dismounting.

Each jump standard contains an independent controller responsible for:

- Motion state machine
- Height tracking
- Heartbeat timeout enforcement
- Fault latching
- Stop gating

A mounted mobile application acts as an orchestrator and enforces:

- Synchronized preset commands
- Continuous heartbeat transmission
- Real-time telemetry monitoring
- Desynchronization detection
- Coordinated stop on anomaly
- Explicit reset after fault

The firmware layer is currently modeled via deterministic emulation to ensure behavior is fully testable before hardware implementation.

---

## Architecture

High-Level Flow:

Rider Intent  
→ Mobile App Orchestrator  
→ BLE Command + Heartbeat  
→ Controller State Machine (Left + Right)  
→ Actuator Model  

Architecture documentation:

- docs/11_system_architecture.md  
- docs/09_state_diagrams.md  

Layered Structure:

- app/ – Orchestrator logic  
- ble/ – GATT emulator (firmware model)  
- tests/ – Safety validation  
- docs/ – Diagrams and design documentation  
- firmware/ – Planned embedded layer  
- hardware/ – Mechanical and electrical planning  
- mobile_app/ – Future mounted UI implementation  
- test_artifacts/ – Validation logs  

---

## Safety Model

The system enforces strict motion constraints:

- No motion unless in idle_ready
- Heartbeat timeout triggers controller fault
- Desynchronization triggers coordinated app fault
- Coordinated stop issued to both standards
- Faults are latched until explicit reset
- Motion gating exists at both app and controller layers

Desync tolerance is configurable per build.

All safety behavior is validated via deterministic simulation tests.

---

## Validation

Run unit tests:

python3 -m pytest -q

Run demonstration scenario:

python3 demo_run.py

Demo includes:

- Normal synchronized motion
- Desync fault during movement
- Coordinated stop enforcement

---

## Development Workflow

This repository follows a disciplined workflow:

Issue → Feature Branch → Merge Request → CI → Merge → Issue Auto-Close

Enforced via:

- Structured issue templates
- Structured merge request template
- No direct commits to main
- CI pipeline validation

This ensures safety-impacting logic remains traceable and reviewable.

---

## Project Status

Prototype complete for:

- BLE contract modeling
- Dual-controller synchronization
- Heartbeat enforcement
- Desync detection
- Configurable tolerance
- CI integration
- Structured engineering workflow

Next milestone: Replace emulator with ESP32 firmware and physical actuator hardware.

