#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

instruction=$(cat <<EOF
You will receive a git diff.
Respond with a code review of the commit.
Look for bugs, security issues, and opportunities for improvement.
Provide short actionable comments with examples if needed.
If no issues are found, respond with "Looks good to me".
Use markdown to format your review.
EOF
)
instruction=$(echo "${instruction}" | jq -sRr @uri)

git_diff=$(git diff --cached | jq -sRr @uri)
curl -sX POST "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${OPENAI_API_KEY}" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "system", "content": "'${instruction}'"},
      {"role": "user", "content": "'${git_diff}'"}
    ],
    "temperature": 0.2
  }' | jq -r '.choices[0].message.content'
