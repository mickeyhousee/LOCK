import time
import hashlib
import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Function to hash the contents of a file using SHA-256
def hash_file(filename):
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# Function to save the current file hashes to a JSON file
def save_hashes(hashes, filepath):
    with open(filepath, 'w') as file:
        json.dump(hashes, file, indent=4)

# Function to load the hashes from a JSON file
def load_hashes(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            return json.load(file)
    return {}

# Handler class for the watchdog observer
class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:  # Ignore changes to directories
            self.check_file(event.src_path)

    def check_file(self, file_path):
        filename = os.path.basename(file_path)
        current_hash = hash_file(file_path)
        if filename in known_hashes:
            if current_hash != known_hashes[filename]:
                print(f"ALERT: Hash for file '{filename}' has changed.")
                known_hashes[filename] = current_hash
                save_hashes(known_hashes, hash_storage_file)
        else:
            print(f"New file '{filename}' detected with hash {current_hash}.")
            known_hashes[filename] = current_hash
            save_hashes(known_hashes, hash_storage_file)

# Load the initial known hashes
hash_storage_file = "known_hashes.json"
known_hashes = load_hashes(hash_storage_file)

# Set the directory path you want to monitor
path_to_monitor = "files"  # Replace this with the path you want to monitor

# Set up the observer
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
