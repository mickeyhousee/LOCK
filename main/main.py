#!/usr/bin/env python3
"""
Script made for LS24
Menu to configure modules via systemd

Author: Development Team CCD PT
"""

import subprocess
import os
import sys


# ------------------------- SERVICE FUNCTIONS -------------------------

def install_service(file_path, service_file_path, service_name):
    print(f"Installing service: {service_name}")

    if not os.path.isfile(file_path):
        print(f"ERROR: Script not found -> {file_path}")
        return

    if not os.path.isfile(service_file_path):
        print(f"ERROR: Service file not found -> {service_file_path}")
        return

    # Update ExecStart
    with open(service_file_path, "r") as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("ExecStart="):
            lines[i] = f"ExecStart={file_path}\n"

    with open(service_file_path, "w") as file:
        file.writelines(lines)

    try:
        subprocess.run(["chmod", "+x", file_path], check=True)
        subprocess.run(["cp", service_file_path, "/etc/systemd/system/"], check=True)
        subprocess.run(["systemctl", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "enable", service_name], check=True)
        subprocess.run(["systemctl", "start", service_name], check=True)

        print(f"Service '{service_name}' installed and started successfully!")

    except subprocess.CalledProcessError as e:
        print(f"ERROR installing service '{service_name}': {e}")


def start_service(service_name):
    try:
        subprocess.run(["systemctl", "start", service_name], check=True)
        print(f"Service '{service_name}' started successfully!")
    except subprocess.CalledProcessError as e:
        print(f"ERROR starting service '{service_name}': {e}")


def stop_service(service_name):
    try:
        subprocess.run(["systemctl", "stop", service_name], check=True)
        print(f"Service '{service_name}' stopped successfully!")
    except subprocess.CalledProcessError as e:
        print(f"ERROR stopping service '{service_name}': {e}")


# ------------------------- MENUS -------------------------

def backup_menu():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{dir_path}/modules/backup/backup.py"
    service_file_path = f"{dir_path}/modules/backup/backup.service"
    service_name = "backup"

    while True:
        print("\nBackup Script Menu:")
        print("1. Install service")
        print("2. Start Backup service")
        print("3. Stop Backup service")
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


def service_monitor_menu():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = f"{dir_path}/modules/servicemonitor/servicemonitor.py"
    service_file_path = f"{dir_path}/modules/servicemonitor/servicemonitor.service"
    service_name = "servicemonitor"

    while True:
        print("\nServiceMonitor Script Menu:")
        print("1. Install service")
        print("2. Start ServiceMonitor service")
        print("3. Stop ServiceMonitor service")
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


# ------------------------- MAIN -------------------------

def main():
    if os.geteuid() != 0:
        print("ERROR: Run this script as root.")
        sys.exit(1)

    while True:
        print("\nSelect an option:")
        print("1. Backup Script")
        print("2. ServiceMonitor Script")
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


if __name__ == "__main__":
    main()
