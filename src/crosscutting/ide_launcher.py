import subprocess
import sys
import logging
import os

logger = logging.getLogger(__name__)

def open_in_ide(file_path: str) -> bool:
    """Opens a file in PyCharm if available, otherwise falls back to system default."""
    try:
        # Try to open with PyCharm (assuming pycharm is in PATH)
        try:
            cmd = "pycharm" if sys.platform != "win32" else "pycharm64.exe"
            subprocess.Popen([cmd, file_path])
            return True
        except FileNotFoundError:
            # Fallback to system default
            logger.info("PyCharm not found in PATH, falling back to system default editor.")
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", file_path])
            else:
                subprocess.Popen(["xdg-open", file_path])
            return True
    except Exception as e:
        logger.warning(f"Failed to open file in IDE: {e}")
        return False
