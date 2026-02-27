import argparse
import sys


def cmd_demo(args) -> int:
    from smartjump.demo import main as demo_main
    demo_main()
    return 0


def cmd_test(args) -> int:
    import subprocess
    return subprocess.call([sys.executable, "-m", "pytest", "-q"])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="smartjump")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_demo = sub.add_parser("demo", help="Run the mounted demo scenario")
    p_demo.set_defaults(func=cmd_demo)

    p_test = sub.add_parser("test", help="Run the test suite")
    p_test.set_defaults(func=cmd_test)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
