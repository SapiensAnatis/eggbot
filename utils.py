import inspect
import re
from datetime import datetime

image_extensions = ["png", "jpg"]
_pattern = r"(https?:\/\/.*\.(?:"
# Generate the url regex pattern from supported extensions
# Example: if the list contains only png and jpg, should look like
# (https?:\/\/.*\.(?:png|jpg)"
for e in image_extensions:
    _pattern += rf"{e}|"

# replace the last | with the closing bracket
_pattern = _pattern[:-1] + ")"

_url_regex = re.compile(_pattern)

def log(message: str) -> None:
    frame = inspect.stack()[1]
    filename = frame.filenamepython

    now = datetime.now()
    time_str = now.strftime("%H:%M:%S")

    print(f"[{time_str}] [{filename}]: {message}")

def is_url(url: str) -> bool:
    # No need to return the actual match; since it will be the entire string provided
    # A simple test will suffice
    return (_url_regex.match(url) is not None)