#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKUP_SCRIPT="$SCRIPT_DIR/onedrive_backup.py"

echo "OneDrive Backup Scheduler"
echo "========================"
echo ""
echo "Choose scheduling option:"
echo "1. Hourly backup"
echo "2. Daily backup (at 2 AM)"
echo "3. Weekly backup (Sunday at 2 AM)"
echo "4. Custom cron schedule"
echo "5. Remove scheduled backup"
echo ""
read -p "Enter option (1-5): " option

case $option in
    1)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="hourly"
        ;;
    2)
        CRON_SCHEDULE="0 2 * * *"
        DESCRIPTION="daily at 2 AM"
        ;;
    3)
        CRON_SCHEDULE="0 2 * * 0"
        DESCRIPTION="weekly on Sunday at 2 AM"
        ;;
    4)
        echo "Enter custom cron schedule (e.g., '0 */6 * * *' for every 6 hours):"
        read CRON_SCHEDULE
        DESCRIPTION="custom"
        ;;
    5)
        echo "Removing OneDrive backup from crontab..."
        (crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT") | crontab -
        echo "Scheduled backup removed."
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac

CRON_JOB="$CRON_SCHEDULE /usr/bin/python3 $BACKUP_SCRIPT >> $SCRIPT_DIR/cron.log 2>&1"

(crontab -l 2>/dev/null | grep -v "$BACKUP_SCRIPT"; echo "$CRON_JOB") | crontab -

echo ""
echo "Backup scheduled: $DESCRIPTION"
echo "Cron job: $CRON_JOB"
echo ""
echo "View scheduled jobs with: crontab -l"
echo "View backup logs at: $SCRIPT_DIR/backup.log"
echo "View cron logs at: $SCRIPT_DIR/cron.log"