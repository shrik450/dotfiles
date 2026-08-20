#!/bin/bash

cat <<'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "STYLE REMINDER for this response: follow the Language rules section of ~/.claude/CLAUDE.md (the global user CLAUDE.md already in context)."
  },
  "suppressOutput": true
}
EOF
