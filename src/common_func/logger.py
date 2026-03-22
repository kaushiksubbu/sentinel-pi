# logger.py
from datetime import datetime
import os


def setup_log_dir(log_dir: str, log_filename: str = "default.log") -> str:
    """
    Ensures the log directory exists and returns full path to log file.

    Args:
        log_dir (str): Directory path to store logs
        log_filename (str): Name of the log file (default: default.log)

    Returns:
        str: Full path to the log file
    """
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, log_filename)


def log(message: str, log_file: str):
    """
    Writes timestamped log message to file and prints to console.

    Args:
        message (str): Message to log
        log_file (str): Path to log file
    """
    timestamp = datetime.now().isoformat()
    with open(log_file, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"{timestamp} - {message}")
