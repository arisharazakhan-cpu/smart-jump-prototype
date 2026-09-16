from ble.gatt_emulator import GattEmulator

def test_set_preset_reaches_target_with_heartbeat():
    dev = GattEmulator(controller_id="STD_A", position_in=24, target_in=24)
    events = []
    dev.on_notify = lambda m: events.append(m)

    dev.write_heartbeat({})
    dev.write_command({"type": "set_preset", "preset_in": 39})

    for _ in range(200):
        dev.write_heartbeat({})
        dev.tick(dt_ms=50)
        if dev.state == "idle_ready" and dev.position_in == 39:
            break

    assert dev.position_in == 39
    assert dev.state == "idle_ready"
    assert any(e.get("type") == "ack" and e.get("ack") == "set_preset" for e in events)

def test_heartbeat_timeout_faults_while_moving():
    dev = GattEmulator(controller_id="STD_A", position_in=24, target_in=24, heartbeat_timeout_ms=100)
    events = []
    dev.on_notify = lambda m: events.append(m)

    dev.write_heartbeat({})
    dev.write_command({"type": "set_preset", "preset_in": 60})

    # do not send heartbeat, tick until timeout
    for _ in range(20):
        dev.tick(dt_ms=50)
        if dev.state == "fault":
            break

    assert dev.state == "fault"
    assert any(e.get("type") == "fault" and e.get("fault") == "heartbeat_timeout" for e in events)


def test_stop_does_not_clear_latched_fault():
    dev = GattEmulator(controller_id="STD_A", state="fault", position_in=30, target_in=60)
    dev.write_command({"type": "stop"})
    assert dev.state == "fault"
    assert dev.target_in == 30


def test_move_is_rejected_outside_idle_ready():
    dev = GattEmulator(controller_id="STD_A", state="moving", position_in=30, target_in=40)
    events = []
    dev.on_notify = events.append
    dev.write_command({"type": "set_preset", "preset_in": 48})
    assert dev.target_in == 40
    assert any(event.get("fault") == "invalid_state" for event in events)
