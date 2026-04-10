# [OPTIONAL_MODULE]
# This module provides optional external-environment integration.
# It is not part of the core port-checking flow.
# Behavior may depend on OS / desktop / local environment setup.

import os
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def create_temp_result_file(content: str, ext: str = "md") -> str:
    """Creates a temporary result file with a timestamped name."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"topo_checker_result_{timestamp}.{ext}"
        
        # Use tempfile.gettempdir() to get the system temp directory
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
        return file_path
    except Exception as e:
        logger.warning(f"Failed to create temporary file: {e}")
        return ""
