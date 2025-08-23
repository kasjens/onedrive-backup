#!/bin/bash

echo "=========================================="
echo "OneDrive Configuration Helper"
echo "=========================================="
echo ""
echo "This will guide you through configuring rclone for OneDrive."
echo ""
echo "You'll need to:"
echo "1. Log in to your Microsoft account when prompted"
echo "2. Grant permissions for rclone to access your OneDrive"
echo ""
read -p "Ready to start? (y/n): " ready

if [ "$ready" != "y" ] && [ "$ready" != "Y" ]; then
    echo "Configuration cancelled."
    exit 0
fi

echo ""
echo "Starting rclone configuration..."
echo ""
echo "IMPORTANT: When prompted:"
echo "- Choose 'n' for new remote"
echo "- Name it 'onedrive' (exactly as shown)"
echo "- Select 'Microsoft OneDrive' from the list"
echo "- Use default options for most settings"
echo ""
echo "Press Enter to continue..."
read

rclone config

echo ""
echo "Testing configuration..."
rclone lsd onedrive: 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ OneDrive configured successfully!"
    echo ""
    echo "You can now:"
    echo "1. Test backup:  ./onedrive_backup.py --dry-run"
    echo "2. Run backup:   ./onedrive_backup.py"
    echo "3. Schedule:     ./schedule_backup.sh"
else
    echo ""
    echo "⚠ Configuration may not be complete."
    echo "Run 'rclone config' to review settings."
    echo "Make sure the remote is named 'onedrive'"
fi