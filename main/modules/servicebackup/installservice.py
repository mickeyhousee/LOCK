#!/usr/bin/env python3
"""__summary__
Script made for LS24
This script is used to install a service based on ".service" file.

Author: Development Team COCIBER PT
"""
import subprocess
import os

def install_service(file_path, service_file_path, service_name):
    try:
        # Update ExecStart in service file with file_path
        with open(service_file_path, 'r') as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if line.startswith("ExecStart="):
                lines[i] = f"ExecStart={file_path}\n"

        with open(service_file_path, 'w') as file:
            file.writelines(lines)

        # Set executable permissions on the file
        subprocess.run(['chmod', '+x', file_path], check=True)

        # Copy service file to appropriate directory
        subprocess.run(['sudo', 'cp', service_file_path, '/etc/systemd/system/'], check=True)

        # Reload systemctl services
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)

        # Enable the service
        subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)

        # Start the service
        subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)

        print(f'Service {service_name} installed and started successfully!')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while installing service {service_name}: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

dir_path = os.path.dirname(os.path.realpath(__file__))
file_path = f"{dir_path}/LOCK"
service_file_path = f"{dir_path}/LOCK.service"
service_name = "LOCK"
install_service(file_path, service_file_path, service_name)
