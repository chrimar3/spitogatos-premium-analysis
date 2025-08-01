#!/bin/bash

# GitHub Repository Setup and Hourly Automation Script
# For Spitogatos Premium Analysis Project

echo "🔗 GITHUB REPOSITORY SETUP"
echo "=========================="

# 1. Manual GitHub Setup Instructions
echo "📋 MANUAL SETUP REQUIRED:"
echo "1. Go to https://github.com/new"
echo "2. Repository name: spitogatos-premium-analysis"
echo "3. Make it Public"
echo "4. Don't initialize with README (we already have files)"
echo "5. Click 'Create repository'"
echo ""
echo "6. Copy the repository URL (should be something like):"
echo "   https://github.com/YOUR_USERNAME/spitogatos-premium-analysis.git"

# 2. Add remote and push
echo ""
echo "🚀 THEN RUN THESE COMMANDS:"
echo "git remote add origin https://github.com/YOUR_USERNAME/spitogatos-premium-analysis.git"
echo "git branch -M main"
echo "git push -u origin main"

# 3. Create hourly commit script
cat > hourly_commit.sh << 'EOF'
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
EOF

chmod +x hourly_commit.sh

# 4. Create cron job setup
cat > setup_hourly_commits.sh << 'EOF'
#!/bin/bash

# Setup hourly commits using cron
echo "⚙️ Setting up hourly commits..."

CURRENT_DIR=$(pwd)
SCRIPT_PATH="$CURRENT_DIR/hourly_commit.sh"

# Add cron job to run every hour
(crontab -l 2>/dev/null; echo "0 * * * * cd $CURRENT_DIR && $SCRIPT_PATH >> $CURRENT_DIR/commit_log.txt 2>&1") | crontab -

echo "✅ Hourly commits configured!"
echo "📝 Commits will run at the top of every hour"
echo "📄 Check commit_log.txt for automation logs"
EOF

chmod +x setup_hourly_commits.sh

echo ""
echo "📁 FILES CREATED:"
echo "✅ hourly_commit.sh - Manual commit script"
echo "✅ setup_hourly_commits.sh - Automated hourly setup"
echo ""
echo "🔧 TO COMPLETE SETUP:"
echo "1. Create GitHub repository manually (instructions above)"
echo "2. Run: git remote add origin YOUR_REPO_URL"
echo "3. Run: git push -u origin main"
echo "4. Run: ./setup_hourly_commits.sh (for automatic hourly commits)"
echo ""
echo "📊 YOUR REPOSITORY WILL BE AT:"
echo "https://github.com/YOUR_USERNAME/spitogatos-premium-analysis"