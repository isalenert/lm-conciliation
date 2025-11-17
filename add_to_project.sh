#!/bin/bash

# Configurações
REPO="isalenert/lm-conciliation"
PROJECT_NUMBER=1  # Número do seu project (geralmente é 1 se for o primeiro)

echo "🚀 Adicionando issues ao project..."

# Pegar todas as issues
issues=$(gh issue list --repo $REPO --limit 100 --json number --jq '.[].number')

count=0
for issue in $issues; do
    gh project item-add $PROJECT_NUMBER --owner isalenert --url "https://github.com/$REPO/issues/$issue"
    echo "✅ Issue #$issue adicionada"
    ((count++))
done

echo ""
echo "📊 Total: $count issues adicionadas ao project!"
