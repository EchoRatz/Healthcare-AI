#!/usr/bin/env python3
"""
📡 Simple MCP Client - Model Context Protocol Client
ไคลเอนต์ MCP ที่เรียบง่ายและเข้าใจง่าย

Author: Refactored Version
Date: 2025-07-31
"""
import asyncio
import json
import struct
from typing import Dict, Any, Optional, List


class MCPClient:
    """MCP Client ที่เรียบง่าย"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.connected = False
        self.request_id = 0
        self.server_info = {}
        self.capabilities = {}
    
    def next_id(self) -> int:
        """รับ ID ถัดไป"""
        self.request_id += 1
        return self.request_id
    
    async def connect(self) -> bool:
        """เชื่อมต่อกับเซิร์ฟเวอร์"""
        try:
            print(f"🔗 กำลังเชื่อมต่อ {self.host}:{self.port}...")
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            self.connected = True
            print("✅ เชื่อมต่อสำเร็จ!")
            
            # ส่ง initialize request
            await self.initialize()
            return True
        
        except Exception as e:
            print(f"❌ เชื่อมต่อไม่สำเร็จ: {e}")
            return False
    
    async def disconnect(self):
        """ตัดการเชื่อมต่อ"""
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        self.connected = False
        print("🔌 ตัดการเชื่อมต่อแล้ว")
    
    async def send_request(self, method: str, params: Dict = None) -> Dict:
        """ส่ง request และรอ response"""
        if not self.connected:
            raise RuntimeError("ไม่ได้เชื่อมต่อกับเซิร์ฟเวอร์")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.next_id(),
            "method": method,
            "params": params or {}
        }
        
        # ส่ง request
        await self.write_message(request)
        
        # รอ response
        response = await self.read_message()
        
        if response is None:
            raise RuntimeError("ไม่ได้รับ response จากเซิร์ฟเวอร์")
        
        if "error" in response:
            error = response["error"]
            raise RuntimeError(f"Server error: {error.get('message', 'Unknown error')}")
        
        return response.get("result", {})
    
    async def read_message(self) -> Optional[Dict]:
        """อ่าน message จาก stream"""
        try:
            # อ่าน length (4 bytes)
            length_data = await self.reader.read(4)
            if not length_data:
                return None
            
            length = struct.unpack('>I', length_data)[0]
            
            # อ่าน message
            message_data = await self.reader.read(length)
            if len(message_data) != length:
                return None
            
            # แปลง JSON
            message = json.loads(message_data.decode('utf-8'))
            return message
        
        except Exception as e:
            print(f"❌ Error reading message: {e}")
            return None
    
    async def write_message(self, message: Dict):
        """เขียน message ไปยัง stream"""
        try:
            # แปลงเป็น JSON
            message_json = json.dumps(message, ensure_ascii=False)
            message_bytes = message_json.encode('utf-8')
            
            # เขียน length และ message
            length = len(message_bytes)
            self.writer.write(struct.pack('>I', length))
            self.writer.write(message_bytes)
            await self.writer.drain()
        
        except Exception as e:
            print(f"❌ Error writing message: {e}")
    
    async def initialize(self) -> Dict:
        """เริ่มต้น MCP protocol"""
        print("🚀 กำลังเริ่มต้น MCP protocol...")
        
        init_params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "roots": {"listChanged": True}
            },
            "clientInfo": {
                "name": "simple-mcp-client",
                "version": "2.0.0"
            }
        }
        
        result = await self.send_request("initialize", init_params)
        
        self.server_info = result.get("serverInfo", {})
        self.capabilities = result.get("capabilities", {})
        
        print(f"✅ เชื่อมต่อกับ: {self.server_info.get('name', 'Unknown')} v{self.server_info.get('version', '0.0.0')}")
        
        return result
    
    async def list_tools(self) -> List[Dict]:
        """รายการ tools"""
        result = await self.send_request("tools/list")
        return result.get("tools", [])
    
    async def call_tool(self, name: str, arguments: Dict = None) -> Dict:
        """เรียกใช้ tool"""
        params = {
            "name": name,
            "arguments": arguments or {}
        }
        return await self.send_request("tools/call", params)
    
    async def list_resources(self) -> List[Dict]:
        """รายการ resources"""
        result = await self.send_request("resources/list")
        return result.get("resources", [])
    
    async def read_resource(self, uri: str) -> Dict:
        """อ่าน resource"""
        params = {"uri": uri}
        return await self.send_request("resources/read", params)
    
    async def list_prompts(self) -> List[Dict]:
        """รายการ prompts"""
        result = await self.send_request("prompts/list")
        return result.get("prompts", [])
    
    async def get_prompt(self, name: str, arguments: Dict = None) -> Dict:
        """ใช้ prompt"""
        params = {
            "name": name,
            "arguments": arguments or {}
        }
        return await self.send_request("prompts/get", params)


class MCPClientDemo:
    """Demo client สำหรับทดสอบ MCP Server"""
    
    def __init__(self, client: MCPClient):
        self.client = client
    
    async def run_demo(self):
        """รัน demo ทั้งหมด"""
        print("\n" + "="*60)
        print("🎯 MCP Client Demo - ทดสอบการทำงาน")
        print("="*60)
        
        try:
            # เชื่อมต่อ
            if not await self.client.connect():
                return
            
            # ทดสอบ tools
            await self.demo_tools()
            
            # ทดสอบ resources
            await self.demo_resources()
            
            # ทดสอบ prompts
            await self.demo_prompts()
            
        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาดใน demo: {e}")
        
        finally:
            await self.client.disconnect()
    
    async def demo_tools(self):
        """ทดสอบ tools"""
        print("\n🔧 ทดสอบ Tools:")
        print("-" * 40)
        
        # รายการ tools
        tools = await self.client.list_tools()
        print(f"📋 พบ {len(tools)} tools:")
        for tool in tools:
            print(f"  • {tool['name']}: {tool['description']}")
        
        print("\n🎯 ทดสอบการเรียกใช้ tools:")
        
        # ทดสอบ echo
        echo_result = await self.client.call_tool("echo", {"message": "สวัสดี MCP Server!"})
        self.print_tool_result("echo", echo_result)
        
        # ทดสอบ calculate
        calc_result = await self.client.call_tool("calculate", {
            "operation": "add",
            "a": 15,
            "b": 25
        })
        self.print_tool_result("calculate", calc_result)
        
        # ทดสอบ system_info
        sys_result = await self.client.call_tool("system_info")
        self.print_tool_result("system_info", sys_result)
    
    async def demo_resources(self):
        """ทดสอบ resources"""
        print("\n📄 ทดสอบ Resources:")
        print("-" * 40)
        
        # รายการ resources
        resources = await self.client.list_resources()
        print(f"📂 พบ {len(resources)} resources:")
        for resource in resources:
            print(f"  • {resource['name']}: {resource['description']}")
        
        print("\n📖 ทดสอบการอ่าน resources:")
        
        # อ่าน greeting
        greeting = await self.client.read_resource("memory://greeting")
        self.print_resource_content("greeting", greeting)
        
        # อ่าน status
        status = await self.client.read_resource("memory://status")
        self.print_resource_content("status", status)
    
    async def demo_prompts(self):
        """ทดสอบ prompts"""
        print("\n💡 ทดสอบ Prompts:")
        print("-" * 40)
        
        # รายการ prompts
        prompts = await self.client.list_prompts()
        print(f"💭 พบ {len(prompts)} prompts:")
        for prompt in prompts:
            print(f"  • {prompt['name']}: {prompt['description']}")
        
        print("\n🎪 ทดสอบการใช้ prompts:")
        
        # ใช้ introduce prompt
        intro_result = await self.client.get_prompt("introduce", {"name": "นักพัฒนา"})
        self.print_prompt_result("introduce", intro_result)
    
    def print_tool_result(self, tool_name: str, result: Dict):
        """แสดงผลลัพธ์ tool"""
        print(f"  ✅ {tool_name}:")
        content = result.get("content", [])
        for item in content:
            if item.get("type") == "text":
                print(f"     {item.get('text', '')}")
    
    def print_resource_content(self, resource_name: str, result: Dict):
        """แสดงเนื้อหา resource"""
        print(f"  📖 {resource_name}:")
        contents = result.get("contents", [])
        for content in contents:
            text = content.get("text", "")
            # แสดงเฉพาะ 200 ตัวอักษรแรก
            if len(text) > 200:
                text = text[:200] + "..."
            
            # แบ่งเป็นบรรทัด
            for line in text.split('\n'):
                if line.strip():
                    print(f"     {line}")
    
    def print_prompt_result(self, prompt_name: str, result: Dict):
        """แสดงผลลัพธ์ prompt"""
        print(f"  💡 {prompt_name}:")
        print(f"     คำอธิบาย: {result.get('description', '')}")
        
        messages = result.get("messages", [])
        for msg in messages:
            content = msg.get("content", {})
            if content.get("type") == "text":
                print(f"     ข้อความ: {content.get('text', '')}")


async def run_interactive_mode():
    """โหมดโต้ตอบ"""
    client = MCPClient()
    
    print("\n" + "="*60)
    print("🎮 MCP Client - Interactive Mode")
    print("="*60)
    
    if not await client.connect():
        return
    
    print("\nคำสั่งที่ใช้ได้:")
    print("  tools           - รายการ tools")
    print("  call <name>     - เรียกใช้ tool")
    print("  resources       - รายการ resources")
    print("  read <uri>      - อ่าน resource")
    print("  prompts         - รายการ prompts")
    print("  prompt <name>   - ใช้ prompt")
    print("  quit            - ออก")
    print("-" * 60)
    
    try:
        while True:
            command = input("\n💻 Command: ").strip().lower()
            
            if not command:
                continue
            
            if command == "quit" or command == "q":
                break
            
            try:
                if command == "tools":
                    tools = await client.list_tools()
                    print(f"\n🔧 Tools ({len(tools)}):")
                    for tool in tools:
                        print(f"  • {tool['name']}: {tool['description']}")
                
                elif command.startswith("call "):
                    tool_name = command[5:].strip()
                    if tool_name == "echo":
                        msg = input("  ข้อความ: ")
                        result = await client.call_tool("echo", {"message": msg})
                    elif tool_name == "calculate":
                        print("  การคำนวณ (add/subtract/multiply/divide):")
                        op = input("  operation: ")
                        a = float(input("  a: "))
                        b = float(input("  b: "))
                        result = await client.call_tool("calculate", {"operation": op, "a": a, "b": b})
                    elif tool_name == "system_info":
                        result = await client.call_tool("system_info")
                    else:
                        print(f"  ❌ ไม่รู้จัก tool: {tool_name}")
                        continue
                    
                    content = result.get("content", [])
                    for item in content:
                        if item.get("type") == "text":
                            print(f"  ✅ {item.get('text', '')}")
                
                elif command == "resources":
                    resources = await client.list_resources()
                    print(f"\n📄 Resources ({len(resources)}):")
                    for resource in resources:
                        print(f"  • {resource['uri']}: {resource['name']}")
                
                elif command.startswith("read "):
                    uri = command[5:].strip()
                    result = await client.read_resource(uri)
                    contents = result.get("contents", [])
                    for content in contents:
                        text = content.get("text", "")
                        print(f"  📖 {text}")
                
                elif command == "prompts":
                    prompts = await client.list_prompts()
                    print(f"\n💡 Prompts ({len(prompts)}):")
                    for prompt in prompts:
                        print(f"  • {prompt['name']}: {prompt['description']}")
                
                elif command.startswith("prompt "):
                    prompt_name = command[7:].strip()
                    if prompt_name == "introduce":
                        name = input("  ชื่อ: ")
                        result = await client.get_prompt("introduce", {"name": name})
                        print(f"  💭 {result.get('description', '')}")
                        messages = result.get("messages", [])
                        for msg in messages:
                            content = msg.get("content", {})
                            if content.get("type") == "text":
                                print(f"  💬 {content.get('text', '')}")
                    else:
                        print(f"  ❌ ไม่รู้จัก prompt: {prompt_name}")
                
                else:
                    print(f"  ❌ ไม่รู้จักคำสั่ง: {command}")
            
            except Exception as e:
                print(f"  ❌ เกิดข้อผิดพลาด: {e}")
    
    except KeyboardInterrupt:
        pass
    
    finally:
        await client.disconnect()
        print("\n👋 ขอบคุณที่ใช้งาน!")


async def main():
    """หน้าต่างหลัก"""
    print("📡 Simple MCP Client (Refactored)")
    print("Model Context Protocol Client ที่เรียบง่าย")
    
    print("\nเลือกโหมด:")
    print("1. Demo Mode (ทดสอบอัตโนมัติ)")
    print("2. Interactive Mode (โต้ตอบ)")
    print("3. Exit")
    
    while True:
        try:
            choice = input("\nเลือก (1-3): ").strip()
            
            if choice == '1':
                client = MCPClient()
                demo = MCPClientDemo(client)
                await demo.run_demo()
                break
            
            elif choice == '2':
                await run_interactive_mode()
                break
            
            elif choice == '3':
                print("👋 ขอบคุณที่ใช้งาน!")
                break
            
            else:
                print("❌ กรุณาเลือก 1-3")
        
        except KeyboardInterrupt:
            print("\n👋 ขอบคุณที่ใช้งาน!")
            break


if __name__ == "__main__":
    asyncio.run(main())
