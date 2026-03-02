import argparse

from .magicid import MagicID


def main() -> None:
    """
    MagicID CLI entry point.
    Commands::
        new - generate some MUID. Can be used with -n flag. Then MUID will be generated N times.
        validate - validate a MUID
    """

    parser = argparse.ArgumentParser(prog="muid", description="MagicID CLI")
    sub = parser.add_subparsers(dest="cmd")

    gen = sub.add_parser("new", help="Generate MagicID")
    gen.add_argument("-n", type=int, default=1, help="Count")

    val = sub.add_parser("validate", help="Validate MagicID")
    val.add_argument("muid", type=str)

    args = parser.parse_args()

    if args.cmd == "new":
        for _ in range(args.n):
            print(MagicID())
    elif args.cmd == "validate":
        if MagicID.is_valid(args.muid):
            print(f"Valid: {args.muid}")
        else:
            print(f"Invalid: {args.muid}")
            raise SystemExit(1)
    else:
        parser.print_help()
