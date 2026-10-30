#!/usr/bin/env bash
# Ask before git add/commit of ISO blobs, package archives, or credential files.
set -euo pipefail

input=$(cat)
command=$(printf '%s' "$input" | jq -r '.command // empty')

if [[ ! "$command" =~ (^|[[:space:]])git[[:space:]]+(add|commit|update-index) ]]; then
  echo '{ "permission": "allow" }'
  exit 0
fi

if [[ "$command" =~ \.(iso|pkg\.tar\.(zst|xz|gz)|pem|key|p12|secret)([[:space:]]|$) ]] \
  || [[ "$command" =~ (^|[[:space:]])(out/|build/out/|\.env) ]]; then
  cat <<'EOF'
{
  "permission": "ask",
  "user_message": "This git command may stage ISO, package, or credential artifacts that SynapseOS keeps out of Git.",
  "agent_message": "A hook flagged a git add/commit that looks like a build blob or secret. Keep those files untracked."
}
EOF
  exit 0
fi

echo '{ "permission": "allow" }'
exit 0
