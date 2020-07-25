import inspect
from datetime import datetime

def log(message: str):
    frame = inspect.stack()[1]
    filename = frame.filename

    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")

    print(f"[{time_str}] [{filename}]: {message}")
