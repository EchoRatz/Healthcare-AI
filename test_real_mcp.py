#!/usr/bin/env python3
"""Test real MCP connection"""

import asyncio
import logging
from mcp_healthcare_client import MCPHealthcareClient

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async def test_real_mcp():
    print('Testing REAL MCP connection...')
    client = MCPHealthcareClient()
    try:
        await client.initialize()
        if client.initialized:
            print('SUCCESS: REAL MCP Connected!')
            print(f'Available tools: {len(client.available_tools)}')
            
            # Test a simple tool call
            result = await client.call_tool('lookup_patient', {'patient_id': '12345'})
            print(f'Test result success: {result.success}')
            if result.success:
                print('SUCCESS: REAL MCP IS WORKING!')
            else:
                print(f'Tool call failed: {result.error}')
        else:
            print('FAILED: REAL MCP connection failed')
        await client.close()
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    asyncio.run(test_real_mcp())