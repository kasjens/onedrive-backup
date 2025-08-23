# OneDrive Backup Tool

A robust backup solution for Microsoft OneDrive that downloads and stores your cloud files locally with version management, scheduling, and easy restoration capabilities.

## 🚀 Quick Start

### 1. Initial Setup (One-time)

```bash
# Clone or navigate to the project directory
cd ~/projects/onedrive-backup

# Run the setup script (will install dependencies)
./setup.sh
```

The setup will:
- Check for Python 3 and rsync
- Offer to install rclone (required for OneDrive access)
- Create a default configuration file

### 2. Configure OneDrive Access

```bash
# Run the configuration helper
./configure_onedrive.sh
```

**During configuration:**
1. Choose `n` for "New remote"
2. Name it exactly: `onedrive`
3. Select "Microsoft OneDrive" from the provider list
4. Press Enter for default options (Client ID/Secret)
5. Choose `1` for "Microsoft Cloud Global"
6. Follow the browser authorization:
   - A browser will open (or you'll get a link)
   - Log in to your Microsoft account
   - Grant permissions for rclone
7. Confirm the configuration

### 3. Run Your First Backup

```bash
# Test with a dry run (shows what will be backed up without downloading)
./onedrive_backup.py --dry-run

# Run the actual backup
./onedrive_backup.py
```

## 📁 What Gets Backed Up?

**Everything in your OneDrive**, except:
- Temporary files (`*.tmp`, `~$*`)
- System files (`.DS_Store`, `Thumbs.db`, `desktop.ini`)
- Personal Vault (requires special authentication)

**Default backup location:** `~/onedrive-backup/`

## 🔧 Configuration

Edit `config.json` to customize settings:

```json
{
    "backup_destination": "~/onedrive-backup",  // Where to store backups
    "keep_versions": 3,                         // Number of backup versions to keep
    "exclude_patterns": ["*.tmp", "~$*"],       // Files to skip
    "dry_run": false                            // Set true for testing
}
```

### Key Settings Explained

| Setting | Description | Default |
|---------|------------|---------|
| `backup_destination` | Where backups are stored | `~/onedrive-backup` |
| `keep_versions` | How many backup versions to keep | `3` |
| `source_type` | Use `rclone` for cloud or `local` for mounted drive | `rclone` |
| `rclone_remote` | Name of your rclone remote | `onedrive:` |

## 📋 Common Tasks

### View Backup Progress
The tool shows real-time progress during backup:
- Files being transferred
- Transfer speed
- Time remaining
- Total size

### Check Backup Logs
```bash
# View recent backup activity
tail -f ~/onedrive-backup/backup.log
```

### List Available Backups
```bash
./restore.py --list
```

Output example:
```
Available backups:
  2025-01-23 14:30:00: 30.5 GB
  2025-01-22 14:30:00: 30.4 GB
  2025-01-21 14:30:00: 30.3 GB
```

## 🔄 Restore Files

### Restore Everything
```bash
# Restore latest backup to ~/OneDrive-Restored
./restore.py

# Restore to specific location
./restore.py --destination ~/my-restored-files
```

### Restore Specific Files
```bash
# Restore a single file
./restore.py --files "Documents/report.docx"

# Restore multiple files/folders
./restore.py --files "Documents/reports/" "Pictures/vacation/"
```

### Search and Restore
```bash
# Find files first
./restore.py --search "*.docx"

# Then restore specific ones
./restore.py --files "Documents/important.docx"
```

### Restore from Specific Backup
```bash
# List backups
./restore.py --list

# Restore from specific date
./restore.py --backup "2025-01-20"
```

## ⏰ Schedule Automatic Backups

```bash
./schedule_backup.sh
```

Choose from:
1. **Hourly** - Every hour
2. **Daily** - Every day at 2 AM
3. **Weekly** - Every Sunday at 2 AM
4. **Custom** - Your own schedule
5. **Remove** - Stop scheduled backups

### View Scheduled Backups
```bash
crontab -l
```

### Manual Scheduling (Advanced)
```bash
# Edit crontab directly
crontab -e

# Add a line like this for daily 3 AM backups:
0 3 * * * /usr/bin/python3 ~/projects/onedrive-backup/onedrive_backup.py
```

## 📊 Storage Management

### Check Backup Sizes
```bash
# See how much space backups use
du -sh ~/onedrive-backup/*
```

### Adjust Version Retention
Edit `config.json`:
```json
"keep_versions": 1  // Only keep latest (saves space)
"keep_versions": 7  // Keep a week's worth
```

### Manual Cleanup
```bash
# Remove old backups manually
rm -rf ~/onedrive-backup/backup_20250120_*
```

## 🛠️ Troubleshooting

### "rclone remote not found"
```bash
# Reconfigure OneDrive access
rclone config
# Make sure to name it exactly: onedrive
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x *.py *.sh
```

### Backup is too slow
Edit `config.json` to increase parallel transfers:
```json
"rclone_options": [
    "--transfers", "8",     // Increase from 4
    "--checkers", "16"      // Increase from 8
]
```

### Personal Vault Error
This is normal. Personal Vault requires additional authentication and is skipped by default.

### Test Connection
```bash
# List OneDrive contents
rclone ls onedrive: --max-depth 1

# Check available space
rclone about onedrive:
```

## 📈 Advanced Usage

### Dry Run (Preview Mode)
Always test changes with dry-run first:
```bash
./onedrive_backup.py --dry-run
```

### Backup Specific Folders Only
Edit `config.json` to change source:
```json
"rclone_remote": "onedrive:Documents"  // Only backup Documents folder
```

### Exclude More File Types
Add patterns to `config.json`:
```json
"exclude_patterns": [
    "*.tmp",
    "*.cache",
    "node_modules/",
    "*.log"
]
```

### Use Different Config File
```bash
./onedrive_backup.py --config my-config.json
```

## 📝 File Structure

After running backups, your directory structure will look like:

```
~/onedrive-backup/
├── backup_20250123_143000/    # Timestamped backup
│   ├── Documents/
│   ├── Pictures/
│   └── ...
├── backup_20250122_143000/    # Previous version
├── backup_20250121_143000/    # Older version
├── latest -> backup_20250123_143000  # Symlink to newest
└── backup.log                  # Backup history
```

## 🔐 Security Notes

- Your OneDrive credentials are stored securely by rclone
- Backups are stored unencrypted locally (use disk encryption if needed)
- The tool only reads from OneDrive, never writes or deletes
- Personal Vault files require additional authentication

## 💡 Tips

1. **First Backup**: Will take longest as it downloads everything
2. **Subsequent Backups**: Much faster (only new/changed files)
3. **Network**: Use ethernet for initial backup if possible
4. **Storage**: Ensure you have enough space (check with `df -h`)
5. **Monitoring**: Use `tail -f backup.log` during backups

## 🔋 Preventing System Sleep During Backup

Your system may go to sleep during long backups. Use these tools to prevent interruption:

### Check Your Power Settings
```bash
./check_power.sh
```
This shows:
- Current power source (AC/Battery)
- Sleep timeout settings
- Active sleep inhibitors
- Personalized recommendations

### Method 1: All-in-One (Recommended)
Run backup with automatic sleep prevention:
```bash
./backup_no_sleep.sh
```
This wraps the backup process and prevents sleep until completion.

### Method 2: Separate Sleep Prevention
Keep system awake in one terminal while running backup in another:

**Terminal 1 - Prevent Sleep:**
```bash
./backup_no_sleep.sh --prevent-sleep-only
# or shorter: ./backup_no_sleep.sh -p
```
Keep this running (press Ctrl+C when done)

**Terminal 2 - Run Backup:**
```bash
./onedrive_backup.py
```

### Method 3: Temporary System Setting
Disable sleep for current session:
```bash
# Disable sleep
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 0

# Run your backup
./onedrive_backup.py

# Restore original setting (optional)
gsettings set org.gnome.settings-daemon.plugins.power sleep-inactive-ac-timeout 3600
```

### Why This Matters
- Default Ubuntu/GNOME: Sleep after 60 minutes of inactivity
- Your 30GB backup: May take 1-3+ hours
- Without prevention: Backup fails when system sleeps
- With prevention: Backup completes uninterrupted

## 🆘 Getting Help

- **Check logs**: `cat ~/onedrive-backup/backup.log`
- **Verbose mode**: Add `-v` flag for detailed output
- **Test config**: `rclone listremotes` should show `onedrive:`
- **Manual sync**: `rclone sync onedrive: ~/test --dry-run`
- **Power status**: `./check_power.sh` to see sleep settings

## 📜 License

This tool is provided as-is for personal use. Always maintain separate backups of critical data.