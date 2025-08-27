#!/usr/bin/env python3
"""
Setup QGIS error logging to development folder for debugging
"""

import os

PLUGIN_PATH = r"C:\Users\Lindsay\AppData\Roaming\QGIS\QGIS3\profiles\take2\python\plugins\build_urbs"
LOG_PATH = r"E:\GitHub\pyromb2025\qgis_debug.log"

def add_logging_to_plugin():
    """Add comprehensive logging to plugin files."""
    
    # Logging setup code to inject into plugin
    logging_code = f'''
import logging
import traceback
import sys

# Setup logging to development folder
logging.basicConfig(
    filename=r"{LOG_PATH}",
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a'
)
logger = logging.getLogger('build_urbs')

def log_exception(func_name, exception):
    """Log exception with full traceback."""
    logger.error(f"Exception in {{func_name}}: {{str(exception)}}")
    logger.error(f"Traceback: {{traceback.format_exc()}}")
    print(f"BUILD_URBS ERROR in {{func_name}}: {{str(exception)}}")
    print(f"Full traceback written to: {LOG_PATH}")
'''

    # Add to __init__.py
    init_file = os.path.join(PLUGIN_PATH, "__init__.py")
    if os.path.exists(init_file):
        with open(init_file, 'r') as f:
            content = f.read()
        
        if "Setup logging to development folder" not in content:
            # Insert logging setup at the top
            lines = content.split('\n')
            # Find first import or function
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ', 'def ', 'class ')):
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, logging_code)
            
            with open(init_file, 'w') as f:
                f.write('\n'.join(lines))
            
            print("✓ Added logging to __init__.py")

    # Add to build_urbs_algorithm.py
    algorithm_file = os.path.join(PLUGIN_PATH, "build_urbs_algorithm.py")
    if os.path.exists(algorithm_file):
        with open(algorithm_file, 'r') as f:
            content = f.read()
        
        # Add try/except around processAlgorithm
        if "try:" not in content or "log_exception" not in content:
            # Find processAlgorithm method
            lines = content.split('\n')
            new_lines = []
            in_process_algorithm = False
            indent_level = 0
            
            for line in lines:
                if "def processAlgorithm(" in line:
                    in_process_algorithm = True
                    indent_level = len(line) - len(line.lstrip())
                    new_lines.append(line)
                    new_lines.append(" " * (indent_level + 4) + "try:")
                    new_lines.append(" " * (indent_level + 8) + "logger.info('Starting URBS processAlgorithm')")
                elif in_process_algorithm and line.strip() and len(line) - len(line.lstrip()) <= indent_level and line.strip() != "":
                    # End of method
                    new_lines.append(" " * (indent_level + 4) + "except Exception as e:")
                    new_lines.append(" " * (indent_level + 8) + "log_exception('processAlgorithm', e)")
                    new_lines.append(" " * (indent_level + 8) + "raise")
                    new_lines.append(line)
                    in_process_algorithm = False
                elif in_process_algorithm:
                    # Inside method - add extra indentation
                    if line.strip():
                        new_lines.append(" " * 4 + line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            with open(algorithm_file, 'w') as f:
                f.write('\n'.join(new_lines))
            
            print("✓ Added logging to build_urbs_algorithm.py")

def create_debug_script():
    """Create a script to monitor the debug log."""
    debug_script = f'''#!/usr/bin/env python3
"""
Monitor QGIS Build_URBS plugin debug log
"""

import time
import os

LOG_FILE = r"{LOG_PATH}"

def monitor_log():
    """Monitor the log file for new entries."""
    if not os.path.exists(LOG_FILE):
        print("Log file doesn't exist yet. Run the plugin in QGIS first.")
        return
    
    print(f"Monitoring: {{LOG_FILE}}")
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
                print("\\nStopping log monitor")
                break

if __name__ == "__main__":
    monitor_log()
'''
    
    script_path = r"E:\GitHub\pyromb2025\monitor_qgis_log.py"
    with open(script_path, 'w') as f:
        f.write(debug_script)
    
    print(f"✓ Created log monitor script: {script_path}")

def clear_log():
    """Clear existing log file."""
    if os.path.exists(LOG_PATH):
        with open(LOG_PATH, 'w') as f:
            f.write("")
        print(f"✓ Cleared log file: {LOG_PATH}")

def main():
    """Setup logging for QGIS plugin debugging."""
    print("Setting up QGIS Plugin Logging")
    print("=" * 40)
    
    try:
        # Clear existing log
        clear_log()
        
        # Add logging to plugin
        add_logging_to_plugin()
        
        # Create debug monitor script
        create_debug_script()
        
        print(f"\\n✅ Logging setup complete!")
        print(f"\\nDebug log location: {LOG_PATH}")
        print("\\nNext steps:")
        print("1. Reload Build_URBS plugin in QGIS")
        print("2. Run monitor_qgis_log.py to watch errors in real-time")
        print("3. Test plugin - all errors will be logged")
        
        return True
        
    except Exception as e:
        print(f"\\n❌ Logging setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
