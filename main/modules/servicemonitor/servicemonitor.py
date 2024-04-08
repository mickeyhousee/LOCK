#!/usr/bin/env python3
"""__summary__
Script made for LS24
This script is used to monitor some services based on the configuration file ".cfg".

Author: Development Team COCIBER PT
"""

import subprocess
import time
import sys
import os
import platform
import logging

def setup_logging(log_file):
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        logging.error("Unsupported operating system.")
        sys.exit(1)

def start_service(service_name):
    if platform.system() == "Linux":
        try:
            subprocess.check_output(["sudo", "systemctl", "start", service_name])
            logging.info(f"Service {service_name} started successfully.")
        except subprocess.CalledProcessError as e:
            logging.error(f"Error starting service {service_name}: {e}")
    elif platform.system() == "FreeBSD":
        try:
            subprocess.check_output(["service", service_name, "status"])
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        logging.error("Unsupported operating system.")
        sys.exit(1)

def read_services_from_config(config_file):
    with open(config_file, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def monitor_services(services):
    while True:
        for service in services:
            if not check_service(service):
                logging.warning(f"The service {service} is not running. Starting...")
                start_service(service)
        time.sleep(5)  # Check services every 5 seconds

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file = f"{dir_path}/services.cfg"
    log_file = f"{dir_path}/service_monitor.log"
    setup_logging(log_file)
    try:
        services = read_services_from_config(config_file)
        monitor_services(services)
        logging.info("Script started successfully.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
