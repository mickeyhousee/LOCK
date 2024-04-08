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
from logging.handlers import RotatingFileHandler
import socket

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
SCP_SERVER = '192.168.151.105'
SCP_USER = 'joaog'
SCP_PASSWORD = 'joaog'  # It's recommended to use SSH key authentication instead
SCP_REMOTE_PATH = '/home/joaog'

# Relative Path
dir_path = os.path.dirname(os.path.realpath(__file__))

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't actually send data
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
    finally:
        s.close()
    return IP

# Directories and file paths
MONITOR_CFG = f'{dir_path}/services.cfg'  # Config file listing files to monitor
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

def create_scp_session():
    """ Create an SCP session for file transfers """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(SCP_SERVER, username=SCP_USER, password=SCP_PASSWORD)
    return ssh

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
    
def scp_transfer(ssh_session, local_path, remote_path):
    """
    Transfer a file or directory to the SCP server.
    
    :param ssh_session: An active SSH session.
    :param local_path: The local path of the file or directory to transfer.
    :param remote_path: The remote destination path on the SCP server.
    """
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.put(local_path, remote_path=remote_path, recursive=True)

def backup_and_hash_files():
    """ Backup and hash files listed in the .cfg file """
    with open(MONITOR_CFG, 'r') as cfg:
        files_to_monitor = cfg.read().splitlines()

    manifest = {}
    for filepath in files_to_monitor:
        file_hash = hash_file(filepath)
        if file_hash:
            manifest[filepath] = file_hash
            # Backup the file
            shutil.copy2(filepath, BACKUP_DIR)
            logging.info(f"Backed up and hashed file: {filepath}")

    # Write hashes to manifest file
    with open(os.path.join(BACKUP_DIR, MANIFEST_FILE), 'w') as f:
        for path, file_hash in manifest.items():
            f.write(f"{path},{file_hash}\n")

    # SCP transfer the backup directory
    ssh_session = create_scp_session()
    scp_transfer(ssh_session, BACKUP_DIR, os.path.join(SCP_REMOTE_PATH, get_local_ip()))
    ssh_session.close()

    logging.info("Backup files and manifest transferred to SCP server.")


def fetch_backup_manifest(ssh_session, local_manifest_path):
    """ Download the backup manifest file from the SCP server """
    remote_manifest_path = os.path.join(SCP_REMOTE_PATH, get_local_ip(), MANIFEST_FILE)
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.get(remote_manifest_path, local_manifest_path)

def monitor_files():
    """ Monitor the files for any changes based on the backup manifest from the SCP server """
    ssh_session = create_scp_session()
    local_manifest_path = os.path.join(BACKUP_DIR, MANIFEST_FILE)
    fetch_backup_manifest(ssh_session, local_manifest_path)
    
    with open(local_manifest_path, 'r') as manifest:
        backup_hashes = {line.split(',')[0]: line.strip().split(',')[1] for line in manifest.readlines()}

    while running:
        for filepath, backup_hash in backup_hashes.items():
            if os.path.exists(filepath):
                current_hash = hash_file(filepath)
                if current_hash != backup_hash:
                    logging.warning(f"File changed or corrupted: {filepath}")
                    restore_file_from_backup(ssh_session, filepath)
            else:
                logging.warning(f"File deleted or moved: {filepath}")
        time.sleep(5)  # Modify as needed for your use case

    ssh_session.close()

def restore_file_from_backup(ssh_session, filepath):
    """ Restore the file from the backup on the SCP server """
    remote_backup_dir = os.path.join(SCP_REMOTE_PATH, get_local_ip())
    filename = os.path.basename(filepath)
    remote_backup_filepath = os.path.join(remote_backup_dir, filename)
    local_dir = os.path.dirname(filepath)
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.get(remote_backup_filepath, local_dir)
    logging.info(f"Restored file from backup: {filename}")

def main():
    signal.signal(signal.SIGTERM, handle_stop_signals)
    signal.signal(signal.SIGINT, handle_stop_signals)
    
    backup_and_hash_files()
    monitor_files()

if __name__ == "__main__":
    main()
