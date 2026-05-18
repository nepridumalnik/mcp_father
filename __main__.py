if __name__ == "__main__":
    try:
        from src import start

        start()
    except Exception as e:
        from sys import stderr

        print(f"Exception raised during execution: {e}", out=stderr)
        exit(-1)
