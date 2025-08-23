#!/usr/bin/env python3

import os
import sys
import json
import subprocess
import logging
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import time

class OneDriveBackup:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.setup_logging()
        
    def load_config(self):
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration"""
        config = {
            "source_type": "rclone",  # "rclone" or "local"
            "rclone_remote": "onedrive:",  # Name of your rclone remote
            "local_source": "~/OneDrive",  # Path if OneDrive is mounted locally
            "backup_destination": "~/onedrive-backup",
            "exclude_patterns": [
                "*.tmp",
                "~$*",
                ".DS_Store",
                "Thumbs.db",
                "desktop.ini"
            ],
            "rsync_options": [
                "--archive",
                "--verbose",
                "--human-readable",
                "--progress",
                "--delete-after",
                "--partial"
            ],
            "rclone_options": [
                "--verbose",
                "--progress",
                "--transfers", "4",
                "--checkers", "8",
                "--contimeout", "60s",
                "--timeout", "300s",
                "--retries", "3",
                "--low-level-retries", "10"
            ],
            "log_file": "~/onedrive-backup/backup.log",
            "keep_versions": 3,
            "dry_run": False
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"Created default configuration file: {self.config_file}")
        print("Please edit this file to match your setup before running the backup.")
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_file = os.path.expanduser(self.config['log_file'])
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def check_dependencies(self):
        """Check if required tools are installed"""
        tools = []
        
        if self.config['source_type'] == 'rclone':
            tools.append('rclone')
        else:
            tools.append('rsync')
        
        missing_tools = []
        for tool in tools:
            if shutil.which(tool) is None:
                missing_tools.append(tool)
        
        if missing_tools:
            self.logger.error(f"Missing required tools: {', '.join(missing_tools)}")
            if 'rclone' in missing_tools:
                self.logger.info("Install rclone: https://rclone.org/install/")
            if 'rsync' in missing_tools:
                self.logger.info("Install rsync: sudo apt-get install rsync")
            return False
        
        return True
    
    def setup_rclone(self):
        """Check and setup rclone configuration"""
        try:
            result = subprocess.run(['rclone', 'listremotes'], 
                                  capture_output=True, text=True)
            
            if self.config['rclone_remote'] not in result.stdout:
                self.logger.warning(f"Remote '{self.config['rclone_remote']}' not found in rclone config")
                self.logger.info("Run 'rclone config' to set up OneDrive remote")
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error checking rclone config: {e}")
            return False
    
    def create_backup_directory(self):
        """Create backup directory structure"""
        backup_dest = os.path.expanduser(self.config['backup_destination'])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if self.config['keep_versions'] > 1:
            backup_path = os.path.join(backup_dest, f"backup_{timestamp}")
        else:
            backup_path = os.path.join(backup_dest, "current")
        
        os.makedirs(backup_path, exist_ok=True)
        
        self.logger.info(f"Backup destination: {backup_path}")
        return backup_path
    
    def build_exclude_file(self):
        """Create temporary exclude file for rsync/rclone"""
        exclude_file = '/tmp/onedrive_backup_exclude.txt'
        with open(exclude_file, 'w') as f:
            for pattern in self.config['exclude_patterns']:
                f.write(f"{pattern}\n")
        return exclude_file
    
    def backup_with_rsync(self, backup_path):
        """Perform backup using rsync (for locally mounted OneDrive)"""
        source = os.path.expanduser(self.config['local_source'])
        
        if not os.path.exists(source):
            self.logger.error(f"Source directory not found: {source}")
            return False
        
        exclude_file = self.build_exclude_file()
        
        cmd = ['rsync']
        cmd.extend(self.config['rsync_options'])
        cmd.extend(['--exclude-from', exclude_file])
        
        if self.config['dry_run']:
            cmd.append('--dry-run')
        
        cmd.extend([f"{source}/", backup_path])
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True)
            
            for line in process.stdout:
                print(line.rstrip())
                self.logger.debug(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.logger.info("Backup completed successfully")
                return True
            else:
                self.logger.error(f"Backup failed with return code: {process.returncode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during rsync backup: {e}")
            return False
        finally:
            os.remove(exclude_file)
    
    def backup_with_rclone(self, backup_path):
        """Perform backup using rclone (for cloud OneDrive)"""
        exclude_file = self.build_exclude_file()
        
        cmd = ['rclone', 'sync']
        cmd.append(self.config['rclone_remote'])
        cmd.append(backup_path)
        cmd.extend(self.config['rclone_options'])
        cmd.extend(['--exclude-from', exclude_file])
        
        if self.config['dry_run']:
            cmd.append('--dry-run')
        
        self.logger.info(f"Running: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.STDOUT, text=True)
            
            for line in process.stdout:
                print(line.rstrip())
                self.logger.debug(line.rstrip())
            
            process.wait()
            
            if process.returncode == 0:
                self.logger.info("Backup completed successfully")
                return True
            else:
                self.logger.error(f"Backup failed with return code: {process.returncode}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during rclone backup: {e}")
            return False
        finally:
            os.remove(exclude_file)
    
    def cleanup_old_backups(self):
        """Remove old backup versions"""
        if self.config['keep_versions'] <= 1:
            return
        
        backup_dest = os.path.expanduser(self.config['backup_destination'])
        
        backup_dirs = []
        for item in os.listdir(backup_dest):
            if item.startswith('backup_'):
                path = os.path.join(backup_dest, item)
                if os.path.isdir(path):
                    backup_dirs.append(path)
        
        backup_dirs.sort(reverse=True)
        
        for old_backup in backup_dirs[self.config['keep_versions']:]:
            self.logger.info(f"Removing old backup: {old_backup}")
            shutil.rmtree(old_backup)
    
    def create_symlink_to_latest(self, backup_path):
        """Create a symlink to the latest backup"""
        if self.config['keep_versions'] <= 1:
            return
        
        backup_dest = os.path.expanduser(self.config['backup_destination'])
        latest_link = os.path.join(backup_dest, 'latest')
        
        if os.path.exists(latest_link):
            os.remove(latest_link)
        
        os.symlink(os.path.basename(backup_path), latest_link)
        self.logger.info(f"Created symlink 'latest' -> {os.path.basename(backup_path)}")
    
    def get_backup_stats(self, backup_path):
        """Get statistics about the backup"""
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(backup_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                    file_count += 1
                except:
                    pass
        
        size_gb = total_size / (1024 ** 3)
        self.logger.info(f"Backup statistics: {file_count} files, {size_gb:.2f} GB")
        
        return file_count, size_gb
    
    def run(self, dry_run=False):
        """Run the backup process"""
        start_time = time.time()
        
        if dry_run:
            self.config['dry_run'] = True
            self.logger.info("Running in DRY RUN mode - no changes will be made")
        
        self.logger.info("Starting OneDrive backup")
        
        if not self.check_dependencies():
            return False
        
        if self.config['source_type'] == 'rclone':
            if not self.setup_rclone():
                return False
        
        backup_path = self.create_backup_directory()
        
        if self.config['source_type'] == 'rclone':
            success = self.backup_with_rclone(backup_path)
        else:
            success = self.backup_with_rsync(backup_path)
        
        if success and not self.config['dry_run']:
            self.cleanup_old_backups()
            self.create_symlink_to_latest(backup_path)
            self.get_backup_stats(backup_path)
        
        elapsed_time = time.time() - start_time
        self.logger.info(f"Backup {'completed' if success else 'failed'} in {elapsed_time:.2f} seconds")
        
        return success

def main():
    parser = argparse.ArgumentParser(description='Backup OneDrive to local disk')
    parser.add_argument('--config', default='config.json', 
                       help='Configuration file path')
    parser.add_argument('--dry-run', action='store_true',
                       help='Perform a dry run without making changes')
    parser.add_argument('--setup', action='store_true',
                       help='Create default configuration and exit')
    
    args = parser.parse_args()
    
    backup = OneDriveBackup(args.config)
    
    if args.setup:
        print("Configuration file created. Please edit it before running backup.")
        return
    
    success = backup.run(dry_run=args.dry_run)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()