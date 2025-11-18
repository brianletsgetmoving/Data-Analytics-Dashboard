#!/bin/bash
# Helper script to start/stop/status the auto-commit watcher

SCRIPT_DIR="/Users/buyer/Data Analytics V5"
PID_FILE="${SCRIPT_DIR}/auto-commit.pid"
LOG_FILE="${SCRIPT_DIR}/auto-commit.log"

case "$1" in
    start)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "⚠️  Auto-commit is already running (PID: $PID)"
                exit 1
            else
                rm "$PID_FILE"
            fi
        fi
        
        echo "🚀 Starting auto-commit watcher..."
        cd "$SCRIPT_DIR" || exit 1
        nohup ./auto-commit.sh > "$LOG_FILE" 2>&1 &
        PID=$!
        echo "$PID" > "$PID_FILE"
        echo "✅ Auto-commit started (PID: $PID)"
        echo "📝 Logs: $LOG_FILE"
        echo "💡 Use './manage-auto-commit.sh stop' to stop it"
        ;;
    
    stop)
        if [ ! -f "$PID_FILE" ]; then
            echo "⚠️  Auto-commit is not running"
            exit 1
        fi
        
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            kill "$PID"
            rm "$PID_FILE"
            echo "✅ Auto-commit stopped"
        else
            echo "⚠️  Process not found, cleaning up PID file"
            rm "$PID_FILE"
        fi
        ;;
    
    status)
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p "$PID" > /dev/null 2>&1; then
                echo "✅ Auto-commit is running (PID: $PID)"
                echo "📝 Logs: $LOG_FILE"
                echo ""
                echo "Last 5 log entries:"
                tail -5 "$LOG_FILE" 2>/dev/null || echo "No log entries yet"
            else
                echo "⚠️  PID file exists but process is not running"
                rm "$PID_FILE"
            fi
        else
            echo "❌ Auto-commit is not running"
        fi
        ;;
    
    logs)
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "No log file found. Start auto-commit first."
        fi
        ;;
    
    *)
        echo "Usage: $0 {start|stop|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start  - Start the auto-commit watcher"
        echo "  stop   - Stop the auto-commit watcher"
        echo "  status - Check if auto-commit is running"
        echo "  logs   - View live log output"
        exit 1
        ;;
esac

