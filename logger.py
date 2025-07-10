import sys
from multiprocessing import Lock
from datetime import datetime


class ConcurrentLogger:
    def __init__(self):
        self.lock = Lock()

    def log(self, message: str, prefix: str = ""):
        """Thread-safe logging with optional prefix"""
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            if prefix:
                print(f"[{timestamp}][{prefix}] {message}")
            else:
                print(f"[{timestamp}] {message}")
            sys.stdout.flush()


# Global logger instance
logger = ConcurrentLogger()
