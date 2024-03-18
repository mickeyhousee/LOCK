import time
import hashlib
import os
import json
import shutil
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

print(f"Current Working Directory: {os.getcwd()}")  # Print the current working directory

def hash_file(filename):
    try:
        hasher = hashlib.sha256()
        with open(filename, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        hash_value = hasher.hexdigest()
        print(f"Hashing file: {filename}, Hash: {hash_value}")
        return hash_value
    except FileNotFoundError:
        print(f"File not found during hashing: {filename}")
        return None

def save_hashes(hashes, filepath):
    try:
        with open(filepath, 'w') as file:
            json.dump(hashes, file, indent=4)
        print(f"Hashes successfully saved to {filepath}.")
        # Debug: Read and print the content right after saving
        with open(filepath, 'r') as file:
            print(f"Debug content after saving: {file.read()}")
    except Exception as e:
        print(f"Failed to save hashes to {filepath}. Error: {e}")

def load_hashes(filepath):
    try:
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, 'r') as file:
                print(f"Loading hashes from {filepath}.")
                return json.load(file)
        else:
            print(f"{filepath} is empty or doesn't exist. Starting with an empty hash table.")
            return {}
    except json.JSONDecodeError as e:
        print(f"Error reading {filepath}. File might be corrupt. Starting with an empty hash table. Error: {e}")
        return {}

def initial_hashing(path, hash_storage):
    hashes = load_hashes(hash_storage)
    for root, _, files in os.walk(path):
        for name in files:
            file_path = os.path.join(root, name)
            file_hash = hash_file(file_path)
            if file_hash:
                hashes[name] = file_hash
    save_hashes(hashes, hash_storage)

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and not event.src_path.endswith('.bak'):
            self.process_file_change(event.src_path)

    def process_file_change(self, file_path):
        filename = os.path.basename(file_path)
        current_hash = hash_file(file_path)
        if current_hash is None:
            return

        if filename in known_hashes:
            if current_hash != known_hashes[filename]:
                known_hashes[filename] = current_hash
                save_hashes(known_hashes, hash_storage_file)
                print(f"ALERT: Hash for file '{filename}' has changed.")
                backup_filename = f"{filename}.{int(datetime.now().timestamp())}.bak"
                backup_path = os.path.join(os.path.dirname(file_path), backup_filename)
                shutil.copy2(file_path, backup_path)
                print(f"Backup of '{filename}' created as '{backup_filename}'.")
                os.remove(file_path)
                print(f"Original file '{filename}' deleted after hash change.")
        else:
            known_hashes[filename] = current_hash
            save_hashes(known_hashes, hash_storage_file)
            print(f"New file '{filename}' detected and hashed.")

def test_file_write():
    """A simple write test to manually test file writing capabilities."""
    test_data = {"test": "value"}
    try:
        with open("test_known_hashes.json", 'w') as file:
            json.dump(test_data, file, indent=4)
        print("Test write completed. Check 'test_known_hashes.json' for test data.")
    except Exception as e:
        print(f"Test write failed. Error: {e}")

hash_storage_file = "known_hashes.json"
path_to_monitor = "files"  # Adjust to your directory

# Perform a manual file write test
test_file_write()

# Perform initial hashing of all files and save the state
initial_hashing(path_to_monitor, hash_storage_file)

# Load the latest state of known hashes
known_hashes = load_hashes(hash_storage_file)

# Setup watchdog to monitor the directory for changes
event_handler = ChangeHandler()
observer = Observer()
observer.schedule(event_handler, path_to_monitor, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
