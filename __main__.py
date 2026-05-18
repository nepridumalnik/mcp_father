import sys
from pathlib import Path


def main() -> int:
    if __package__:
        from .src.cli import MCPFatherCLI
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from src.cli import MCPFatherCLI

    cli = MCPFatherCLI()
    cli.execute()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        print(f"Failed during execution: {e}", file=sys.stderr)
        raise SystemExit(1)
