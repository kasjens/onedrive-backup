#!/bin/bash

# Check for --prevent-sleep-only flag
if [ "$1" = "--prevent-sleep-only" ] || [ "$1" = "-p" ]; then
    echo "====================================="
    echo "Sleep Prevention Mode"
    echo "====================================="
    echo ""
    
    if ! command -v gnome-session-inhibit &> /dev/null; then
        echo "Error: gnome-session-inhibit not found"
        echo "To install: sudo apt-get install gnome-session"
        exit 1
    fi
    
    echo "Preventing system sleep/suspend..."
    echo "Your system will stay awake until you press Ctrl+C"
    echo ""
    echo "You can now run your backup in another terminal:"
    echo "  ./onedrive_backup.py"
    echo ""
    echo "Press Ctrl+C when backup is complete to allow sleep again"
    echo ""
    
    # Just inhibit sleep without running any command
    gnome-session-inhibit \
        --app-id "OneDrive Backup" \
        --reason "Preventing sleep during OneDrive backup" \
        --inhibit idle:sleep:suspend \
        --inhibit-only
    
    echo ""
    echo "✓ Sleep prevention released"
    exit 0
fi

# Show help if requested
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --prevent-sleep-only, -p  Only prevent sleep (run backup separately)"
    echo "  --help, -h               Show this help message"
    echo "  [backup options]         Any options to pass to onedrive_backup.py"
    echo ""
    echo "Examples:"
    echo "  $0                      Run backup with sleep prevention"
    echo "  $0 --dry-run            Run backup dry-run with sleep prevention"
    echo "  $0 --prevent-sleep-only Keep system awake (run backup in another terminal)"
    exit 0
fi

echo "====================================="
echo "OneDrive Backup (Sleep Prevention On)"
echo "====================================="
echo ""

# Check if gnome-session-inhibit is available
if ! command -v gnome-session-inhibit &> /dev/null; then
    echo "Warning: gnome-session-inhibit not found"
    echo "System may go to sleep during backup"
    echo ""
    echo "To install: sudo apt-get install gnome-session"
    echo ""
    read -p "Continue anyway? (y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ] && [ "$continue_anyway" != "Y" ]; then
        exit 1
    fi
    # Run without sleep prevention
    ./onedrive_backup.py "$@"
else
    echo "Starting backup with sleep/suspend prevention..."
    echo "Your system will NOT go to standby during the backup."
    echo ""
    echo "Press Ctrl+C to cancel"
    echo ""
    
    # Run backup with sleep inhibition
    # --inhibit idle:sleep:suspend = prevent idle, sleep, and suspend
    # --inhibit-only would only inhibit without running command
    gnome-session-inhibit \
        --app-id "OneDrive Backup" \
        --reason "Backing up OneDrive data" \
        --inhibit idle:sleep:suspend \
        ./onedrive_backup.py "$@"
    
    RESULT=$?
    
    if [ $RESULT -eq 0 ]; then
        echo ""
        echo "✓ Backup completed successfully"
        echo "✓ System sleep prevention has been released"
    else
        echo ""
        echo "⚠ Backup exited with code: $RESULT"
        echo "✓ System sleep prevention has been released"
    fi
    
    exit $RESULT
fi