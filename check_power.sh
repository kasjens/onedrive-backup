#!/bin/bash

echo "System Power Management Status"
echo "=============================="
echo ""

# Check current power settings
echo "Current Power Settings:"
echo "-----------------------"

# Check if on AC or battery
if [ -f /sys/class/power_supply/AC/online ]; then
    AC_STATUS=$(cat /sys/class/power_supply/AC/online)
    if [ "$AC_STATUS" = "1" ]; then
        echo "Power Source: AC (Plugged In)"
    else
        echo "Power Source: Battery"
    fi
else
    echo "Power Source: Unknown"
fi

echo ""

# Check GNOME settings
if command -v gsettings &> /dev/null; then
    echo "GNOME Power Management:"
    echo "-----------------------"
    
    AC_TIMEOUT=$(gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 2>/dev/null)
    BATTERY_TIMEOUT=$(gsettings get org.gnome.settings-daemon.plugins.power sleep-inactive-battery-timeout 2>/dev/null)
    
    if [ -n "$AC_TIMEOUT" ]; then
        if [ "$AC_TIMEOUT" = "0" ]; then
            echo "On AC Power: Never sleep"
        else
            AC_MINUTES=$((AC_TIMEOUT / 60))
            echo "On AC Power: Sleep after $AC_MINUTES minutes of inactivity"
        fi
    fi
    
    if [ -n "$BATTERY_TIMEOUT" ]; then
        if [ "$BATTERY_TIMEOUT" = "0" ]; then
            echo "On Battery: Never sleep"
        else
            BATTERY_MINUTES=$((BATTERY_TIMEOUT / 60))
            echo "On Battery: Sleep after $BATTERY_MINUTES minutes of inactivity"
        fi
    fi
    
    echo ""
fi

# Check systemd sleep status
echo "System Sleep Services:"
echo "----------------------"
systemctl is-active sleep.target &>/dev/null && echo "Sleep: Active" || echo "Sleep: Inactive"
systemctl is-active suspend.target &>/dev/null && echo "Suspend: Active" || echo "Suspend: Inactive"
systemctl is-active hibernate.target &>/dev/null && echo "Hibernate: Active" || echo "Hibernate: Inactive"

echo ""

# Check for inhibitors
echo "Current Sleep Inhibitors:"
echo "-------------------------"
if command -v systemd-inhibit &> /dev/null; then
    INHIBITORS=$(systemd-inhibit --list --no-pager 2>/dev/null | grep -c "sleep")
    if [ "$INHIBITORS" -gt 0 ]; then
        echo "Active inhibitors found ($INHIBITORS):"
        systemd-inhibit --list --no-pager 2>/dev/null | grep -E "(Who|What|Why)" | head -20
    else
        echo "No active sleep inhibitors"
    fi
else
    echo "Cannot check inhibitors (systemd-inhibit not found)"
fi

echo ""
echo "Recommendations:"
echo "----------------"

if [ "$AC_TIMEOUT" != "0" ] && [ -n "$AC_TIMEOUT" ]; then
    echo "⚠ Your system will sleep after $AC_MINUTES minutes on AC power"
    echo ""
    echo "For long backups, use one of these options:"
    echo ""
    echo "1. Use the no-sleep wrapper (RECOMMENDED):"
    echo "   ./backup_no_sleep.sh"
    echo ""
    echo "2. Temporarily disable sleep (until reboot):"
    echo "   gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0"
    echo ""
    echo "3. Keep system active manually:"
    echo "   - Move mouse occasionally"
    echo "   - Or run: watch -n 300 echo 'Keeping system awake'"
else
    echo "✓ Your system is configured to never sleep on AC power"
    echo "  You can run backups without worry about standby"
fi

echo ""
echo "To run backup with sleep prevention:"
echo "  ./backup_no_sleep.sh"
echo ""
echo "To run backup normally:"
echo "  ./onedrive_backup.py"