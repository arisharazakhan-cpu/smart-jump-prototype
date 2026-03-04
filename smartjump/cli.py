import argparse

def cmd_demo(args):
    from smartjump.demo import main as demo_main
    demo_main()
    return 0

def cmd_test(args):
    import subprocess, sys
    return subprocess.call([sys.executable, "-m", "pytest", "-q"])

def cmd_ui(args):
    from smartjump.ui import run_ui
    return run_ui(host=args.host, port=args.port, open_browser=(not args.no_browser))

def main(argv=None):
    p = argparse.ArgumentParser(prog="smartjump", description="Smart Jump prototype cli")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="run demo scenario")
    d.set_defaults(func=cmd_demo)

    t = sub.add_parser("test", help="run tests")
    t.set_defaults(func=cmd_test)

    u = sub.add_parser("ui", help="run local web ui")
    u.add_argument("--host", default="127.0.0.1")
    u.add_argument("--port", type=int, default=8000)
    u.add_argument("--no-browser", action="store_true")
    u.set_defaults(func=cmd_ui)

    args = p.parse_args(argv)
    return args.func(args)

if __name__ == "__main__":
    raise SystemExit(main())
