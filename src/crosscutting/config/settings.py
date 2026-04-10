import os
from pathlib import Path

class Settings:
    def __init__(self):
        # Resolve the project root dynamically. 
        # Since this file is in src/crosscutting/config/, the project root is 3 levels up.
        _current_dir = Path(__file__).resolve().parent
        _project_root = _current_dir.parent.parent.parent
        
        self.BASE_DIR = os.getenv("CHECKTOOL_BASE_DIR", str(_project_root))

settings = Settings()
