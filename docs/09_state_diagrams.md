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
```

Device guarantees:
- stop always accepted  
- watchdog triggers fault while moving  
- fault is latched until reset  
- no motion allowed unless in idle_ready  

---

## 2. App Orchestrator State Machine

```mermaid
stateDiagram-v2
    [*] --> app_idle

    app_idle --> app_moving : set_preset
    app_moving --> app_idle : both_idle_ready

    app_moving --> app_fault : desync_detected
    app_moving --> app_fault : telemetry_timeout
    app_moving --> app_fault : device_fault
    app_moving --> app_fault : unexpected_ack

    app_fault --> app_idle : reset_sequence

    app_moving --> app_idle : user_stop
```

App guarantees:
- monitors both standards continuously  
- enforces desync tolerance  
- enforces telemetry timeout  
- issues stop to both on any anomaly  
- requires explicit reset after fault  