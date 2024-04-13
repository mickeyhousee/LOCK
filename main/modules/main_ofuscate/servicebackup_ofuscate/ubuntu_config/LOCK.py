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
import pwd
import grp
import sys
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
SCP_SERVER = '172.20.10.4'
SCP_USER = 'joaog'
SCP_PASSWORD = 'joaog'  # It's recommended to use SSH key authentication instead
SCP_REMOTE_PATH = '/tmp/backups'

# Relative Path
dir_path = os.path.dirname(sys.executable)

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
    ssh_session = create_scp_session()
    local_manifest_path = os.path.join(BACKUP_DIR, MANIFEST_FILE)
    fetch_backup_manifest(ssh_session, local_manifest_path)
    
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
                    restore_file_from_backup(ssh_session, filepath, expected_hash, permissions, uid, gid)
            else:
                logging.warning(f"File deleted or moved: {filepath}")
                restore_file_from_backup(ssh_session, filepath, expected_hash, permissions, uid, gid)
                
        send_logs_to_scp(ssh_session)
        time.sleep(10)

    ssh_session.close()


def restore_file_from_backup(ssh_session, filepath, expected_hash, permissions, uid, gid):
    remote_backup_dir = os.path.join(SCP_REMOTE_PATH, local_ip)
    filename = os.path.basename(filepath)
    remote_backup_filepath = os.path.join(remote_backup_dir, 'backup', filename)
    local_dir = os.path.dirname(filepath)

    os.makedirs(local_dir, exist_ok=True)
    
    with SCPClient(ssh_session.get_transport()) as scp:
        scp.get(remote_backup_filepath, local_path=filepath)
    logging.info(f"Restored file from backup: {filename}. Restored to: {filepath}")

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
