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
