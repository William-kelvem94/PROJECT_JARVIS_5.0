
cd /d %~dp0
call venv\Scripts\activate.bat
python agents_worker.py
pause

