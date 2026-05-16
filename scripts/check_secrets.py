"""提交前检查 - 扫描敏感信息，防止隐私泄露"""
import re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'recovery'}

PATTERNS = [
    (r'0x[a-fA-F0-9]{64}', 'Private Key (64 hex)'),
    (r'PRIVATE_KEY\s*=\s*["\'](?!YOUR_)(?!$)["\']?[a-fA-F0-9x]', 'Non-placeholder PRIVATE_KEY'),
    (r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', 'UUID (possible API key)'),
    (r'sk-[a-zA-Z0-9]{32,}', 'OpenAI API Key'),
    (r'Bearer\s+[a-zA-Z0-9_\-]{20,}', 'Bearer Token'),
]

found = 0
for root, dirs, files in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')]
    for f in files:
        if not f.endswith(('.py', '.js', '.ts', '.json', '.md', '.env', '.example')):
            continue
        fp = os.path.join(root, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                content = fh.read()
        except:
            continue

        for pattern, name in PATTERNS:
            matches = re.findall(pattern, content)
            if matches and all('YOUR_' not in m and '0x...' not in m for m in matches):
                print(f"[!] {os.path.relpath(fp, ROOT)}: {name}")
                for m in matches[:3]:
                    print(f"    {m[:60]}...")
                found += 1

if found:
    print(f"\n[!] {found} potential secret(s) found! Fix before committing.")
    sys.exit(1)
else:
    print("[OK] No secrets detected.")
