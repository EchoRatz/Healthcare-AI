#!/usr/bin/env python3
"""
🌐 Simple MCP Server - Model Context Protocol Server
เซิร์ฟเวอร์ MCP ที่เรียบง่ายและเข้าใจง่าย

Author: Refactored Version  
Date: 2025-07-31
"""
import asyncio
import json
import struct
import sys
import platform
from typing import Dict, Any, Optional
from datetime import datetime


class MCPServer:
    """MCP Server ที่เรียบง่าย"""
    
    def __init__(self, name: str = "simple-mcp-server", version: str = "2.0.0"):
        self.name = name
        self.version = version
        self.initialized = False
        
        # Tools ที่มีให้ใช้งาน
        self.tools = {
            "echo": {
                "name": "echo",
                "description": "ส่งข้อความกลับไป",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "ข้อความที่ต้องการ echo"}
                    },
                    "required": ["message"]
                }
            },
            "calculate": {
                "name": "calculate",
                "description": "คำนวณตัวเลข (บวก ลบ คูณ หาร)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["add", "subtract", "multiply", "divide"]},
                        "a": {"type": "number", "description": "ตัวเลขที่ 1"},
                        "b": {"type": "number", "description": "ตัวเลขที่ 2"}
                    },
                    "required": ["operation", "a", "b"]
                }
            },
            "system_info": {
                "name": "system_info", 
                "description": "ข้อมูลของระบบ",
                "inputSchema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
        
        # Resources ที่มีให้เข้าถึง
        self.resources = {
            "greeting": {
                "uri": "memory://greeting",
                "name": "คำทักทาย",
                "description": "ข้อความทักทายจาก MCP Server",
                "mimeType": "text/plain"
            },
            "server_status": {
                "uri": "memory://status", 
                "name": "สถานะเซิร์ฟเวอร์",
                "description": "ข้อมูลสถานะของเซิร์ฟเวอร์",
                "mimeType": "application/json"
            }
        }
        
        # Prompts ที่มีให้ใช้
        self.prompts = {
            "introduce": {
                "name": "introduce",
                "description": "แนะนำตัวเอง",
                "arguments": [
                    {"name": "name", "description": "ชื่อที่ต้องการแนะนำ", "required": True}
                ]
            }
        }
    
    def create_response(self, request_id: Optional[int], result: Any = None, error: Optional[Dict] = None) -> Dict:
        """สร้าง response message"""
        response = {
            "jsonrpc": "2.0",
            "id": request_id
        }
        
        if error:
            response["error"] = error
        else:
            response["result"] = result
        
        return response
    
    def create_error(self, code: int, message: str, data: Any = None) -> Dict:
        """สร้าง error object"""
        error = {"code": code, "message": message}
        if data:
            error["data"] = data
        return error
    
    async def handle_initialize(self, params: Dict) -> Dict:
        """จัดการ initialize request"""
        self.initialized = True
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True, "subscribe": True},
                "prompts": {"listChanged": True}
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    async def handle_tools_list(self, params: Dict) -> Dict:
        """รายการ tools"""
        return {"tools": list(self.tools.values())}
    
    async def handle_tools_call(self, params: Dict) -> Dict:
        """เรียกใช้ tool"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"ไม่มี tool ชื่อ: {tool_name}")
        
        if tool_name == "echo":
            message = arguments.get("message", "")
            return {
                "content": [{"type": "text", "text": f"📢 Echo: {message}"}]
            }
        
        elif tool_name == "calculate":
            operation = arguments.get("operation")
            a = arguments.get("a", 0)
            b = arguments.get("b", 0)
            
            try:
                if operation == "add":
                    result = a + b
                elif operation == "subtract":
                    result = a - b
                elif operation == "multiply":
                    result = a * b
                elif operation == "divide":
                    if b == 0:
                        raise ValueError("ไม่สามารถหารด้วยศูนย์ได้")
                    result = a / b
                else:
                    raise ValueError(f"ไม่รองรับการคำนวณ: {operation}")
                
                return {
                    "content": [{"type": "text", "text": f"🧮 {a} {operation} {b} = {result}"}]
                }
            except Exception as e:
                raise ValueError(f"ข้อผิดพลาดในการคำนวณ: {str(e)}")
        
        elif tool_name == "system_info":
            info = {
                "platform": platform.system(),
                "python_version": platform.python_version(),
                "timestamp": datetime.now().isoformat(),
                "server": f"{self.name} v{self.version}"
            }
            
            info_text = "\n".join([f"{k}: {v}" for k, v in info.items()])
            
            return {
                "content": [{"type": "text", "text": f"💻 ข้อมูลระบบ:\n{info_text}"}]
            }
        
        raise ValueError(f"ไม่รู้จัก tool: {tool_name}")
    
    async def handle_resources_list(self, params: Dict) -> Dict:
        """รายการ resources"""
        return {"resources": list(self.resources.values())}
    
    async def handle_resources_read(self, params: Dict) -> Dict:
        """อ่าน resource"""
        uri = params.get("uri")
        
        if uri == "memory://greeting":
            content = f"👋 สวัสดีจาก {self.name}!\n\nเซิร์ฟเวอร์นี้พร้อมให้บริการแล้ว\nเวลา: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return {
                "contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]
            }
        
        elif uri == "memory://status":
            status = {
                "server_name": self.name,
                "version": self.version,
                "initialized": self.initialized,
                "timestamp": datetime.now().isoformat(),
                "available_tools": len(self.tools),
                "available_resources": len(self.resources),
                "available_prompts": len(self.prompts)
            }
            
            return {
                "contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(status, indent=2)}]
            }
        
        raise ValueError(f"ไม่พบ resource: {uri}")
    
    async def handle_prompts_list(self, params: Dict) -> Dict:
        """รายการ prompts"""
        return {"prompts": list(self.prompts.values())}
    
    async def handle_prompts_get(self, params: Dict) -> Dict:
        """ใช้ prompt"""
        name = params.get("name")
        arguments = params.get("arguments", {})
        
        if name == "introduce":
            user_name = arguments.get("name", "ผู้ใช้")
            prompt_text = f"สวัสดี {user_name}! ฉันคือ {self.name} ฉันพร้อมช่วยเหลือคุณในการใช้งาน MCP Protocol"
            
            return {
                "description": f"แนะนำตัวให้กับ {user_name}",
                "messages": [
                    {"role": "user", "content": {"type": "text", "text": prompt_text}}
                ]
            }
        
        raise ValueError(f"ไม่รู้จัก prompt: {name}")
    
    async def handle_request(self, request: Dict) -> Dict:
        """จัดการ request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            elif method == "resources/list":
                result = await self.handle_resources_list(params)
            elif method == "resources/read":
                result = await self.handle_resources_read(params)
            elif method == "prompts/list":
                result = await self.handle_prompts_list(params)
            elif method == "prompts/get":
                result = await self.handle_prompts_get(params)
            else:
                raise ValueError(f"ไม่รองรับ method: {method}")
            
            return self.create_response(request_id, result)
        
        except Exception as e:
            error = self.create_error(-32603, f"Internal error: {str(e)}")
            return self.create_response(request_id, error=error)
    
    async def read_message(self, reader: asyncio.StreamReader) -> Optional[Dict]:
        """อ่าน message จาก stream"""
        try:
            # อ่าน length (4 bytes)
            length_data = await reader.read(4)
            if not length_data:
                return None
            
            length = struct.unpack('>I', length_data)[0]
            
            # อ่าน message
            message_data = await reader.read(length)
            if len(message_data) != length:
                return None
            
            # แปลง JSON
            message = json.loads(message_data.decode('utf-8'))
            return message
        
        except Exception as e:
            print(f"❌ Error reading message: {e}")
            return None
    
    async def write_message(self, writer: asyncio.StreamWriter, message: Dict):
        """เขียน message ไปยัง stream"""
        try:
            # แปลงเป็น JSON
            message_json = json.dumps(message, ensure_ascii=False)
            message_bytes = message_json.encode('utf-8')
            
            # เขียน length และ message
            length = len(message_bytes)
            writer.write(struct.pack('>I', length))
            writer.write(message_bytes)
            await writer.drain()
        
        except Exception as e:
            print(f"❌ Error writing message: {e}")
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """จัดการ client connection"""
        client_addr = writer.get_extra_info('peername')
        print(f"🔗 Client connected: {client_addr}")
        
        try:
            while True:
                message = await self.read_message(reader)
                if message is None:
                    break
                
                print(f"📨 Received: {message.get('method', 'unknown')} (id: {message.get('id')})")
                
                response = await self.handle_request(message)
                await self.write_message(writer, response)
                
                print(f"📤 Sent response for id: {response.get('id')}")
        
        except Exception as e:
            print(f"❌ Error handling client: {e}")
        
        finally:
            print(f"🔌 Client disconnected: {client_addr}")
            writer.close()
            await writer.wait_closed()
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """เริ่มเซิร์ฟเวอร์"""
        server = await asyncio.start_server(self.handle_client, host, port)
        addr = server.sockets[0].getsockname()
        
        print(f"🚀 {self.name} v{self.version} เริ่มทำงาน")
        print(f"🌐 ที่อยู่: {addr[0]}:{addr[1]}")
        print(f"🔧 Tools: {len(self.tools)}")
        print(f"📄 Resources: {len(self.resources)}")
        print(f"💡 Prompts: {len(self.prompts)}")
        print("=" * 50)
        print("กำลังรอการเชื่อมต่อ... (กด Ctrl+C เพื่อหยุด)")
        
        async with server:
            await server.serve_forever()


async def main():
    """หน้าต่างหลัก"""
    print("🌐 Simple MCP Server (Refactored)")
    print("Model Context Protocol Server ที่เรียบง่าย")
    
    server = MCPServer()
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\n\n👋 เซิร์ฟเวอร์หยุดทำงาน")
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")


if __name__ == "__main__":
    asyncio.run(main())
