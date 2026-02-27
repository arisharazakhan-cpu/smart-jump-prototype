# Software Architecture Specification
## Smart Jump System – Distributed Control Model

---

# 1. System Model

The Smart Jump System is a distributed real-time control system composed of:

- One mobile control client (BLE Central)
- Two standard controllers (BLE Peripherals)
- Six actuator control loops (3 per standard)

The system must coordinate motion across all six actuators while maintaining safety guarantees.

---

# 2. Logical Components

## 2.1 Mobile Application (Control Authority)

Responsibilities:
- User interface (preset selection, stop, lock)
- Command broadcasting to both standards
- Synchronization monitoring
- Desynchronization detection
- Fault state display
- Configuration and calibration management

The app acts as the authoritative command source.

---

## 2.2 Standard Controller (Left / Right)

Each standard contains:

- Local actuator controllers (3)
- Local safety supervisor
- BLE communication layer
- Hardware emergency interface

Each standard must be able to:
- Execute coordinated stage movement
- Halt immediately on local fault
- Report telemetry continuously

---

# 3. Control Architecture

The system operates under a master-command, distributed-execution model.

Flow:

1. App computes target rail positions from preset.
2. App sends structured command to both standards.
3. Each standard computes local actuator targets.
4. Actuator controllers execute synchronized motion.
5. Standards stream telemetry to app.
6. App monitors synchronization.
7. Any fault triggers global halt.

---

# 4. Actuator Control Loop

Each of the six actuators runs an independent control loop.

Loop components:
- Position reference
- Current position
- Motion planner (ramped profile)
- Safety monitor (limit, overcurrent, timeout)

Pseudo-loop:

while moving:
    if limit_triggered: fault_stop()
    if overcurrent: fault_stop()
    step_motor()
    update_position()
    report_telemetry()

---

# 5. Multi-Axis Coordination Strategy

There are two coordination layers:

Layer 1 – Intra-Standard Coordination  
Ensures bottom, middle, and top actuators on a single standard move according to target table.

Layer 2 – Inter-Standard Synchronization  
Ensures left and right standards maintain positional parity.

Desync threshold defined as:
absolute(left_top - right_top) > tolerance

If exceeded:
- immediate stop broadcast

---

# 6. Fault Model

Fault states include:

- Travel limit exceeded
- Desynchronization threshold breach
- Communication timeout
- Motor driver failure
- Emergency stop activation

Upon fault:
- Motion stops
- Actuators disabled
- Fault code transmitted
- System requires explicit reset

---

# 7. Communication Protocol Model

BLE communication uses:

- Structured command packets
- Sequence numbers
- Acknowledgment mechanism
- Telemetry notifications

Command types:
- SET_PRESET
- MOVE_INCREMENT
- STOP
- CALIBRATE
- QUERY_STATUS

---

# 8. Safety Priority Hierarchy

Priority 1: Hardware emergency stop  
Priority 2: Firmware fault detection  
Priority 3: App desync detection  

No lower layer may override a higher safety layer.

---

# 9. Real-Time Considerations

- Movement updates must occur at fixed time intervals.
- Telemetry must be streamed at consistent frequency (e.g., 10 Hz).
- Communication latency must not exceed safe threshold during motion.

---

# 10. Scalability Considerations

Future system versions may:

- Support multiple jumps
- Support arena-wide group addressing
- Support configurable motion curves
- Log movement analytics

