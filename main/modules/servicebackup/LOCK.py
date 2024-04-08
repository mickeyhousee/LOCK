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
import paramiko
from scp import SCPClient
import signal

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("monitoring.log", maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)

# SCP server details
SCP_SERVER = ''
SCP_USER = ''
SCP_PASSWORD = ''  # It's recommended to use SSH key authentication instead
SCP_REMOTE_PATH = ''

# Relative Path
dir_path = os.path.dirname(os.path.realpath(__file__))

# Directories and file paths
MONITOR_CFG = f'{dir_path}/files_to_monitor.cfg'  # Config file listing files to monitor
BACKUP_DIR = f'{dir_path}/backup'
QUARANTINE_DIR = f'{dir_path}/quarantine'
HASH_FILE = 'hashes.csv'

# Create necessary directories if they don't exist
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)

running = True

def handle_stop_signals(signum, frame):
    global running
    running = False
    logging.info("Received stop signal, shutting down...")

def create_scp_session(host, user, password):
    """ Create an SCP session for file transfers """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    return ssh

def scp_transfer(ssh_session, files, remote_path):
    """ Transfer files using SCP """
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.put(files, remote_path)

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
    """ Backup and hash files listed in the .cfg file """
    hashes = {}
    with open(MONITOR_CFG, 'r') as cfg:
        files_to_monitor = cfg.read().splitlines()

    for filepath in files_to_monitor:
        file_hash = hash_file(filepath)
        if file_hash:
            hashes[filepath] = file_hash
            # Backup the file
            shutil.copy2(filepath, BACKUP_DIR)
            logging.info(f"Backed up and hashed file: {filepath}")

    # Write hashes to file
    with open(HASH_FILE, 'w') as f:
        for path, file_hash in hashes.items():
            f.write(f"{path},{file_hash}\n")

    # SCP transfer the hashes and the backup
    ssh_session = create_scp_session(SCP_SERVER, SCP_USER, SCP_PASSWORD)
    scp_transfer(ssh_session, [HASH_FILE] + files_to_monitor, SCP_REMOTE_PATH)
    ssh_session.close()

    logging.info(f"Backup files and hashes transferred to SCP server.")

    return hashes

def monitor_files(hashes):
    """ Monitor the files for any changes based on the hashes """
    while running:
        for filepath in hashes:
            if os.path.exists(filepath):
                current_hash = hash_file(filepath)
                if current_hash != hashes[filepath]:
                    logging.warning(f"File changed or corrupted: {filepath}")
                    restore_file_from_backup(filepath)
            else:
                logging.warning(f"File deleted or moved: {filepath}")
        time.sleep(5)  # Modify as needed for your use case

def restore_file_from_backup(filepath):
    """ Restore the file from the backup """
    filename = os.path.basename(filepath)
    backup_filepath = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_filepath):
        shutil.copy2(backup_filepath, filepath)
        logging.info(f"Restored file from backup: {filename}")
    else:
        logging.error(f"Backup file not found for {filename}")

def system_startup():
    """ Perform actions on system startup """
    hashes = backup_and_hash_files()
    monitor_files(hashes)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, handle_stop_signals)
    signal.signal(signal.SIGINT, handle_stop_signals)
    system_startup()
