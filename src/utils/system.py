import datetime
import socket
import os

def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_hostname() -> str:
    return socket.gethostname()

def create_directory(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"Directory created: {path}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"
