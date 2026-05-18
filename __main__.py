import sys
import logging
from pathlib import Path


def main() -> int:
    if __package__:
        from .src.cli import MCPFatherCLI
    else:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from src.cli import MCPFatherCLI

    cli = MCPFatherCLI()
    return cli.execute()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        logging.getLogger("mcp_father").exception("Failed during execution")
        print(f"Failed during execution: {e}", file=sys.stderr)
        raise SystemExit(1)
