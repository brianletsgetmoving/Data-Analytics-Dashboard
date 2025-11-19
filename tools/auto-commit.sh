#!/bin/bash
# Auto-commit script that watches for changes and commits/pushes automatically

REPO_PATH="/Users/buyer/Data Analytics V5"
cd "$REPO_PATH" || exit 1

# Ensure we're in the right directory
if [ ! -d ".git" ]; then
    echo "Error: Not a git repository. Exiting."
    exit 1
fi

echo "Starting auto-commit watcher for: $REPO_PATH"
echo "Press Ctrl+C to stop"

# Function to commit and push
commit_and_push() {
    # Check for changes (both staged and unstaged)
    if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
        # Add all changes
        git add .
        
        # Commit with timestamp
        TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
        COMMIT_MSG="Auto-commit: $TIMESTAMP"
        
        if git commit -m "$COMMIT_MSG" > /dev/null 2>&1; then
            echo "[$(date '+%H:%M:%S')] ✅ Committed: $COMMIT_MSG"
            
            # Push to remote
            if git push origin main > /dev/null 2>&1; then
                echo "[$(date '+%H:%M:%S')] ✅ Pushed to origin/main"
            else
                echo "[$(date '+%H:%M:%S')] ⚠️  Push failed (check network/credentials)"
            fi
        else
            echo "[$(date '+%H:%M:%S')] ℹ️  No changes to commit"
        fi
    fi
}

# Initial commit check
commit_and_push

# Watch for changes every 60 seconds
while true; do
    sleep 60
    commit_and_push
done

