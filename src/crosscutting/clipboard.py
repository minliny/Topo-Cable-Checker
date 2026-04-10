# [OPTIONAL_MODULE]
# This module provides optional external-environment integration.
# It is not part of the core port-checking flow.
# Behavior may depend on OS / desktop / local environment setup.

import subprocess
import sys
import logging

logger = logging.getLogger(__name__)

def copy_to_clipboard(text: str) -> bool:
    """Copies text to the system clipboard, returning True on success."""
    try:
        if sys.platform == "win32":
            process = subprocess.Popen(["clip"], stdin=subprocess.PIPE, text=True, encoding="utf-8")
            process.communicate(text)
            return process.returncode == 0
        elif sys.platform == "darwin":
            process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True, encoding="utf-8")
            process.communicate(text)
            return process.returncode == 0
        else:
            # Try xclip first, then xsel
            try:
                process = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True, encoding="utf-8")
                process.communicate(text)
                return process.returncode == 0
            except FileNotFoundError:
                process = subprocess.Popen(["xsel", "--clipboard", "--input"], stdin=subprocess.PIPE, text=True, encoding="utf-8")
                process.communicate(text)
                return process.returncode == 0
    except Exception as e:
        logger.warning(f"Failed to copy to clipboard: {e}")
        return False
