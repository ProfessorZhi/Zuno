import sys


def main() -> int:
    payload = " ".join(sys.argv[1:]).strip()
    print(f"ZUNO_ECHO:{payload}" if payload else "ZUNO_ECHO:")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
