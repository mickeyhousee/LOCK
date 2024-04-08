#!/usr/bin/env python3
"""__summary__
Script made for LS24

Author: Development Team COCIBER PT
"""
import hashlib
import os
import shutil
import logging
import time 
from datetime import datetime
from logging.handlers import RotatingFileHandler


# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("monitoring.log", maxBytes=10485760, backupCount=10),
        logging.StreamHandler()
    ]
)
# Relative Path
dir_path = os.path.dirname(os.path.realpath(__file__))

print(dir_path)
# Directories and file paths (to be adjusted to your actual paths)
MONITOR_DIR = f'{dir_path}/monitor'  # Directory containing files to be monitored
BACKUP_DIR = '/home/onezero/LOCK/prototype/backup'  # Directory where backups will be stored
QUARANTINE_DIR = '/home/onezero/LOCK/prototype/quarantine'  # Directory where suspicious files will be quarantined
HASH_FILE = 'hashes.csv'  # File where current hashes will be stored
BACKUP_HASH_FILE = 'backup_hashes.csv'  # File where backup hashes will be stored

# Create necessary directories if they don't exist
os.makedirs(MONITOR_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(QUARANTINE_DIR, exist_ok=True)

def create_service():
    """ Placeholder for the OS-specific service creation logic """
    logging.info("Service creation logic goes here.")

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

def initial_hashing():
    """ Hash all files in the monitoring directory and backup the hashes """
    hashes = {}
    with open(HASH_FILE, 'w') as f, open(BACKUP_HASH_FILE, 'w') as bf:
        for filename in os.listdir(MONITOR_DIR):
            filepath = os.path.join(MONITOR_DIR, filename)
            file_hash = hash_file(filepath)
            if file_hash:
                hashes[filepath] = file_hash
                f.write(f"{filepath},{file_hash}\n")
                bf.write(f"{filepath},{file_hash}\n")
                # Create a backup copy of the file
                shutil.copy2(filepath, BACKUP_DIR)
                logging.info(f"Hashed and backed up {filepath}")
    # Make hash storage read-only
    os.chmod(HASH_FILE, 0o444)

def monitor_files():
    """ Continuously monitor the files for changes """
    while True:
        with open(HASH_FILE, 'r') as f:
            current_hashes = {line.split(',')[0]: line.split(',')[1].strip() for line in f.readlines()}
        for filepath, saved_hash in current_hashes.items():
            if os.path.exists(filepath):
                current_hash = hash_file(filepath)
                if current_hash != saved_hash:
                    logging.warning(f"File changed or corrupted: {filepath}")
                    quarantine_file(filepath)
            else:
                logging.warning(f"File deleted or moved: {filepath}")
                quarantine_file(filepath)
        time.sleep(5)  # Interval for checking file changes

def quarantine_file(filepath):
    """ Move the file to the quarantine directory and restore from backup if necessary """
    # Extract the filename from the filepath
    filename = os.path.basename(filepath)
    # Move the file to the quarantine directory
    shutil.move(filepath, os.path.join(QUARANTINE_DIR, filename))
    logging.info(f"Moved {filename} to quarantine.")
    # Restore the file from the backup
    backup_filepath = os.path.join(BACKUP_DIR, filename)
    if os.path.exists(backup_filepath):
        shutil.copy2(backup_filepath, MONITOR_DIR)
        logging.info(f"Restored {filename} from backup.")

def system_startup():
    """ Perform actions on system startup """
    create_service()
    initial_hashing()
    monitor_files()

if __name__ == "__main__":
    system_startup()
