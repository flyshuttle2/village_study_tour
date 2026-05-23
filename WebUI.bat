@echo off
chcp 65001 >nul
title 乡村文旅研学解决方案生成器
cd /d "%~dp0"
echo.
echo ========================================
echo    乡村文旅研学解决方案生成器
echo ========================================
echo.
echo 正在启动服务，请稍候...
echo.
python app.py
pause
