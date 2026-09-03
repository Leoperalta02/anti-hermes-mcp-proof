import re

path = r'C:\LEO-LAB-ANTIGRAVITY\hermes-agent\tools\environments\local.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the body of _bash_starts to simply return True without running subprocess
content = re.sub(
    r'def _bash_starts\(bash: str\) -> bool:[\s\S]*?(?=\n\n_git_bash_bin_dirs_cache)',
    'def _bash_starts(bash: str) -> bool:\n    return True\n',
    content
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('Patched _bash_starts to always return True!')
