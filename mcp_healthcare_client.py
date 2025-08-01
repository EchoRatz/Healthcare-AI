#!/usr/bin/env python3
"""
MCP Healthcare Client
====================

Integrates with CMKL MCP server for healthcare data validation
and cross-checking to improve answer accuracy and consistency.
"""

import json
import asyncio
import aiohttp
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger("mcp_healthcare_client")

@dataclass
class MCPResponse:
    """MCP server response"""
    success: bool
    data: Any = None
    error: str = None
    confidence: float = 0.0

class MCPHealthcareClient:
    """Client for CMKL MCP Healthcare Server"""
    
    def __init__(self, server_url: str = "https://mcp-hackathon.cmkl.ai"):
        self.server_url = server_url
        self.session = None
        self.initialized = False
        self.available_tools = []
        # Generate session ID upfront for CMKL MCP server
        import uuid
        self.session_id = str(uuid.uuid4())
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize MCP connection"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Initialize MCP session with proper protocol version
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "sessionId": self.session_id,  # Include session ID in init
                "params": {
                    "protocolVersion": "2025-06-18",
                    "clientInfo": {
                        "name": "healthcare-ai-client",
                        "version": "1.0.0"
                    },
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    }
                }
            }
            
            response = await self._send_request(init_request)
            if response.success:
                logger.info("MCP client initialized successfully")
                # Extract session ID from server response if available
                if response.data and "sessionId" in response.data:
                    self.session_id = response.data["sessionId"]
                
                await self._discover_tools()
                self.initialized = True
            else:
                logger.error(f"Failed to initialize MCP client: {response.error}")
                
        except Exception as e:
            logger.error(f"MCP initialization error: {e}")
    
    async def close(self):
        """Close MCP connection"""
        if self.session:
            await self.session.close()
    
    async def call_tool(self, tool_name: str, arguments: Dict) -> MCPResponse:
        """Call a tool on the MCP server"""
        if not self.initialized:
            return MCPResponse(success=False, error="MCP client not initialized")
            
        request = {
            "jsonrpc": "2.0",
            "id": f"tool-{tool_name}-{hash(str(arguments))}",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
                "sessionId": self.session_id  # Session ID in params
            }
        }
            
        return await self._send_request(request)
    
    async def _send_request(self, request: Dict) -> MCPResponse:
        """Send JSON-RPC request to MCP server"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            # Try different endpoints based on MCP server setup  
            endpoints = ["/mcp", "/message", "/api/mcp"]  # Start with /mcp first based on error logs
            
            for endpoint in endpoints:
                url = f"{self.server_url}{endpoint}"
                try:
                    async with self.session.post(url, json=request, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            content_type = response.headers.get('content-type', '')
                            
                            if 'text/event-stream' in content_type:
                                # Handle Server-Sent Events (SSE) response
                                text_data = await response.text()
                                logger.debug(f"SSE response: {text_data[:200]}...")
                                
                                # Parse SSE format - look for JSON in data: lines
                                lines = text_data.strip().split('\n')
                                for line in lines:
                                    if line.startswith('data: '):
                                        try:
                                            json_str = line[6:]  # Remove "data: " prefix
                                            if json_str.strip():
                                                data = json.loads(json_str)
                                                if "error" in data:
                                                    return MCPResponse(success=False, error=data["error"]["message"])
                                                return MCPResponse(success=True, data=data.get("result"))
                                        except json.JSONDecodeError:
                                            continue
                                            
                                return MCPResponse(success=False, error="No valid JSON found in SSE stream")
                            else:
                                # Handle regular JSON response
                                data = await response.json()
                                if "error" in data:
                                    return MCPResponse(success=False, error=data["error"]["message"])
                                return MCPResponse(success=True, data=data.get("result"))
                        elif response.status == 404:
                            continue  # Try next endpoint
                        else:
                            error_text = await response.text()
                            logger.debug(f"Endpoint {endpoint} failed: HTTP {response.status}: {error_text}")
                            return MCPResponse(success=False, error=f"HTTP {response.status}: {error_text}")
                except asyncio.TimeoutError:
                    logger.debug(f"Endpoint {endpoint} timed out")
                    continue
                except Exception as e:
                    logger.debug(f"Endpoint {endpoint} error: {e}")
                    continue
            
            return MCPResponse(success=False, error="No valid endpoint found")
            
        except Exception as e:
            return MCPResponse(success=False, error=str(e))
    
    async def _discover_tools(self):
        """Discover available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {
                "sessionId": self.session_id  # Try session ID in params
            }
        }
        
        response = await self._send_request(request)
        if response.success and response.data:
            self.available_tools = response.data.get("tools", [])
            logger.info(f"Discovered {len(self.available_tools)} tools")
            for tool in self.available_tools:
                logger.info(f"  - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        else:
            logger.warning("Could not discover tools")
    
    async def validate_healthcare_answer(self, question: str, local_answer: List[str], choices: Dict[str, str]) -> MCPResponse:
        """Validate healthcare answer using MCP server"""
        if not self.initialized:
            return MCPResponse(success=False, error="MCP client not initialized")
        
        # Try different healthcare validation approaches
        validation_methods = [
            self._validate_with_lookup_patient,
            self._validate_with_available_tools,
            self._validate_with_general_query
        ]
        
        for method in validation_methods:
            try:
                result = await method(question, local_answer, choices)
                if result.success:
                    return result
            except Exception as e:
                logger.warning(f"Validation method failed: {e}")
                continue
        
        return MCPResponse(success=False, error="No validation method succeeded")
    
    async def _validate_with_lookup_patient(self, question: str, local_answer: List[str], choices: Dict[str, str]) -> MCPResponse:
        """Validate using lookup_patient tool with healthcare question"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "lookup_patient",
                "arguments": {
                    "patient_id": f"healthcare_policy_question: {question[:100]}"  # Use question as context
                }
            }
        }
        
        response = await self._send_request(request)
        if response.success:
            return self._parse_validation_response(response.data, local_answer)
        
        return response
    
    async def _validate_with_available_tools(self, question: str, local_answer: List[str], choices: Dict[str, str]) -> MCPResponse:
        """Validate using any available tools from the discovered tools list"""
        if not self.available_tools:
            return MCPResponse(success=False, error="No tools available")
        
        # Try each available tool
        for i, tool in enumerate(self.available_tools):
            tool_name = tool.get("name", f"tool_{i}")
            
            # Adapt arguments based on tool schema
            if "patient" in tool_name.lower():
                arguments = {"patient_id": question[:50]}
            elif "lookup" in tool_name.lower():
                arguments = {"query": question}
            elif "search" in tool_name.lower():
                arguments = {"search_term": question}
            else:
                # Generic arguments
                arguments = {
                    "question": question,
                    "context": "Thai healthcare policy",
                    "choices": choices
                }
            
            request = {
                "jsonrpc": "2.0",
                "id": 4 + i,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            try:
                response = await self._send_request(request)
                if response.success:
                    return self._parse_validation_response(response.data, local_answer)
            except Exception as e:
                logger.warning(f"Tool {tool_name} failed: {e}")
                continue
        
        return MCPResponse(success=False, error="All available tools failed")
    
    async def _validate_with_general_query(self, question: str, local_answer: List[str], choices: Dict[str, str]) -> MCPResponse:
        """Validate using a general query format"""
        # Try different argument patterns that might work
        argument_patterns = [
            {"patient_id": question},
            {"query": question, "options": list(choices.values())},
            {"text": question, "choices": choices},
            {"question": question, "format": "multiple_choice"},
            {"healthcare_query": question, "answer_choices": choices}
        ]
        
        for i, arguments in enumerate(argument_patterns):
            request = {
                "jsonrpc": "2.0",
                "id": 10 + i,
                "method": "tools/call",
                "params": {
                    "name": "lookup_patient",  # Use the known tool name
                    "arguments": arguments
                }
            }
            
            try:
                response = await self._send_request(request)
                if response.success:
                    return self._parse_validation_response(response.data, local_answer)
            except Exception as e:
                logger.debug(f"Pattern {i} failed: {e}")
                continue
        
        return MCPResponse(success=False, error="All query patterns failed")
    
    def _parse_validation_response(self, mcp_data: Any, local_answer: List[str]) -> MCPResponse:
        """Parse MCP validation response"""
        try:
            # Try to extract answer from various possible response formats
            mcp_answer = None
            confidence = 0.8
            
            if isinstance(mcp_data, dict):
                # Look for common answer fields
                for field in ["answer", "result", "response", "choice", "selection"]:
                    if field in mcp_data:
                        mcp_answer = mcp_data[field]
                        break
                
                # Look for confidence
                if "confidence" in mcp_data:
                    confidence = float(mcp_data["confidence"])
            
            elif isinstance(mcp_data, str):
                # Parse string response for Thai choices
                import re
                choices_found = re.findall(r'[ก-ง]', mcp_data)
                if choices_found:
                    mcp_answer = choices_found
            
            if mcp_answer:
                # Normalize to list format
                if isinstance(mcp_answer, str):
                    if ',' in mcp_answer:
                        mcp_answer = [a.strip() for a in mcp_answer.split(',')]
                    else:
                        mcp_answer = [mcp_answer]
                
                # Filter valid Thai choices
                mcp_answer = [a for a in mcp_answer if a in ['ก', 'ข', 'ค', 'ง']]
                
                return MCPResponse(
                    success=True,
                    data={
                        "mcp_answer": mcp_answer,
                        "local_answer": local_answer,
                        "validation_result": self._compare_answers(local_answer, mcp_answer)
                    },
                    confidence=confidence
                )
            
            return MCPResponse(success=False, error="Could not parse MCP response")
            
        except Exception as e:
            return MCPResponse(success=False, error=f"Parse error: {e}")
    
    def _compare_answers(self, local: List[str], mcp: List[str]) -> Dict[str, Any]:
        """Compare local and MCP answers"""
        local_set = set(local)
        mcp_set = set(mcp)
        
        agreement = local_set == mcp_set
        overlap = len(local_set.intersection(mcp_set))
        
        # Check for logical contradictions
        contradiction = False
        if 'ง' in local_set and len(local_set) > 1:  # "ไม่มีข้อใดถูกต้อง" + others
            contradiction = True
        
        return {
            "agreement": agreement,
            "overlap": overlap,
            "total_local": len(local_set),
            "total_mcp": len(mcp_set),
            "contradiction_detected": contradiction,
            "recommended_answer": list(mcp_set) if mcp_set else local,
            "confidence_boost": 0.2 if agreement else -0.1
        }
    
    async def get_healthcare_context(self, question: str) -> MCPResponse:
        """Get additional healthcare context from MCP server"""
        if not self.initialized:
            return MCPResponse(success=False, error="MCP client not initialized")
        
        # Try to get resources
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "resources/list"
        }
        
        response = await self._send_request(request)
        if response.success and response.data:
            resources = response.data.get("resources", [])
            
            # Find relevant resources
            for resource in resources:
                uri = resource.get("uri", "")
                if any(keyword in uri.lower() for keyword in ["healthcare", "policy", "rights", "benefits"]):
                    # Read the resource
                    read_request = {
                        "jsonrpc": "2.0",
                        "id": 7,
                        "method": "resources/read",
                        "params": {"uri": uri}
                    }
                    
                    read_response = await self._send_request(read_request)
                    if read_response.success:
                        return MCPResponse(
                            success=True,
                            data=read_response.data,
                            confidence=0.7
                        )
        
        return MCPResponse(success=False, error="No relevant healthcare context found")

# Async wrapper functions for integration
async def validate_answer_with_mcp(question: str, local_answer: List[str], choices: Dict[str, str]) -> Tuple[List[str], float, str]:
    """Validate answer using MCP server - async wrapper"""
    try:
        async with MCPHealthcareClient() as mcp_client:
            result = await mcp_client.validate_healthcare_answer(question, local_answer, choices)
            
            if result.success and result.data:
                validation = result.data["validation_result"]
                
                if validation["agreement"]:
                    # MCP agrees with local answer
                    return local_answer, result.confidence + 0.1, "MCP_VALIDATED"
                elif validation["contradiction_detected"]:
                    # Fix contradiction
                    recommended = validation["recommended_answer"]
                    return recommended, 0.9, "MCP_CORRECTED_CONTRADICTION"
                else:
                    # Different answers, use MCP if confident
                    if result.confidence > 0.7:
                        return result.data["mcp_answer"], result.confidence, "MCP_OVERRIDE"
                    else:
                        return local_answer, result.confidence - 0.1, "MCP_UNCERTAIN"
            else:
                return local_answer, 0.5, f"MCP_ERROR: {result.error}"
                
    except Exception as e:
        logger.error(f"MCP validation failed: {e}")
        return local_answer, 0.4, f"MCP_EXCEPTION: {str(e)[:50]}"

def validate_answer_sync(question: str, local_answer: List[str], choices: Dict[str, str]) -> Tuple[List[str], float, str]:
    """Synchronous wrapper for MCP validation"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(validate_answer_with_mcp(question, local_answer, choices))
    except Exception as e:
        return local_answer, 0.4, f"SYNC_ERROR: {str(e)[:50]}"
    finally:
        loop.close()

if __name__ == "__main__":
    # Test the MCP client
    async def test_mcp_client():
        async with MCPHealthcareClient() as client:
            # Test question from your example
            test_question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
            test_choices = {
                "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
                "ข": "สิทธิบัตรทอง", 
                "ค": "สิทธิ 30 บาทรักษาทุกโรค",
                "ง": "ไม่มีข้อใดถูกต้อง"
            }
            test_local_answer = ["ข", "ง", "ก"]  # Contradictory answer
            
            result = await client.validate_healthcare_answer(test_question, test_local_answer, test_choices)
            print(f"Validation result: {result}")
    
    # Run test
    asyncio.run(test_mcp_client())