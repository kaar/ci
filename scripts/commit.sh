#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

instruction=$(cat <<EOF
You will receive a git diff and respond with a git commit message.
Limit the subject line to 50 characters.
Separate subject from body with a blank line.
Be concise and to the point.
EOF
)
instruction=$(echo "${instruction}" | jq -sRr @uri)

git_diff=$(git diff --cached | jq -sRr @uri)
commit_msg=$(curl -sX POST "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "'${instruction}'"},
      {"role": "user", "content": "'${git_diff}'"}
    ],
    "temperature": 0.2
  }' | jq -r '.choices[0].message.content')

echo "${commit_msg}" | git commit -eF -
