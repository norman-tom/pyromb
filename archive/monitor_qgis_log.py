#!/usr/bin/env python3
"""
Monitor QGIS Build_URBS plugin debug log
"""

import time
import os

LOG_FILE = r"E:\GitHub\pyromb2025\qgis_debug.log"

def monitor_log():
    """Monitor the log file for new entries."""
    if not os.path.exists(LOG_FILE):
        print("Log file doesn't exist yet. Run the plugin in QGIS first.")
        return
    
    print(f"Monitoring: {LOG_FILE}")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    with open(LOG_FILE, 'r') as f:
        f.seek(0, 2)  # Go to end of file
        
        while True:
            try:
                line = f.readline()
                if line:
                    print(line.strip())
                else:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print("\nStopping log monitor")
                break

if __name__ == "__main__":
    monitor_log()
