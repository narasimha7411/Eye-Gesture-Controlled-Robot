import os, sys, subprocess

# Path to your correct Python
PY = r"C:\Python312\python.exe"
THIS = os.path.join(os.path.dirname(__file__), "control_launcher.py")

# If we're not already using the right interpreter, relaunch
if sys.executable.lower() != PY.lower():
    subprocess.run([PY, THIS])
    sys.exit()
