"""
patch_toolsets.py
Ensures mention_agent_in_channel is included in buzz_ipc toolset inside C:\LEO-LAB-ANTIGRAVITY\hermes-agent\toolsets.py
"""
path = r'C:\LEO-LAB-ANTIGRAVITY\hermes-agent\toolsets.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

target = '"tools": ["send_managed_agent"],'
replacement = '"tools": ["send_managed_agent", "mention_agent_in_channel"],'

if target in content:
    content = content.replace(target, replacement)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Successfully updated toolsets.py to include mention_agent_in_channel!')
else:
    print('toolsets.py already includes mention_agent_in_channel or target pattern not found.')
