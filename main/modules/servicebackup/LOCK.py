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
import os
import stat

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

# SCP server details
SCP_SERVER = '192.168.151.105'
SCP_USER = 'joaog'
SCP_PASSWORD = 'joaog'  # It's recommended to use SSH key authentication instead
SCP_REMOTE_PATH = '/tmp/backups'

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
    Transfer a file or directory to the SCP server, ensuring the remote path exists.
    
    :param ssh_session: An active SSH session.
    :param local_path: The local path of the file or directory to transfer.
    :param remote_path: The remote destination path on the SCP server.
    """
    # Command to create the remote directory structure if it doesn't exist
    mkdir_command = f'mkdir -p {remote_path}'
    
    # Execute the mkdir command on the remote server
    stdin, stdout, stderr = ssh_session.exec_command(mkdir_command)
    exit_status = stdout.channel.recv_exit_status()  # Wait for the command to complete
    
    if exit_status == 0:
        logging.info(f"Ensured remote directory exists: {remote_path}.")
    else:
        logging.error(f"Failed to ensure remote directory exists: {remote_path}. stderr: {stderr.read().decode()}")
        return  # Exit if the directory could not be created

    # Proceed to transfer the file or directory
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.put(local_path, remote_path=remote_path, recursive=True)
        logging.info(f"Successfully transferred {local_path} to {remote_path}.")



def backup_and_hash_files():
    """ Backup and hash files listed in the .cfg file """
    files_to_monitor = read_cfg_file(MONITOR_CFG)

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
    scp_transfer(ssh_session, BACKUP_DIR, os.path.join(SCP_REMOTE_PATH, local_ip))
    ssh_session.close()

    logging.info("Backup files and manifest transferred to SCP server.")

def send_logs_to_scp(ssh_session):
    """ Send the logs to SCP server """
    remote_log_file = os.path.join(SCP_REMOTE_PATH, local_ip, log_file)
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.put(log_file, remote_path=remote_log_file)

def fetch_backup_manifest(ssh_session, local_manifest_path):
    """Download the backup manifest file from the SCP server."""
    remote_manifest_path = os.path.join(SCP_REMOTE_PATH, local_ip, MANIFEST_FILE)
    
    # Attempt to check if the remote manifest exists before fetching
    stdin, stdout, stderr = ssh_session.exec_command(f"test -f {remote_manifest_path} && echo 'exists' || echo 'not exists'")
    if stdout.read().decode().strip() != "exists":
        logging.error(f"Remote manifest file does not exist: {remote_manifest_path}")
        # Handle the error (e.g., retry, create a new file, or abort)
        return
    
    with SCPClient(ssh_session.get_transport()) as scp:
        try:
            scp.get(remote_manifest_path, local_manifest_path)
        except SCPException as e:
            logging.error(f"Failed to fetch manifest: {e}")
            # Additional error handling here


def monitor_files():
    """Monitor the files for any changes based on the backup manifest from the SCP server."""
    ssh_session = create_scp_session()
    local_manifest_path = os.path.join(BACKUP_DIR, MANIFEST_FILE)
    fetch_backup_manifest(ssh_session, local_manifest_path)
    
    # Load the backup hashes from the manifest file
    backup_hashes = {}
    with open(local_manifest_path, 'r') as manifest:
        for line in manifest:
            filepath, file_hash = line.strip().split(',', 1)
            backup_hashes[filepath] = file_hash

    while running:
        for filepath, expected_hash in backup_hashes.items():
            # Check if the file exists
            if os.path.exists(filepath):
                # If it exists, hash the current file and compare
                current_hash = hash_file(filepath)
                if current_hash != expected_hash:
                    logging.warning(f"File changed or corrupted: {filepath}")
                    restore_file_from_backup(ssh_session, filepath, expected_hash)
            else:
                # If the file does not exist, restore it from backup
                logging.warning(f"File deleted or moved: {filepath}")
                restore_file_from_backup(ssh_session, filepath, expected_hash)
                
            # Consider adding a short sleep here if you're monitoring a large number of files
            # to reduce CPU usage. For example, time.sleep(0.1)

        # Optionally, send logs to SCP every cycle or at fixed intervals
        # This is a placeholder function call; implement according to your logging requirements
        # send_logs_to_scp(ssh_session)
        
        # Wait some time before the next check to reduce load on the server
        time.sleep(10)  # Adjust the sleep time as needed

    ssh_session.close()


def restore_file_from_backup(ssh_session, filepath, expected_hash):
    """Restore the file from the backup on the SCP server and check its integrity."""
    remote_backup_dir = os.path.join(SCP_REMOTE_PATH, local_ip)
    filename = os.path.basename(filepath)
    remote_backup_filepath = os.path.join(remote_backup_dir, 'backup', filename)
    local_dir = os.path.dirname(filepath)
    
    # Ensure local directory structure exists
    os.makedirs(local_dir, exist_ok=True)
    
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.get(remote_backup_filepath, local_path=local_dir)
    logging.info(f"Restored file from backup: {filename}")
    
    # Post-recovery integrity check
    current_hash = hash_file(filepath)
    if current_hash != expected_hash:
        logging.error(f"Post-recovery integrity check failed for {filepath}. The file may have been tampered with.")
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