"""__summary__
Script made for LS24
This script is used to monitor some services based on the configuration file ".cfg".


Author: Developer Team CCD PT
"""

import subprocess
import time
import sys
import os
import platform

def check_service(service_name):
    if platform.system() == "Linux":
        try:
            subprocess.check_output(["systemctl", "status", service_name])
            return True
        except subprocess.CalledProcessError:
            return False
    elif platform.system() == "FreeBSD":
        try:
            subprocess.check_output(["service", service_name, "status"])
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        print("Unsupported operating system.")
        sys.exit(1)

def start_service(service_name):
    if platform.system() == "Linux":
        try:
            subprocess.check_output(["sudo", "systemctl", "start", service_name])
            print(f"Service {service_name} started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error starting service {service_name}: {e}")
    elif platform.system() == "FreeBSD":
        try:
            subprocess.check_output(["service", service_name, "status"])
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        print("Unsupported operating system.")
        sys.exit(1)

def read_services_from_config(config_file):
    with open(config_file, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def monitor_services(services, log_file):
    if not os.path.exists(log_file):
        with open(log_file, 'w') as f:
            f.write("Starting log...\n")
    
    while True:
        with open(log_file, 'a') as f:
            sys.stdout = f
            for service in services:
                if not check_service(service):
                    print(f"The service {service} is not running. Starting...")
                    start_service(service)
        sys.stdout = sys.__stdout__
        time.sleep(5)  # Check services every 5 seconds

if __name__ == "__main__":
    config_file = "services.cfg"
    log_file = "service_monitor.log"
    services = read_services_from_config(config_file)
    monitor_services(services, log_file)
