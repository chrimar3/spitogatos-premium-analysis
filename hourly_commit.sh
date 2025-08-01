#!/bin/bash

# Hourly Git Commit Script
# Automatically commits and pushes project progress every hour

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
HOUR=$(date "+%H")

echo "⏰ Hourly commit at $TIMESTAMP"

# Add all changes
git add .

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "📝 No changes to commit at $TIMESTAMP"
else
    # Commit with timestamp
    git commit -m "Hourly progress update - $(date '+%Y-%m-%d %H:00')

Project progress auto-commit:
- Real estate data analysis development
- Validated scraper improvements
- City block analysis updates

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

    # Push to GitHub
    git push origin main
    
    echo "✅ Successfully committed and pushed changes at $TIMESTAMP"
fi
