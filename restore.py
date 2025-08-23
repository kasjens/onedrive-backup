#!/usr/bin/env python3

import os
import sys
import argparse
import subprocess
import json
from datetime import datetime
from pathlib import Path

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            return json.load(f)
    else:
        print(f"Configuration file not found: {config_file}")
        sys.exit(1)

def list_backups(backup_dir):
    """List available backup versions"""
    backups = []
    
    if os.path.exists(os.path.join(backup_dir, 'current')):
        backups.append(('current', os.path.join(backup_dir, 'current')))
    
    for item in os.listdir(backup_dir):
        if item.startswith('backup_'):
            path = os.path.join(backup_dir, item)
            if os.path.isdir(path):
                timestamp = item.replace('backup_', '')
                try:
                    dt = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                    formatted = dt.strftime('%Y-%m-%d %H:%M:%S')
                    backups.append((formatted, path))
                except:
                    backups.append((item, path))
    
    return sorted(backups, reverse=True)

def restore_files(source_path, destination, files=None, dry_run=False):
    """Restore files from backup to destination"""
    
    cmd = ['rsync', '-avh', '--progress']
    
    if dry_run:
        cmd.append('--dry-run')
    
    if files:
        for file in files:
            file_source = os.path.join(source_path, file)
            if os.path.exists(file_source):
                file_dest = os.path.join(destination, file)
                os.makedirs(os.path.dirname(file_dest), exist_ok=True)
                
                file_cmd = cmd + [file_source, file_dest]
                print(f"Restoring: {file}")
                subprocess.run(file_cmd)
    else:
        cmd.extend([f"{source_path}/", destination])
        print(f"Restoring entire backup to {destination}")
        subprocess.run(cmd)

def search_in_backup(backup_path, pattern):
    """Search for files in backup"""
    import fnmatch
    
    matches = []
    for root, dirs, files in os.walk(backup_path):
        for filename in files:
            if fnmatch.fnmatch(filename, pattern):
                rel_path = os.path.relpath(os.path.join(root, filename), backup_path)
                matches.append(rel_path)
    
    return matches

def main():
    parser = argparse.ArgumentParser(description='Restore files from OneDrive backup')
    parser.add_argument('--config', default='config.json', 
                       help='Configuration file path')
    parser.add_argument('--list', action='store_true',
                       help='List available backups')
    parser.add_argument('--backup', 
                       help='Backup version to restore from (default: latest)')
    parser.add_argument('--destination', 
                       help='Restore destination (default: original location)')
    parser.add_argument('--files', nargs='+',
                       help='Specific files to restore')
    parser.add_argument('--search', 
                       help='Search for files matching pattern')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be restored without doing it')
    
    args = parser.parse_args()
    
    config = load_config(args.config)
    backup_dir = os.path.expanduser(config['backup_destination'])
    
    if not os.path.exists(backup_dir):
        print(f"Backup directory not found: {backup_dir}")
        sys.exit(1)
    
    backups = list_backups(backup_dir)
    
    if args.list:
        print("Available backups:")
        for name, path in backups:
            size = sum(os.path.getsize(os.path.join(dirpath, filename))
                      for dirpath, dirnames, filenames in os.walk(path)
                      for filename in filenames) / (1024**3)
            print(f"  {name}: {size:.2f} GB")
        return
    
    if args.backup:
        backup_path = None
        for name, path in backups:
            if args.backup in name or args.backup in path:
                backup_path = path
                break
        if not backup_path:
            print(f"Backup not found: {args.backup}")
            sys.exit(1)
    else:
        if backups:
            backup_path = backups[0][1]
        else:
            print("No backups found")
            sys.exit(1)
    
    print(f"Using backup: {backup_path}")
    
    if args.search:
        matches = search_in_backup(backup_path, args.search)
        if matches:
            print(f"Found {len(matches)} matching files:")
            for match in matches[:20]:
                print(f"  {match}")
            if len(matches) > 20:
                print(f"  ... and {len(matches) - 20} more")
        else:
            print("No matching files found")
        return
    
    destination = args.destination
    if not destination:
        if config['source_type'] == 'local':
            destination = os.path.expanduser(config['local_source'])
        else:
            destination = os.path.expanduser('~/OneDrive-Restored')
    
    destination = os.path.expanduser(destination)
    
    if not args.dry_run:
        response = input(f"Restore to {destination}? (y/n): ")
        if response.lower() != 'y':
            print("Restore cancelled")
            return
    
    restore_files(backup_path, destination, args.files, args.dry_run)
    
    if not args.dry_run:
        print(f"Restore complete to: {destination}")

if __name__ == '__main__':
    main()