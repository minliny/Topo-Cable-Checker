import json
import sys

data = json.load(sys.stdin)
paths = [item['path'] for item in data]
print(len(paths))
for p in paths[:5]:
    print(p)
