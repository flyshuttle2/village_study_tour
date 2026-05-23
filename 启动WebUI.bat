@echo off
chcp 65001 >nul
title Village Study Tour Generator
cd /d "%~dp0"
echo.
echo ========================================
echo    Village Study Tour Generator
echo ========================================
echo.
echo Starting service...
echo.
python app.py
pause
