# Smart Jump Prototype

![Status](https://img.shields.io/badge/status-prototype-blue)
![CI](https://img.shields.io/badge/ci-passing-brightgreen)
![Architecture](https://img.shields.io/badge/design-layered-informational)
![Safety](https://img.shields.io/badge/safety-deterministic-critical)
![Target Build](https://img.shields.io/badge/hardware_budget-$2000%E2%80%93$4000-orange)

---

## Intelligent Jump Infrastructure for Mounted Training

**Transforming manual jump adjustment into synchronized, safety supervised motion.**

Smart Jump is a deterministic control architecture prototype that models Bluetooth operated jump standards for performance riders and professional training environments.

This repository focuses on synchronization guarantees, safety invariants, and layered fault enforcement before any physical hardware deployment.

---

## Live Demonstration

The animation below shows:

- Synchronized motion to preset height  
- Forced desynchronization during movement  
- Automatic coordinated fault stop  

![Smart Jump Demo](docs/demo.gif?raw=1)

---

## The Problem

In show jumping training, height changes occur constantly:

Warmup  
Progressive sets  
Competition height  
Technical combinations  

Today this requires:

- Dismount  
- Lift heavy poles  
- Reposition cups  
- Remount  
- Resume  

That interruption compounds across sessions.

It costs time.  
It breaks rhythm.  
It adds physical strain.  
It limits solo training.  

Riders training alone lose valuable momentum.  
Trainers with injuries face unnecessary strain.  
Facilities waste time that could be spent improving performance.

---

## The Shift

Smart Jump reframes height adjustment as infrastructure instead of labor.

Mounted preset selection → Coordinated motion → Supervised stop → Stable safe state.

Training should be limited by skill, not by logistics.

---

## System Concept

The system consists of:

- Two independent jump standards  
- One supervisory mobile orchestrator  
- Bluetooth Low Energy communication  
- Dual layer safety enforcement  

Each standard is a self contained safety device.

The mobile application acts as synchronization authority and fault supervisor.

---

## System Architecture

### End to End Data Flow

```mermaid
flowchart TB
    Rider[Rider Intent] --> App[Mobile App Orchestrator]

    App -->|BLE Write| CmdA[Command RX - Standard A]
    App -->|BLE Write| HbA[Heartbeat RX - Standard A]
    TelA[Telemetry TX - Standard A] -->|BLE Notify| App

    App -->|BLE Write| CmdB[Command RX - Standard B]
    App -->|BLE Write| HbB[Heartbeat RX - Standard B]
    TelB[Telemetry TX - Standard B] -->|BLE Notify| App

    CmdA --> DevA[Controller A State Machine]
    HbA --> DevA
    DevA --> MotA[Actuator A]

    CmdB --> DevB[Controller B State Machine]
    HbB --> DevB
    DevB --> MotB[Actuator B]
```

Detailed design artifacts:

- docs/09_state_diagrams.md  
- docs/11_system_architecture.md  

---

## Safety Model

Safety enforcement exists at two independent layers.

### Controller Layer Guarantees

- Motion only in idle_ready  
- Stop accepted in all states  
- Heartbeat timeout triggers fault  
- Fault latched until reset  
- Limit or overload triggers immediate halt  

### Orchestrator Layer Guarantees

- Continuous telemetry monitoring  
- Configurable desynchronization tolerance  
- Coordinated stop across both standards  
- Fault propagation from either device  
- Explicit reset required before reactivation  

If synchronization diverges beyond tolerance, both standards halt.

All invariants are validated through deterministic simulation tests.

---

## Business Impact

### Operational Efficiency

- Eliminates repeated mount and dismount cycles  
- Preserves training rhythm  
- Increases productive arena time  

### Physical Strain Reduction

- Removes repetitive lifting  
- Reduces instructor fatigue  
- Supports injured trainers  

### Facility Differentiation

- Technology forward positioning  
- Modernized training infrastructure  
- Premium branding signal  

---

## Financial Feasibility

Target build range: $2000 to $4000

Designed around practical component tradeoffs:

| Category | Design Focus |
|----------|--------------|
| Actuators | Load vs response speed |
| Encoders | Precision vs cost |
| MCU | ESP32 class |
| Power | Battery vs fixed supply |
| Mechanical | Backlash tolerance |
| Safety | Hard stops and limit switches |

Designed for serious private barns and professional facilities.

---

## Technical Capabilities

Current prototype includes:

- BLE contract modeling  
- Dual controller synchronization logic  
- Heartbeat supervision  
- Configurable desync tolerance  
- Coordinated stop behavior  
- Deterministic state machine validation  
- CI integrated safety testing  
- Installable CLI entry point  

---

## Running the Prototype

Install in editable mode:

```bash
python3 -m pip install -e ".[dev]"
```

Run automated tests:

```bash
smartjump test
```

Run the interactive simulation:

```bash
smartjump demo
```

The demo validates:

- Synchronized motion to preset  
- Continuous heartbeat supervision  
- Forced desynchronization detection  
- Coordinated fault stop  
- Deterministic state transitions  

---

## Development Discipline

Structured engineering workflow:

Issue → Branch → Merge Request → CI → Merge → Close  

Enforced through:

- Structured issue templates  
- Structured merge request template  
- No direct commits to main  
- Deterministic safety validation  

This mirrors real world safety conscious development practice.

---

## Roadmap

Phase 1 Deterministic Control Modeling Complete  
Phase 2 ESP32 Firmware Integration  
Phase 3 Actuator and Encoder Validation  
Phase 4 Mechanical Load Testing  
Phase 5 Mounted Field Trials  
Phase 6 Cost Optimization and Production Modeling  

---

Smart Jump represents the modernization of equestrian training infrastructure through synchronized, safety controlled automation.