@echo off
title Mental Health Chatbot Server
color 0A
echo ========================================
echo   Mental Health Chatbot Server
echo ========================================
echo.
echo Starting server...
echo.
echo The server will be available at:
echo   http://127.0.0.1:5000
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.
python start_server.py
if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start!
    echo Check the error messages above.
    pause
)

