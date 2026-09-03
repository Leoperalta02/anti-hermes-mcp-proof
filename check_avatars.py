import json

path = r'C:\Users\leope\AppData\Roaming\xyz.block.buzz.app\agents\managed-agents.json'
with open(path, 'r', encoding='utf-8') as f:
    agents = json.load(f)

for a in agents:
    print(f"Name: {a.get('name')} | Avatar: {a.get('avatar_url')}")
