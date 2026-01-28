#!/usr/bin/env python3
"""__summary__
Script made for LS24
This script is a menu to configure the modules.


Author: Development Team CCD PT
"""
import subprocess
import os
import shutil

# Function to install service using systemctl
def install_service(file_path, service_file_path, service_name):
    print("Installing Service")
    with open(service_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("ExecStart="):
            lines[i] = f"ExecStart={file_path}\n"

    with open(service_file_path, 'w') as file:
        file.writelines(lines)
    try:
        subprocess.run(['chmod', '+x', file_path], check=True)

        # Command to copy service file to appropriate directory
        subprocess.run(['cp', service_file_path, '/etc/systemd/system/'], check=True)

        # Determine whether to use sudo for systemctl commands
        use_sudo = shutil.which('sudo') is not None
        has_systemctl = shutil.which('systemctl') is not None

        def run_systemctl(args):
            if not has_systemctl:
                print("WARNING: 'systemctl' is not available in this environment. "
                      "Service was not registered with systemd.")
                return
            cmd = ['systemctl'] + args
            if use_sudo:
                cmd.insert(0, 'sudo')
            subprocess.run(cmd, check=True)

        # Command to reload systemctl services
        run_systemctl(['daemon-reload'])

        # Command to enable the service
        run_systemctl(['enable', service_name])

        # Command to start the service
        run_systemctl(['start', service_name])
        
        print(f'Service {service_name} installed and started successfully!')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while installing service {service_name}: {e}')
    print("Service installed successfully!")

# Function to stop service using systemctl
def stop_service(service_name):
    has_systemctl = shutil.which('systemctl') is not None
    if not has_systemctl:
        print("WARNING: 'systemctl' is not available in this environment. "
              "Service stop command was not executed.")
        return

    use_sudo = shutil.which('sudo') is not None
    cmd = ['systemctl', 'stop', service_name]
    if use_sudo:
        cmd.insert(0, 'sudo')
    subprocess.run(cmd, check=True)
    print("Stopping service...")
    # Commands to stop the service here
    print(f"Service {service_name} stopped successfully!")

def start_service(service_name):
    has_systemctl = shutil.which('systemctl') is not None
    if not has_systemctl:
        print("WARNING: 'systemctl' is not available in this environment. "
              "Service start command was not executed.")
        return

    use_sudo = shutil.which('sudo') is not None
    cmd = ['systemctl', 'start', service_name]
    if use_sudo:
        cmd.insert(0, 'sudo')
    subprocess.run(cmd, check=True)
    print(f"Service {service_name} started successfully!")







###################################### DISPLAY MENU ##############################################


# Function to display "Backup" script menu
def backup_menu():
    # Paths and service name for the backup service
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{dir_path}/modules/servicebackup/LOCK.py"
    service_file_path = f"{dir_path}/modules/servicebackup/LOCK.service"
    service_name = "LOCK"

    while True:
        print("\nBackup script Menu:")
        print("1. Install service (systemctl)")
        print("2. Start \"Backup\" service")
        print("3. Stop \"Backup\" service")
        print("4. Back")

        option = input("Option: ")

        if option == "1":
            install_service(file_path, service_file_path, service_name)
        elif option == "2":
            start_service(service_name)
        elif option == "3":
            stop_service(service_name)
        elif option == "4":
            break
        else:
            print("Invalid option!")

# Function to display "ServiceMonitor" script menu
def service_monitor_menu():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{dir_path}/modules/servicemonitor/servicemonitor.py"
    service_file_path = f"{dir_path}/modules/servicemonitor/servicemonitor.service"
    service_name = "servicemonitor"
    while True:
        print("\nServiceMonitor script Menu:")
        print("1. Install service (systemctl)")
        print("2. Start \"Backup\" ServiceMonitor")
        print("3. Stop \"Backup\" ServiceMonitor")
        print("4. Back")

        option = input("Option: ")

        if option == "1":
            install_service(file_path, service_file_path, service_name)
        elif option == "2":
            start_service(service_name)
        elif option == "3":
            stop_service(service_name)
        elif option == "4":
            break
        else:
            print("Invalid option!")

# Main menu loop
while True:
    print("\nSelect an option:")
    print("1. \"Backup\" Script")
    print("2. \"ServiceMonitor\" Script")
    print("3. Exit")

    option = input("Option: ")

    if option == "1":
        backup_menu()
    elif option == "2":
        service_monitor_menu()
    elif option == "3":
        print("Exiting...")
        break
    else:
        print("Invalid option!")