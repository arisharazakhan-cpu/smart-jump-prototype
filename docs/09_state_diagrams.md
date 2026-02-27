# Smart Jump State Machine Diagrams

This document defines the formal state machines for:

1. Standard Controller (device firmware)
2. Mobile App Orchestrator (control authority)

---

## 1. Standard Controller State Machine

```mermaid
stateDiagram-v2
    [*] --> idle_ready

    idle_ready --> moving : set_preset / move_increment
    moving --> idle_ready : motion_complete

    moving --> fault : comm_timeout
    moving --> fault : overload
    moving --> fault : limit_triggered
    moving --> fault : driver_fault

    idle_ready --> fault : internal_error

    fault --> idle_not_homed : reset_fault
    idle_not_homed --> homing : home_command
    homing --> idle_ready : homing_complete

    moving --> idle_ready : stop
    idle_ready --> idle_ready : stop
    fault --> fault : stop
