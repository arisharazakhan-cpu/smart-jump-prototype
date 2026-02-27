# System Architecture

This project models a mounted Bluetooth control system for an automated jump.

The implementation is structured as layered contracts so real hardware can replace simulated components without rewriting the control logic.

---

## End to end data flow

```mermaid
flowchart TB
    Rider[Rider mounted UI intent] --> App[Mobile App Orchestrator]
    App -->|BLE WriteWithoutResponse| Cmd[Command RX characteristic]
    App -->|BLE WriteWithoutResponse| Hb[Heartbeat RX characteristic]
    Tel[Telemetry TX characteristic] -->|BLE Notify| App

    Cmd --> Dev[Controller Firmware State Machine]
    Hb --> Dev
    Dev --> Mot[Motor + Encoder + Limit Switches]

    subgraph Standard A
        CmdA[Command RX] --> DevA[Controller A]
        HbA[Heartbeat RX] --> DevA
        DevA --> TelA[Telemetry TX]
        DevA --> MotA[Actuator A]
    end

    subgraph Standard B
        CmdB[Command RX] --> DevB[Controller B]
        HbB[Heartbeat RX] --> DevB
        DevB --> TelB[Telemetry TX]
        DevB --> MotB[Actuator B]
    end

    App --> CmdA
    App --> HbA
    TelA --> App

    App --> CmdB
    App --> HbB
    TelB --> App
