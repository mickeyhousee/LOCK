#!/usr/bin/env python3
"""__summary__
Script made for LS24
This script is a menu to configure the modules.


Author: Development Team CCD PT
"""
import subprocess
import os

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
        subprocess.run(['cp', service_file_path, f'/etc/systemd/system/'], check=True)
        
        # Command to reload systemctl services
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        
        # Command to enable the service
        subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)
        
        # Command to start the service
        subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
        
        print(f'Service {service_name} installed and started successfully!')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while installing service {service_name}: {e}')
    print("Service installed successfully!")

# Function to stop service using systemctl
def stop_service(service_name):
    subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True)
    print("Stopping service...")
    # Commands to stop the service here
    print(f"Service {service_name} stopped successfully!")

def start_service(service_name):
    subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
    print(f"Service {service_name} started successfully!")







###################################### DISPLAY MENU ##############################################


# Function to display "Backup" script menu
def backup_menu():
    while True:
        print("\nBackup script Menu:")
        print("1. Install service (systemctl)")
        print("2. Start \"Backup\" service")
        print("3. Stop \"Backup\" service")
        print("4. Back")

        option = input("Option: ")

        if option == "1":
            install_service()
        elif option == "2":
            start_service()
        elif option == "3":
            stop_service()
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
