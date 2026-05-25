#!/usr/bin/env bash
# PreToolUse hook for the Suno Claude loop.
# Reads the tool call from stdin (JSON), blocks dangerous Bash commands.
# Exit 0 = allow, exit 2 = block (Claude sees the blocked reason and adapts).

INPUT=$(cat)

# Extract the command field robustly via Python (jq isn't on every Mac)
CMD=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except Exception:
    pass
" 2>/dev/null)

# If we can't parse, allow (don't block on JSON noise)
if [ -z "$CMD" ]; then
    exit 0
fi

# Block list — destructive or out-of-scope patterns
BLOCK_REGEX='rm -rf (/|~|\$HOME|/Users|/System|/Library)|git push|git reset --hard|git checkout -- \.|git clean -fd|sudo |mkfs|dd if=|:\(\)\{ :\|:\& \};:|curl[^|]*\|[ ]*(sh|bash)|wget[^|]*\|[ ]*(sh|bash)'

if echo "$CMD" | grep -qE "$BLOCK_REGEX"; then
    echo "BLOCKED by .claude/guard.sh — pattern in: $CMD" >&2
    echo "If this is a false positive, narrow the regex in guard.sh." >&2
    exit 2
fi

exit 0
