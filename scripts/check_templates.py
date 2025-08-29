import re
import os
from pathlib import Path

root = Path(__file__).resolve().parent.parent
py_files = list(root.rglob('*.py'))
pattern = re.compile(r"render\(\s*request\s*,\s*['\"]([^'\"]+)['\"]")
found = set()
for p in py_files:
    # skip venv
    if 'venv' in p.parts:
        continue
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    for m in pattern.finditer(text):
        found.add(m.group(1))

missing = []
for tpl in sorted(found):
    tpl_path = root / 'templates' / tpl
    if not tpl_path.exists():
        missing.append(tpl)

print('Templates referenced via render(request, ...):')
for tpl in sorted(found):
    print(' -', tpl)

print('\nMissing templates:')
if missing:
    for m in missing:
        print(' -', m)
    exit(2)
else:
    print('None')
    exit(0)
