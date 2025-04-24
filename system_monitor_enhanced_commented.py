#!/usr/bin/env python3

import psutil
import time
import argparse
import platform
import logging
import json
import smtplib
from email.message import EmailMessage
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Configuration constants
LOG_FILE = "system_monitor.log"
ALERT_EMAIL = "alert@example.com"
EMAIL_ENABLED = False

# Send alert emails if enabled
def send_email_alert(subject, body):
    if not EMAIL_ENABLED:
        return
    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = ALERT_EMAIL
        msg["To"] = ALERT_EMAIL
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

# Logger setup with rotating file and console handlers
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

# Retrieve CPU usage percentage
def get_cpu_usage():
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        logger.error(f"Could not retrieve CPU usage: {e}")
        return None

# Retrieve memory usage percentage
def get_memory_usage():
    try:
        return psutil.virtual_memory().percent
    except Exception as e:
        logger.error(f"Could not retrieve Memory usage: {e}")
        return None

# Retrieve disk usage for the specified path
def get_disk_usage(path='/'):
    try:
        return psutil.disk_usage(path).percent
    except FileNotFoundError:
        logger.error(f"Disk path '{path}' not found.")
        return None
    except Exception as e:
        logger.error(f"Could not retrieve Disk usage for '{path}': {e}")
        return None

# Retrieve temperature from the first available sensor
def get_temperature():
    try:
        temps = psutil.sensors_temperatures()
        if not temps:
            return None
        for entries in temps.values():
            for entry in entries:
                if hasattr(entry, 'current') and entry.current is not None:
                    return entry.current
        return None
    except Exception as e:
        logger.error(f"Could not retrieve temperature: {e}")
        return None

# Export current metrics to JSON for external use
def export_metrics_to_json(cpu, mem, disk, path, net_in, net_out, temp):
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu_percent": cpu,
        "memory_percent": mem,
        "disk_percent": disk,
        "disk_path": path,
        "network_bytes_sent": net_out,
        "network_bytes_recv": net_in,
        "temperature_celsius": temp
    }
    try:
        with open("system_metrics.json", "a") as f:
            f.write(json.dumps(metrics) + "\n")
    except Exception as e:
        logger.error(f"Failed to export metrics to JSON: {e}")

# Get total network input/output in bytes
def get_network_io():
    try:
        net_io = psutil.net_io_counters()
        return net_io.bytes_recv, net_io.bytes_sent
    except Exception as e:
        logger.error(f"Could not retrieve Network I/O: {e}")
        return None, None

# Main monitoring loop for system metrics
def monitor_system(cpu_threshold, mem_threshold, disk_threshold, disk_path, interval, log_to_json, alert_temp):
    logger.info("System monitor started")
    logger.info(f"Config - Interval: {interval}s, CPU>{cpu_threshold}%, Mem>{mem_threshold}%, Disk>{disk_threshold}% at '{disk_path}'")
    logger.info("-" * 50)

    try:
        while True:
            # Gather metrics
            cpu_usage = get_cpu_usage()
            mem_usage = get_memory_usage()
            disk_usage = get_disk_usage(disk_path)
            net_in, net_out = get_network_io()
            temperature = get_temperature()

            # Format output for logging
            cpu_display = f"{cpu_usage:.1f}%" if cpu_usage is not None else "Error"
            mem_display = f"{mem_usage:.1f}%" if mem_usage is not None else "Error"
            disk_display = f"{disk_usage:.1f}%" if disk_usage is not None else "Error"
            net_display = f"Net In: {net_in} B | Net Out: {net_out} B" if None not in (net_in, net_out) else "Network: Error"
            temp_display = f"Temp: {temperature:.1f}°C" if temperature is not None else "Temp: Error"

            logger.info(f"CPU: {cpu_display} | Memory: {mem_display} | Disk ({disk_path}): {disk_display} | {net_display} | {temp_display}")

            # Optionally export to JSON
            if log_to_json:
                export_metrics_to_json(cpu_usage, mem_usage, disk_usage, disk_path, net_in, net_out, temperature)

            # Trigger alerts for thresholds
            if cpu_usage is not None and cpu_usage > cpu_threshold:
                msg = f"High CPU Usage: {cpu_usage:.1f}% (Threshold: {cpu_threshold}%)"
                logger.warning(msg)
                send_email_alert("CPU Alert", msg)
            if mem_usage is not None and mem_usage > mem_threshold:
                msg = f"High Memory Usage: {mem_usage:.1f}% (Threshold: {mem_threshold}%)"
                logger.warning(msg)
                send_email_alert("Memory Alert", msg)
            if disk_usage is not None and disk_usage > disk_threshold:
                msg = f"High Disk Usage ({disk_path}): {disk_usage:.1f}% (Threshold: {disk_threshold}%)"
                logger.warning(msg)
                send_email_alert("Disk Alert", msg)
            if alert_temp is not None and temperature is not None and temperature > alert_temp:
                msg = f"High Temperature: {temperature:.1f}°C (Threshold: {alert_temp}°C)"
                logger.warning(msg)
                send_email_alert("Temperature Alert", msg)

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("Monitoring interrupted by user.")
    except Exception as e:
        logger.critical(f"Critical error during monitoring: {e}")

# Parse arguments from command line
def parse_args():
    parser = argparse.ArgumentParser(description="Enhanced System Resource Monitor")
    parser.add_argument('--cpu', type=float, default=85.0, help='CPU usage warning threshold (default: 85.0)')
    parser.add_argument('--mem', type=float, default=85.0, help='Memory usage warning threshold (default: 85.0)')
    parser.add_argument('--disk', type=float, default=90.0, help='Disk usage warning threshold (default: 90.0)')
    parser.add_argument('--path', type=str, default='/', help="Disk path to monitor")
    parser.add_argument('--interval', type=int, default=5, help='Monitoring interval in seconds (default: 5)')
    parser.add_argument('--log-json', action='store_true', help='Log metrics to JSON file')
    parser.add_argument('--temp-threshold', type=float, help='Temperature warning threshold in Celsius')
    return parser.parse_args()

# Entry point for script execution
if __name__ == "__main__":
    args = parse_args()

    if platform.system() == "Windows" and args.path == '/':
        args.path = 'C:\\'
        logger.info("Windows platform detected. Adjusted disk path to C:\\")

    monitor_system(args.cpu, args.mem, args.disk, args.path, args.interval, args.log_json, args.temp_threshold)
