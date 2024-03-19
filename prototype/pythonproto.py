import hashlib
import os
import shutil
import time

# Define the directory for storing original and backup files
original_files_dir = 'original_files'
backup_files_dir = 'backup_files'
quarantine_dir = 'quarantine'

os.makedirs(original_files_dir, exist_ok=True)
os.makedirs(backup_files_dir, exist_ok=True)
os.makedirs(quarantine_dir, exist_ok=True)

# hashing of a file
def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        buffer = file.read()
        hasher.update(buffer)
    return hasher.hexdigest()

# Hashing the files and storing the hashes
def initial_setup(file_paths):
    hashes = {}
    for file_path in file_paths:
        print(f"Hashing file {file_path}")
        hash_of_file = hash_file(file_path)
        hashes[file_path] = hash_of_file
        # Create a backup of the file
        shutil.copy(file_path, backup_files_dir)
        print(f"Backup created for {file_path}")
    return hashes

# Function to check for changes in the files
def check_for_changes(file_paths, stored_hashes):
    changes_detected = False
    for file_path in file_paths:
        current_hash = hash_file(file_path)
        if current_hash != stored_hashes[file_path]:
            changes_detected = True
            print(f"Change detected in {file_path}. Generating alert...")
            quarantine_path = os.path.join(quarantine_dir, os.path.basename(file_path))
            if os.path.exists(quarantine_path):
                # Rename the existing file in quarantine with a timestamp
                new_name = f"{os.path.splitext(quarantine_path)[0]}_{int(time.time())}{os.path.splitext(quarantine_path)[1]}"
                os.rename(quarantine_path, new_name)
                print(f"Existing quarantine file renamed to {new_name}.")
            # Move the new file to quarantine
            shutil.move(file_path, quarantine_dir)
            print(f"File {file_path} moved to quarantine.")
            # Restore the file from backup
            backup_path = os.path.join(backup_files_dir, os.path.basename(file_path))
            shutil.copy(backup_path, file_path)
            print(f"File {file_path} restored from backup.")
    return changes_detected

def continuous_monitoring(file_paths, stored_hashes):
    print("Starting continuous monitoring for approximately 1 minute...")
    end_time = time.time() + 60 
    try:
        while time.time() < end_time:  # Run until the current time is less than the end time
            print("Checking for changes...")
            if check_for_changes(file_paths, stored_hashes):
                print("Changes detected. Updating hash list and continuing monitoring...")
                for file_path in file_paths:
                    stored_hashes[file_path] = hash_file(file_path)
            time.sleep(10)  # Wait for 10 seconds before the next check
    except KeyboardInterrupt:
        print("Monitoring stopped by user.")

# Sample files creation for the prototype
sample_files = [os.path.join(original_files_dir, 'sample1.txt'), os.path.join(original_files_dir, 'sample2.txt')]
for sample_file in sample_files:
    with open(sample_file, 'w') as f:
        f.write(f"This is a sample file named {os.path.basename(sample_file)}.")

# Running the initial setup
stored_hashes = initial_setup(sample_files)

# Output the result of initial setup
stored_hashes

# Simulate the continuous monitoring
continuous_monitoring(sample_files, stored_hashes)

with open(sample_files[0], 'a') as f:
    f.write("\nModification to the file to simulate a change.")

continuous_monitoring(sample_files, stored_hashes)
