@echo off
chcp 65001 >nul
echo ====================================================
echo 🤖 AI Query System - Refactored Version
echo ระบบ AI ที่ปรับปรุงใหม่ให้อ่านง่ายขึ้น
echo ====================================================
echo.

cd /d "%~dp0"

echo เลือกโปรแกรมที่ต้องการใช้งาน:
echo.
echo [1] 🤖 AI Query System (ระบบตอบคำถาม)
echo [2] 📁 Data Manager (จัดการข้อมูล)
echo [3] 🌐 MCP Server (เซิร์ฟเวอร์)
echo [4] 📡 MCP Client (ไคลเอนต์)
echo [5] 🧪 ทดสอบทั้งหมด
echo [6] ❌ ออก
echo.

set /p choice="เลือก (1-6): "
echo.

if "%choice%"=="1" (
    echo 🚀 เริ่ม AI Query System...
    echo.
    python ai_system.py
) else if "%choice%"=="2" (
    echo 📁 เริ่ม Data Manager...
    echo.
    python data_manager.py
) else if "%choice%"=="3" (
    echo 🌐 เริ่ม MCP Server...
    echo ⚠️  เปิด terminal อีกหน้าต่างหนึ่งแล้วรัน MCP Client
    echo.
    python mcp_server.py
) else if "%choice%"=="4" (
    echo 📡 เริ่ม MCP Client...
    echo ⚠️  ตรวจสอบให้แน่ใจว่า MCP Server ทำงานอยู่แล้ว
    echo.
    python mcp_client.py
) else if "%choice%"=="5" (
    echo 🧪 ทดสอบระบบทั้งหมด...
    echo.
    echo [1/3] ทดสอบ AI Query System...
    python -c "
import sys
sys.path.append('.')
from ai_system import AIQuerySystem, run_test_suite
import asyncio

async def test():
    await asyncio.to_thread(run_test_suite)

try:
    asyncio.run(test())
except:
    run_test_suite()
"
    echo.
    echo [2/3] ทดสอบ Data Manager...
    python -c "
from data_manager import DataImporter, TextProcessor
print('✅ Data Manager - โหลดสำเร็จ')
importer = DataImporter()
print(f'✅ รองรับไฟล์: {list(importer.get_supported_formats().keys())}')
processor = TextProcessor()
test_text = 'ทดสอบการทำงาน'
cleaned = processor.clean_text(test_text)
print(f'✅ ทดสอบ text processing: {cleaned}')
"
    echo.
    echo [3/3] ทดสอบ MCP Components...
    python -c "
try:
    import mcp_server
    import mcp_client
    print('✅ MCP Server/Client - โหลดสำเร็จ')
    
    server = mcp_server.MCPServer()
    print(f'✅ MCP Server: {len(server.tools)} tools, {len(server.resources)} resources')
    
    client = mcp_client.MCPClient()
    print('✅ MCP Client - พร้อมใช้งาน')
except Exception as e:
    print(f'❌ MCP Error: {e}')
"
    echo.
    echo 🎉 การทดสอบเสร็จสิ้น!
) else if "%choice%"=="6" (
    echo 👋 ขอบคุณที่ใช้งาน!
    exit /b
) else (
    echo ❌ เลือกไม่ถูกต้อง กรุณาเลือก 1-6
)

echo.
echo ====================================================
echo การทำงานเสร็จสิ้น
echo ====================================================
pause
