from __future__ import annotations

from ble.gatt_emulator import GattEmulator
from app.orchestrator import Orchestrator


def main() -> None:
    left = GattEmulator(controller_id="L")
    right = GattEmulator(controller_id="R")
    app = Orchestrator(left, right)

    print("Initial height L:", left.position_in)
    print("Initial height R:", right.position_in)
    print()
    print("Rider sets preset to 36 inches")

    app.set_preset(36)

    for step in range(300):
        app.heartbeat()
        app.tick(50)
        if step % 10 == 0 and app.state == "app_moving":
            print("t", step, "state", app.state, "L", left.position_in, "R", right.position_in)
        if app.state == "app_idle":
            break

    print("Final height L:", left.position_in)
    print("Final height R:", right.position_in)
    print("App state:", app.state)
    print()

    print("Simulating desync fault during move to 60 inches")
    app.set_preset(60)

    forced = False
    for step in range(300):
        app.heartbeat()
        app.tick(50)

        if not forced and app.state == "app_moving" and left.position_in < 40:
            left.position_in += 5
            forced = True
            print("forced desync at t", step, "L", left.position_in, "R", right.position_in)

        if step % 10 == 0:
            print("t", step, "state", app.state, "L", left.position_in, "R", right.position_in)

        if app.state == "app_fault":
            break

    print("App state after desync:", app.state)
    print("Final height L:", left.position_in)
    print("Final height R:", right.position_in)
    print("Events:", app.events)


if __name__ == "__main__":
    main()
