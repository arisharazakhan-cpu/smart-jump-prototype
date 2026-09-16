from ble.gatt_emulator import GattEmulator
from app.orchestrator import Orchestrator
import pytest

def test_synchronized_move_reaches_target():
    left = GattEmulator(controller_id="L")
    right = GattEmulator(controller_id="R")
    app = Orchestrator(left, right)

    app.set_preset(36)

    for _ in range(200):
        app.heartbeat()
        app.tick(50)
        if app.state == "app_idle":
            break

    assert left.position_in == 36
    assert right.position_in == 36
    assert app.state == "app_idle"

def test_desync_triggers_fault():
    left = GattEmulator(controller_id="L")
    right = GattEmulator(controller_id="R")
    app = Orchestrator(left, right)

    app.set_preset(40)

    for i in range(50):
        app.heartbeat()
        app.tick(50)
        if i == 10:
            left.position_in += 5  # force desync
        if app.state == "app_fault":
            break

    assert app.state == "app_fault"


def test_height_outside_safe_range_is_rejected():
    app = Orchestrator(GattEmulator(controller_id="L"), GattEmulator(controller_id="R"))
    with pytest.raises(ValueError):
        app.set_preset(100)


def test_user_stop_does_not_clear_app_fault():
    app = Orchestrator(GattEmulator(controller_id="L"), GattEmulator(controller_id="R"))
    app.state = "app_fault"
    app.user_stop()
    assert app.state == "app_fault"
