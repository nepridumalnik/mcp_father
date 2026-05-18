if __name__ == "__main__":
    try:
        import sys
        from .src.cli import MCPFatherCLI

        sys.path.append(".")
        cli = MCPFatherCLI()
        cli.execute()
    except Exception as e:
        print(f"Failed during execution: {e}", out=sys.stderr)
        exit(-1)
