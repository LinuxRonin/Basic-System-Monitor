# System Monitor (Enhanced and Commented)

A cross-platform, Python-powered system monitoring tool that tracks CPU, memory, disk, network I/O, and system temperature (if supported). Designed for sysadmins, developers, and cybersecurity professionals who want full control over their system telemetry.

---

🔄 What's New

- Temperature monitoring now gracefully handles unsupported platforms.

- Added troubleshooting section for temperature-related errors.

- temp-threshold now clearly warns users if sensors aren't available.

- Improved inline comments for clarity and maintainability.

**To see original simplisitc code navigate to system_monitor_prod.py**

---

## ✅ Features

- Monitors CPU, Memory, Disk, and Network usage
- Optionally logs data to JSON for later analysis
- Rotating log files to prevent storage bloat
- Alerts via terminal and email (disabled by default)
- Custom threshold settings per metric
- Graceful handling of unsupported features (like temperature)

---

## 📦 Requirements

- Python 3.7+
- `psutil` (install with `pip install psutil`)

---

## 🚀 Usage

```bash
python system_monitor_enhanced_commented.py [OPTIONS]
```

### 🔧 Options

| Option             | Description                                  |
|--------------------|----------------------------------------------|
| `--cpu`            | CPU usage threshold (default: 85.0)          |
| `--mem`            | Memory usage threshold (default: 85.0)       |
| `--disk`           | Disk usage threshold (default: 90.0)         |
| `--path`           | Disk path to monitor (default: `/`)          |
| `--interval`       | Seconds between checks (default: 5)          |
| `--log-json`       | Enable JSON logging of metrics               |
| `--temp-threshold` | Set temp warning threshold (optional)        |

---

## 📄 Example

```bash
python system_monitor_enhanced_commented.py --cpu 80 --mem 70 --disk 85 --interval 10 --log-json --temp-threshold 75
```

---

## ⚠️ Troubleshooting: "Temp: Error"

This tool attempts to use `psutil.sensors_temperatures()` to retrieve temperature data.

### Common causes:
- Your system does not expose temperature sensors to Python.
- `psutil` can't access sensor data on your OS.
- You're on Windows/macOS where `sensors_temperatures()` returns `{}`.

### How to check:
```python
import psutil
print(psutil.sensors_temperatures())
```

### Solutions:
- If it prints `{}`, your hardware or OS doesn't support this.
- Avoid setting `--temp-threshold` in that case.
- You can safely ignore "Temp: Error" – the script will continue.
- If on Linux, try:
```bash
sudo apt install lm-sensors
sudo sensors-detect
sensors
```

---

## 🗃 Output Files

- `system_monitor.log` – Rotating text log file
- `system_metrics.json` – JSON logs (if `--log-json` is enabled)

---

## 🛡 License

MIT License

---

## 📧 Email Alerts (Optional)

To enable email alerts:
1. Set `EMAIL_ENABLED = True` in the script.
2. Configure the `ALERT_EMAIL` address.
3. Ensure `localhost` SMTP is configured or modify the script to use external SMTP.

---

For advanced deployments, you can integrate this with tools like Prometheus, Grafana, or Elastic Stack.
