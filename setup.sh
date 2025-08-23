#!/bin/bash

echo "OneDrive Backup Setup Script"
echo "============================"
echo ""

check_command() {
    if command -v $1 &> /dev/null; then
        echo "✓ $1 is installed"
        return 0
    else
        echo "✗ $1 is not installed"
        return 1
    fi
}

echo "Checking dependencies..."
echo ""

MISSING_DEPS=0

if ! check_command python3; then
    MISSING_DEPS=1
    echo "  Install: sudo apt-get install python3"
fi

if ! check_command rsync; then
    MISSING_DEPS=1
    echo "  Install: sudo apt-get install rsync"
fi

if ! check_command rclone; then
    echo "  rclone is not installed (required for cloud sync)"
    echo ""
    read -p "Would you like to install rclone now? (y/n): " install_rclone
    if [ "$install_rclone" = "y" ] || [ "$install_rclone" = "Y" ]; then
        echo "Installing rclone..."
        curl https://rclone.org/install.sh | sudo bash
        if [ $? -eq 0 ]; then
            echo "✓ rclone installed successfully"
        else
            echo "✗ Failed to install rclone"
            echo "  Please install manually: curl https://rclone.org/install.sh | sudo bash"
        fi
    else
        echo "  Skipping rclone installation"
        echo "  Note: You'll need rclone for cloud sync. Install later with:"
        echo "  curl https://rclone.org/install.sh | sudo bash"
    fi
fi

echo ""

if [ $MISSING_DEPS -eq 1 ]; then
    echo "Please install missing dependencies before continuing."
    exit 1
fi

echo "Setting up OneDrive backup..."
echo ""

chmod +x onedrive_backup.py

echo "Creating default configuration..."
python3 onedrive_backup.py --setup

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. If using rclone (recommended for cloud sync):"
echo "   - Run: rclone config"
echo "   - Follow the prompts to set up OneDrive access"
echo "   - Name your remote 'onedrive' (or update config.json)"
echo ""
echo "2. Edit config.json to customize your backup settings"
echo ""
echo "3. Test with a dry run:"
echo "   ./onedrive_backup.py --dry-run"
echo ""
echo "4. Run your first backup:"
echo "   ./onedrive_backup.py"
echo ""
echo "5. Set up automatic backups (optional):"
echo "   ./schedule_backup.sh"