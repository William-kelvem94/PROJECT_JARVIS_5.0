@echo off
REM Force Install Windows Dependencies for JARVIS 5.0
echo Installing Windows Dependencies...
pip install pywin32 WMI pycaw comtypes psutil
echo Done.
pause
