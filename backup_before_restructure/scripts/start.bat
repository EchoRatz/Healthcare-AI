@echo off
chcp 65001 >nul
title AI Query System

echo.
echo ████████████████████████████████████████████████████████
echo █                                                      █
echo █         🤖 AI Query System - Clean Version           █
echo █                                                      █
echo ████████████████████████████████████████████████████████
echo.

cd /d "%~dp0"

echo 🚀 เลือกโปรแกรมที่ต้องการใช้งาน:
echo.
echo    [1] 🤖 AI System        - ระบบตอบคำถามหลัก
echo    [2] 📁 Data Manager     - จัดการข้อมูล
echo    [3] 🌐 MCP Server       - เซิร์ฟเวอร์ MCP  
echo    [4] 📡 MCP Client       - ไคลเอนต์ MCP
echo    [5] 🧪 Run Tests        - ทดสอบระบบ
echo    [6] 📖 View Docs        - ดูเอกสาร
echo    [7] ❌ Exit             - ออกจากโปรแกรม
echo.

set /p choice="👉 เลือก (1-7): "
echo.

if "%choice%"=="1" (
    echo 🤖 เริ่มใช้งาน AI System...
    python ai_system.py
) else if "%choice%"=="2" (
    echo 📁 เริ่มใช้งาน Data Manager...
    python data_manager.py
) else if "%choice%"=="3" (
    echo 🌐 เริ่ม MCP Server...
    echo ⚠️  เปิด terminal อีกหน้าต่างแล้ว run: start.bat แล้วเลือก 4
    python mcp_server.py
) else if "%choice%"=="4" (
    echo 📡 เริ่ม MCP Client...
    echo ⚠️  ตรวจสอบให้แน่ใจว่า MCP Server ทำงานอยู่
    python mcp_client.py
) else if "%choice%"=="5" (
    echo 🧪 ทดสอบระบบ...
    python ai_system.py
    echo ✅ การทดสอบเสร็จสิ้น
) else if "%choice%"=="6" (
    echo 📖 เปิดเอกสาร...
    start README.md
) else if "%choice%"=="7" (
    echo 👋 ขอบคุณที่ใช้งาน!
    exit /b 0
) else (
    echo ❌ กรุณาเลือก 1-7
    pause
    goto :EOF
)

echo.
echo ========================================================
echo 🎉 การทำงานเสร็จสิ้น - กด Enter เพื่อปิด
echo ========================================================
pause >nul
