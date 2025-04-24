# System Resource Monitor

A lightweight, production-ready Python script for monitoring system resources such as CPU, memory, and disk usage. This tool provides real-time feedback through logs and is designed for both CLI and background execution in production environments.

## Features

- Monitors CPU, memory, and disk usage
- Configurable warning thresholds
- Cross-platform compatibility (Linux, macOS, Windows)
- Rotating file logging and console output
- Graceful error handling
- Command-line arguments for customization

## Requirements

- Python 3.6+
- psutil

Install dependencies:
```bash
pip install psutil
```

## Usage

Run the script with default settings:
```bash
python system_monitor_prod.py
```

Or customize thresholds and interval:
```bash
python system_monitor_prod.py --cpu 80 --mem 75 --disk 85 --interval 10 --path /
```

### Available Arguments

- `--cpu`: CPU usage warning threshold (default: 85.0)
- `--mem`: Memory usage warning threshold (default: 85.0)
- `--disk`: Disk usage warning threshold (default: 90.0)
- `--path`: Disk path to monitor (default: `/` on Linux/macOS, `C:\` on Windows)
- `--interval`: Time in seconds between checks (default: 1)

## Logging

Logs are saved to:
```
system_monitor.log
```

A rotating log handler ensures the log file does not grow indefinitely.

## Notes

- You may need to run this script with elevated permissions to access certain system metrics depending on your OS.
- For Windows systems, the default disk path is automatically adjusted if set to `/`.

## License

MIT License
