#!/bin/bash

# Enhanced Hourly Git Commit Script
# Automatically commits and pushes project progress every hour with robust error handling

# Configuration
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
HOUR=$(date "+%H")
LOG_FILE="commit_log.txt"
MAX_RETRIES=3
RETRY_DELAY=10

# Function to log messages
log_message() {
    echo "[$TIMESTAMP] $1" | tee -a "$LOG_FILE"
}

# Function to retry git operations
retry_git_operation() {
    local command="$1"
    local operation_name="$2"
    local retry_count=0
    
    while [ $retry_count -lt $MAX_RETRIES ]; do
        if eval "$command"; then
            log_message "✅ $operation_name succeeded"
            return 0
        else
            retry_count=$((retry_count + 1))
            log_message "⚠️ $operation_name failed (attempt $retry_count/$MAX_RETRIES)"
            if [ $retry_count -lt $MAX_RETRIES ]; then
                log_message "🔄 Retrying in $RETRY_DELAY seconds..."
                sleep $RETRY_DELAY
            fi
        fi
    done
    
    log_message "❌ $operation_name failed after $MAX_RETRIES attempts"
    return 1
}

# Function to check network connectivity
check_network() {
    if ping -c 1 github.com >/dev/null 2>&1; then
        return 0
    else
        log_message "❌ No network connectivity to GitHub"
        return 1
    fi
}

# Function to check git repository status
check_git_status() {
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        log_message "❌ Not a git repository"
        return 1
    fi
    
    if ! git remote get-url origin >/dev/null 2>&1; then
        log_message "❌ No remote origin configured"
        return 1
    fi
    
    return 0
}

# Function to create commit message with file summary
create_commit_message() {
    local changed_files=$(git diff --cached --name-only | head -10)
    local file_count=$(git diff --cached --name-only | wc -l)
    
    cat << EOF
Hourly progress update - $(date '+%Y-%m-%d %H:00')

🔄 Automated project backup and progress tracking

📊 Changes in this commit:
EOF

    if [ $file_count -gt 0 ]; then
        echo "📝 Modified files ($file_count total):"
        echo "$changed_files" | sed 's/^/  - /'
        
        if [ $file_count -gt 10 ]; then
            echo "  ... and $((file_count - 10)) more files"
        fi
    fi
    
    cat << EOF

🏗️ Project: Athens Real Estate Energy Efficiency Analysis
🤖 Auto-commit: Preserving development progress
📈 Analysis: SQM-Energy correlation and block-level insights

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
}

# Main execution
main() {
    log_message "⏰ Starting hourly commit process"
    
    # Check if we're in the right directory
    if [ ! -f "hourly_commit.sh" ] && [ ! -f "enhanced_hourly_commit.sh" ]; then
        log_message "❌ Not in project directory, changing to correct location"
        cd /Users/chrism/spitogatos_premium_analysis || {
            log_message "❌ Failed to change to project directory"
            exit 1
        }
    fi
    
    # Check git repository status
    if ! check_git_status; then
        exit 1
    fi
    
    # Check network connectivity
    if ! check_network; then
        log_message "🔄 Network unavailable, will retry next hour"
        exit 0
    fi
    
    # Fetch latest changes from remote (non-blocking)
    log_message "🔄 Fetching latest changes from remote..."
    git fetch origin main >/dev/null 2>&1 || log_message "⚠️ Could not fetch from remote (continuing anyway)"
    
    # Add all changes
    log_message "📦 Adding all changes to staging area..."
    git add . || {
        log_message "❌ Failed to add changes"
        exit 1
    }
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log_message "📝 No changes to commit at $TIMESTAMP"
        exit 0
    fi
    
    # Show summary of changes
    local staged_files=$(git diff --cached --name-only | wc -l)
    local total_additions=$(git diff --cached --numstat | awk '{sum += $1} END {print sum}')
    local total_deletions=$(git diff --cached --numstat | awk '{sum += $2} END {print sum}')
    
    log_message "📊 Changes detected: $staged_files files, +$total_additions -$total_deletions lines"
    
    # Create and execute commit
    local commit_msg=$(create_commit_message)
    log_message "📝 Creating commit..."
    
    if ! retry_git_operation "git commit -m \"$commit_msg\"" "Commit operation"; then
        log_message "❌ Failed to create commit after retries"
        exit 1
    fi
    
    # Push to GitHub with retries
    log_message "🚀 Pushing to GitHub remote..."
    if ! retry_git_operation "git push origin main" "Push operation"; then
        log_message "❌ Failed to push after retries"
        # Don't exit here - the commit was successful, just the push failed
        log_message "💾 Changes committed locally but not pushed to remote"
        exit 1
    fi
    
    log_message "✅ Successfully committed and pushed changes at $TIMESTAMP"
    log_message "🎉 Hourly backup completed successfully"
}

# Execute main function
main "$@"