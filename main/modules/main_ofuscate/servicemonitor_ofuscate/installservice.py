#!/usr/bin/env python3
"""__summary__
Script made for LS24
This script is used to install a service based on ".service" file.

Author: Development Team COCIBER PT
"""
import subprocess
import os
import platform

def install_service(file_path, service_file_path, service_name):
    try:
        if 'freebsd' in platform.platform().lower():
            # Update ExecStart in service file with file_path
            with open(service_file_path, 'r') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("    /usr/local/bin/python3"):
                    lines[i] = f"    /usr/local/bin/python3 {file_path} & echo $! > /var/run/{service_name}.pid\n"

            with open(service_file_path, 'w') as file:
                file.writelines(lines)


            # Set executable permissions on the file
            subprocess.run(['chmod', '+x', file_path], check=True)

            # Copy service file to appropriate directory
            subprocess.run(['cp', service_file_path, '/etc/rc.d/'], check=True)


            dir_path_process = f"/etc/rc.d/{service_name}"
            # Set executable permissions on the file
            subprocess.run(['chmod', '+x', dir_path_process], check=True)

            process_enable = f"{service_name}_enable=YES"
            subprocess.run(['sysrc', process_enable])
        
            # Start the service
            subprocess.run(['service', service_name, 'start'], check=True)

            print(f'Service {service_name} installed and started successfully!')
        else:  # Assume Ubuntu or similar
            # Update ExecStart in service file with file_path
            with open(service_file_path, 'r') as file:
                lines = file.readlines()

            for i, line in enumerate(lines):
                if line.startswith("ExecStart="):
                    lines[i] = f"ExecStart={file_path}\n"

            with open(service_file_path, 'w') as file:
                file.writelines(lines)

            # Set executable permissions on the file
            subprocess.run(['sudo', 'chmod', '+x', file_path], check=True)

            # Copy service file to appropriate directory
            subprocess.run(['sudo', 'cp', service_file_path, '/etc/systemd/system/'], check=True)

            # Reload systemctl services
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)

            # Enable the service
            subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)

            subprocess.run(['sudo', 'rm' 'servicemonitor.py'])


            # Start the service
            subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)

            print(f'Service {service_name} installed and started successfully!')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while installing service {service_name}: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

dir_path = os.path.dirname(os.path.realpath(__file__))

file_path = f"{dir_path}/ubuntu_config/sylogd.py"
file_path_bsd = f"{dir_path}/freebsd_config/servicemonitor_clear.py"

service_file_path = f"{dir_path}/ubuntu_config/sylogd.service"
service_file_path_BSD = f"{dir_path}/freebsd_config/sylogdbsd"

service_name = "sylogd"
service_name_BSD = "sylogdbsd"

if 'freebsd' in platform.platform().lower():
    install_service(file_path_bsd, service_file_path_BSD, service_name_BSD)
else:
    install_service(file_path, service_file_path, service_name)
