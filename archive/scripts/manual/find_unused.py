import os
import re

def get_all_py_files(root_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith('.py') and f != '__init__.py':
                py_files.append(os.path.join(dirpath, f))
    return py_files

src_files = get_all_py_files('src')
used_modules = set()

for pf in src_files + get_all_py_files('tests'):
    with open(pf, 'r', encoding='utf-8') as f:
        content = f.read()
        # naive import extraction
        imports = re.findall(r'^(?:from|import)\s+src\.([a-zA-Z0-9_.]+)', content, re.MULTILINE)
        for imp in imports:
            used_modules.add(imp.replace('.', '/'))

print("All Modules:")
for f in src_files:
    mod_path = f.replace('src/', '').replace('.py', '')
    if mod_path not in used_modules:
        print("Unused:", mod_path)
