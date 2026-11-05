@echo off
title ScholarTrack - Scholarship & Fellowship Deadline Tracker
echo =====================================================================
echo   ScholarTrack Platform - Scholarship ^& Fellowship Deadline Tracker
echo   Integrated Full-Stack Web Application (CyberNaut SRS 2026)
echo =====================================================================
echo.
echo [1/3] Verifying Python package dependencies...
pip install -r requirements.txt
echo.
echo [2/3] Initializing SQLite database and bootstrapping defaults...
python seed_db.py
echo.
echo [3/3] Starting ScholarTrack Flask application server...
echo.
echo =====================================================================
echo   Web Application URL: http://127.0.0.1:5000
echo   Student Demo Login:  student@scholartrack.edu / Student@ScholarTrack2026!
echo   Admin Portal Login:  admin@scholartrack.edu / Admin@ScholarTrack2026!
echo   To run automated tests: python -m pytest
echo   To stop the server, press Ctrl+C in this terminal.
echo =====================================================================
echo.
python app.py
pause
