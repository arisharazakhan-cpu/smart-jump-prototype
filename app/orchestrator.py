"""
Mounted App Orchestrator

Manages two BLE controller connections (left and right standards)
Enforces synchronization, heartbeat, and fail safe logic.
"""

from typing import Dict, Any, Optional
from ble.gatt_emulator import GattEmulator


class Orchestrator:
    def __init__(self, left: GattEmulator, right: GattEmulator, desync_tolerance_in: int = 1):
        self.left = left
        self.right = right
        self.desync_tolerance_in = desync_tolerance_in

        self.state = "app_idle"
        self.events = []

        self.left.on_notify = self._handle_left
        self.right.on_notify = self._handle_right

        self.left_last: Optional[Dict[str, Any]] = None
        self.right_last: Optional[Dict[str, Any]] = None

    def set_preset(self, height_in: int) -> None:
        if self.state != "app_idle":
            return
        self.state = "app_moving"
        self.left.write_command({"type": "set_preset", "preset_in": height_in})
        self.right.write_command({"type": "set_preset", "preset_in": height_in})

    def heartbeat(self) -> None:
        self.left.write_heartbeat({})
        self.right.write_heartbeat({})

    def tick(self, dt_ms: int = 50) -> None:
        self.left.tick(dt_ms)
        self.right.tick(dt_ms)
        self._check_desync()
        self._check_completion()

    def stop_all(self) -> None:
        # stop commands only. caller decides orchestrator state.
        self.left.write_command({"type": "stop"})
        self.right.write_command({"type": "stop"})

    def user_stop(self) -> None:
        self.stop_all()
        self.state = "app_idle"

    def _handle_left(self, msg: Dict[str, Any]) -> None:
        self.left_last = msg
        self._process(msg)

    def _handle_right(self, msg: Dict[str, Any]) -> None:
        self.right_last = msg
        self._process(msg)

    def _process(self, msg: Dict[str, Any]) -> None:
        if msg.get("type") == "fault":
            self._enter_fault("device_fault")

    def _check_completion(self) -> None:
        if self.state == "app_moving":
            if self.left.state == "idle_ready" and self.right.state == "idle_ready":
                self.state = "app_idle"

    def _check_desync(self) -> None:
        if self.state != "app_moving":
            return
        diff = abs(self.left.position_in - self.right.position_in)
        if diff > self.desync_tolerance_in:
            self._enter_fault("desync_detected")

    def _enter_fault(self, reason: str) -> None:
        if self.state == "app_fault":
            return
        self.stop_all()
        self.state = "app_fault"
        self.events.append({"type": "app_fault", "reason": reason})
