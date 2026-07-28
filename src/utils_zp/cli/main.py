from .. import __version__


def main() -> int:
    print("utils_zp")
    print(f"version: {__version__}")
    print("commands:")
    print("  zpbashrc")
    print("  zpburn")
    print("  zprules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
