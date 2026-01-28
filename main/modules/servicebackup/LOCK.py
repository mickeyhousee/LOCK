#!/usr/bin/env python3
"""
Script for monitoring specified files, backing up, and sending via SCP.
It monitors for any changes and restores files from backup if changes are detected.

Author: Development Team COCIBER PT
"""

import hashlib
import os
import shutil
import logging
import time
import signal
from logging.handlers import RotatingFileHandler
import socket
import os
import stat
import pwd
import grp

# Initialize logging
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't actually send data
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    finally:
        s.close()
    return IP

# Get local IP address
local_ip = get_local_ip()

# Log file name based on local IP
log_file = f"{local_ip}_monitoring.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(log_file, maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)

# Relative Path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Directories and file paths
MONITOR_CFG = f'{dir_path}/services.cfg' # Config file listing files to monitor
BACKUP_DIR = f'{dir_path}/backup'
QUARANTINE_DIR = f'{dir_path}/quarantine'
MANIFEST_FILE = 'backup_manifest.csv'  # Manifest file listing file hashes

# Create necessary directories if they don't exist
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)

running = True

def handle_stop_signals(signum, frame):
    global running
    running = False
    logging.info("Received stop signal, shutting down...")

    if os.path.exists(BACKUP_DIR):
        shutil.rmtree(BACKUP_DIR)
        logging.info("Local backup directory deleted.")

def hash_file(filepath):
    """ Generate SHA-256 hash for the specified file """
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except Exception as e:
        logging.error(f"Failed to hash file {filepath}: {e}")
        return None
    
def backup_and_hash_files():
    files_to_monitor = read_cfg_file(MONITOR_CFG)
    manifest = {}
    for filepath in files_to_monitor:
        file_hash = hash_file(filepath)
        stat_info = os.stat(filepath)
        file_permissions = stat_info.st_mode & 0o777
        uid = stat_info.st_uid
        gid = stat_info.st_gid
        if file_hash:
            manifest[filepath] = (file_hash, file_permissions, uid, gid)
            backup_path = shutil.copy2(filepath, BACKUP_DIR)
            logging.info(f"Backed up and hashed file: {filepath}, with permissions {oct(file_permissions)}, UID: {uid}, GID: {gid}. Backup path: {backup_path}")

    with open(os.path.join(BACKUP_DIR, MANIFEST_FILE), 'w') as f:
        for path, (file_hash, permissions, uid, gid) in manifest.items():
            f.write(f"{path},{file_hash},{permissions},{uid},{gid}\n")


def monitor_files():
    local_manifest_path = os.path.join(BACKUP_DIR, MANIFEST_FILE)
    if not os.path.exists(local_manifest_path):
        logging.error(f"Local manifest file does not exist: {local_manifest_path}")
        return
    
    backup_hashes = {}
    backup_permissions = {}
    backup_owners = {}  # Dictionary to hold UID and GID
    with open(local_manifest_path, 'r') as manifest:
        for line in manifest:
            parts = line.strip().split(',')
            filepath, file_hash = parts[0], parts[1]
            permissions, uid, gid = map(int, parts[2:5])  # Correctly extract and convert permissions, UID, and GID
            backup_hashes[filepath] = file_hash
            backup_permissions[filepath] = permissions
            backup_owners[filepath] = (uid, gid)  # Store UID and GID as a tuple

    while running:
        for filepath, expected_hash in backup_hashes.items():
            permissions = backup_permissions[filepath]
            uid, gid = backup_owners[filepath]  # Extract UID and GID
            if os.path.exists(filepath):
                current_hash = hash_file(filepath)
                if current_hash != expected_hash:
                    logging.warning(f"File changed or corrupted: {filepath}")
                    restore_file_from_backup(filepath, expected_hash, permissions, uid, gid)
            else:
                logging.warning(f"File deleted or moved: {filepath}")
                restore_file_from_backup(filepath, expected_hash, permissions, uid, gid)
        time.sleep(10)

def restore_file_from_backup(filepath, expected_hash, permissions, uid, gid):
    filename = os.path.basename(filepath)
    backup_filepath = os.path.join(BACKUP_DIR, filename)
    local_dir = os.path.dirname(filepath)

    os.makedirs(local_dir, exist_ok=True)

    try:
        shutil.copy2(backup_filepath, filepath)
        logging.info(f"Restored file from local backup: {filename}. Restored to: {filepath}")
    except Exception as e:
        logging.error(f"Failed to restore file from local backup {backup_filepath} to {filepath}: {e}")
        return

    try:
        os.chmod(filepath, permissions)
        os.chown(filepath, uid, gid)
        logging.info(f"Successfully applied permissions {oct(permissions)} and ownership (UID: {uid}, GID: {gid}) to {filepath}.")
    except Exception as e:
        logging.error(f"Failed to apply permissions {oct(permissions)} and ownership (UID: {uid}, GID: {gid}) to {filepath}: {e}")

    current_hash = hash_file(filepath)
    if current_hash != expected_hash:
        logging.error(f"Post-recovery integrity check failed for {filepath}.")
    else:
        logging.info(f"Post-recovery integrity check passed for {filepath}.")


def read_cfg_file(cfg_file):
    """ Read the .cfg file and handle folders or whole paths """
    items_to_monitor = []
    with open(cfg_file, 'r') as cfg:
        for line in cfg:
            path = line.strip()
            if os.path.isdir(path):  # If it's a directory, find all files within
                items_to_monitor.extend(find_files(path))
            else:  # Otherwise, assume it's a single file
                items_to_monitor.append(path)
    return items_to_monitor

def find_files(directory):
    """ Recursively find all files in a directory """
    file_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

def main():
    signal.signal(signal.SIGTERM, handle_stop_signals)
    signal.signal(signal.SIGINT, handle_stop_signals)
    
    backup_and_hash_files()
    monitor_files()

if __name__ == "__main__":
    main()