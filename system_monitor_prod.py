#!/usr/bin/env python3

import psutil
import time
import argparse
import platform
import logging
from logging.handlers import RotatingFileHandler

LOG_FILE = "system_monitor.log"

logger = logging.getLogger("SystemMonitor")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=3)
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logger.addHandler(console_handler)

def get_cpu_usage():
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        logger.error(f"Could not retrieve CPU usage: {e}")
        return None

def get_memory_usage():
    try:
        return psutil.virtual_memory().percent
    except Exception as e:
        logger.error(f"Could not retrieve Memory usage: {e}")
        return None

def get_disk_usage(path='/'):
    try:
        return psutil.disk_usage(path).percent
    except FileNotFoundError:
        logger.error(f"Disk path '{path}' not found.")
        return None
    except Exception as e:
        logger.error(f"Could not retrieve Disk usage for '{path}': {e}")
        return None

def monitor_system(cpu_threshold, mem_threshold, disk_threshold, disk_path, interval):
    logger.info("System monitor started")
    logger.info(f"Config - Interval: {interval}s, CPU>{cpu_threshold}%, Mem>{mem_threshold}%, Disk>{disk_threshold}% at '{disk_path}'")
    logger.info("-" * 50)

    try:
        while True:
            cpu_usage = get_cpu_usage()
            mem_usage = get_memory_usage()
            disk_usage = get_disk_usage(disk_path)

            cpu_display = f"{cpu_usage:.1f}%" if cpu_usage is not None else "Error"
            mem_display = f"{mem_usage:.1f}%" if mem_usage is not None else "Error"
            disk_display = f"{disk_usage:.1f}%" if disk_usage is not None else "Error"

            logger.info(f"CPU: {cpu_display} | Memory: {mem_display} | Disk ({disk_path}): {disk_display}")

            if cpu_usage is not None and cpu_usage > cpu_threshold:
                logger.warning(f"High CPU Usage: {cpu_usage:.1f}% (Threshold: {cpu_threshold}%)")
            if mem_usage is not None and mem_usage > mem_threshold:
                logger.warning(f"High Memory Usage: {mem_usage:.1f}% (Threshold: {mem_threshold}%)")
            if disk_usage is not None and disk_usage > disk_threshold:
                logger.warning(f"High Disk Usage ({disk_path}): {disk_usage:.1f}% (Threshold: {disk_threshold}%)")

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user.")
    except Exception as e:
        logger.critical(f"Critical error during monitoring: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Production-Ready System Resource Monitor")
    parser.add_argument('--cpu', type=float, default=85.0, help='CPU usage warning threshold (default: 85.0)')
    parser.add_argument('--mem', type=float, default=85.0, help='Memory usage warning threshold (default: 85.0)')
    parser.add_argument('--disk', type=float, default=90.0, help='Disk usage warning threshold (default: 90.0)')
    parser.add_argument('--path', type=str, default='/', help="Disk path to monitor")
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds (default: 5)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    if platform.system() == "Windows" and args.path == '/':
        args.path = 'C:\\'
        logger.info("Windows platform detected. Adjusted disk path to C:\\")

    monitor_system(args.cpu, args.mem, args.disk, args.path, args.interval)
