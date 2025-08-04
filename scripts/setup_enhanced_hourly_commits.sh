#!/bin/bash

# Setup Enhanced Hourly Commits with Safety and Monitoring
echo "⚙️ Setting up enhanced hourly commits for GitHub automation..."

CURRENT_DIR=$(pwd)
SCRIPT_PATH="$CURRENT_DIR/enhanced_hourly_commit.sh"
LOG_FILE="$CURRENT_DIR/commit_log.txt"

# Ensure we're in the right directory
if [ ! -f "enhanced_hourly_commit.sh" ]; then
    echo "❌ Enhanced commit script not found in current directory"
    exit 1
fi

# Make script executable
chmod +x "$SCRIPT_PATH"

# Remove any existing similar cron jobs to avoid duplicates
echo "🧹 Cleaning up existing hourly commit cron jobs..."
crontab -l 2>/dev/null | grep -v "hourly_commit.sh" | grep -v "enhanced_hourly_commit.sh" | crontab -

# Add new enhanced cron job
echo "📅 Setting up new enhanced hourly cron job..."
(crontab -l 2>/dev/null; echo "0 * * * * cd $CURRENT_DIR && $SCRIPT_PATH >> $LOG_FILE 2>&1") | crontab -

# Verify cron job was added
echo "✅ Verifying cron job installation..."
if crontab -l | grep -q "enhanced_hourly_commit.sh"; then
    echo "✅ Enhanced hourly commits configured successfully!"
else
    echo "❌ Failed to configure cron job"
    exit 1
fi

# Create initial log entry
echo "📝 Creating initial log entry..."
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 🚀 Enhanced hourly commit automation started" >> "$LOG_FILE"

# Display configuration summary
echo ""
echo "📊 CONFIGURATION SUMMARY:"
echo "=========================="
echo "🔄 Frequency: Every hour (at minute 0)"
echo "📁 Project Directory: $CURRENT_DIR"
echo "📜 Script Path: $SCRIPT_PATH"
echo "📄 Log File: $LOG_FILE"
echo "🌐 Remote: $(git remote get-url origin 2>/dev/null || echo 'Not configured')"
echo "🌿 Branch: $(git branch --show-current 2>/dev/null || echo 'Unknown')"

echo ""
echo "⚡ SAFETY FEATURES:"
echo "=================="
echo "🔄 Automatic retry (3 attempts) for failed operations"
echo "🌐 Network connectivity checks before pushing"
echo "📊 Detailed file change summaries in commits"
echo "🛡️ Error handling and graceful failure recovery"
echo "📝 Comprehensive logging to commit_log.txt"

echo ""
echo "🎯 NEXT STEPS:"
echo "=============="
echo "1. Wait for the next hour to see the first automatic commit"
echo "2. Monitor the log file: tail -f $LOG_FILE"
echo "3. Check GitHub repository for automated commits"

echo ""
echo "🔧 MANAGEMENT COMMANDS:"
echo "======================"
echo "• View cron jobs: crontab -l"
echo "• View logs: tail -f commit_log.txt"
echo "• Test manually: ./enhanced_hourly_commit.sh"
echo "• Disable automation: crontab -r"

echo ""
echo "✅ Enhanced hourly commits are now active!"
echo "⏰ Next commit scheduled for: $(date -d '+1 hour' '+%Y-%m-%d %H:00:00')"