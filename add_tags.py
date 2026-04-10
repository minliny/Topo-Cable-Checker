import os

files_to_tag = [
    "src/presentation/result_delivery.py",
    "src/crosscutting/clipboard.py",
    "src/crosscutting/ide_launcher.py",
    "src/crosscutting/temp_files.py",
    "tests/test_result_delivery.py"
]

tag_content = """# [OPTIONAL_MODULE]
# This module provides optional external-environment integration.
# It is not part of the core port-checking flow.
# Behavior may depend on OS / desktop / local environment setup.

"""

for file_path in files_to_tag:
    full_path = os.path.join("/workspace", file_path)
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(tag_content + content)
        print(f"Tagged {file_path}")
    else:
        print(f"Not found: {file_path}")
