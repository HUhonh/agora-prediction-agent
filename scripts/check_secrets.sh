#!/bin/bash
# 提交前检查 - 扫描敏感信息
echo "Checking for secrets..."

PATTERNS=(
    "0x[a-fA-F0-9]{64}"           # 私钥
    "sk-[a-zA-Z0-9]{32,}"         # OpenAI key
    "[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}"  # UUID (Chainlink)
    "PRIVATE_KEY=[^Y]"             # 非占位符的私钥
    "Bearer [a-zA-Z0-9_-]{20,}"    # Bearer token
)

for pattern in "${PATTERNS[@]}"; do
    echo "  Scanning: $pattern"
    # Use ripgrep if available, otherwise grep
    if command -v rg &> /dev/null; then
        rg "$pattern" --no-ignore --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --exclude-dir=".git" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".venv"
    else
        grep -r --include="*.py" --include="*.js" --include="*.ts" --include="*.json" --exclude-dir=".git" --exclude-dir="node_modules" "$pattern" .
    fi
done

echo "Done. Review any matches above before committing."
