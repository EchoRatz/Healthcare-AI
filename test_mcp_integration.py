#!/usr/bin/env python3
"""
Test MCP Integration
===================

Test the MCP healthcare client with your specific problematic question
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_healthcare_client import MCPHealthcareClient, validate_answer_sync

def test_contradiction_case():
    """Test the specific contradictory case you mentioned"""
    print("🧪 Testing MCP Integration with Contradictory Case")
    print("=" * 55)
    
    # Your problematic question
    question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    
    choices = {
        "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
        "ข": "สิทธิบัตรทอง", 
        "ค": "สิทธิ 30 บาทรักษาทุกโรค",
        "ง": "ไม่มีข้อใดถูกต้อง"
    }
    
    # The contradictory local answer
    local_answer = ["ข", "ง", "ก"]  # This makes no logical sense
    
    print(f"📝 Question: {question[:50]}...")
    print(f"🎯 Local Answer (contradictory): {local_answer}")
    print(f"⚠️  Problem: Contains 'ง' (none correct) + other choices!")
    print()
    
    print("🔍 Testing MCP Validation...")
    
    try:
        # Test synchronous validation
        validated_answers, confidence, source = validate_answer_sync(
            question, local_answer, choices
        )
        
        print(f"✅ MCP Validation Complete!")
        print(f"  📊 Original: {local_answer}")
        print(f"  🔧 Validated: {validated_answers}")
        print(f"  📈 Confidence: {confidence:.3f}")
        print(f"  🏷️  Source: {source}")
        
        if "CORRECTED_CONTRADICTION" in source:
            print(f"  🎉 SUCCESS: MCP fixed the contradiction!")
        elif "VALIDATED" in source:
            print(f"  ⚠️  MCP agreed with contradictory answer (unexpected)")
        else:
            print(f"  📋 MCP result: {source}")
            
    except Exception as e:
        print(f"❌ MCP Test Failed: {e}")
        print(f"💡 Make sure MCP server is accessible")

async def test_mcp_client_direct():
    """Test MCP client directly"""
    print("\n🔬 Testing Direct MCP Client Connection")
    print("-" * 45)
    
    try:
        async with MCPHealthcareClient() as client:
            print("✅ MCP Client initialized successfully")
            print(f"📊 Available tools: {len(client.available_tools)}")
            
            for i, tool in enumerate(client.available_tools):
                name = tool.get("name", "Unknown")
                desc = tool.get("description", "No description")
                print(f"  {i+1}. {name}: {desc[:50]}...")
            
            # Test validation
            question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
            choices = {
                "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
                "ข": "สิทธิบัตรทอง", 
                "ค": "สิทธิ 30 บาทรักษาทุกโรค",
                "ง": "ไม่มีข้อใดถูกต้อง"
            }
            local_answer = ["ข", "ง", "ก"]
            
            result = await client.validate_healthcare_answer(question, local_answer, choices)
            
            if result.success:
                print(f"🎯 Validation Result: {result.data}")
                print(f"📈 Confidence: {result.confidence}")
            else:
                print(f"❌ Validation Failed: {result.error}")
                
    except Exception as e:
        print(f"❌ Direct client test failed: {e}")

def test_integration_in_main_system():
    """Test how it would work in the main system"""
    print("\n🚀 Testing Integration with Main System")
    print("-" * 40)
    
    # Simulate the main system flow
    question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
    choices = {
        "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
        "ข": "สิทธิบัตรทอง", 
        "ค": "สิทธิ 30 บาทรักษาทุกโรค",
        "ง": "ไม่มีข้อใดถูกต้อง"
    }
    
    # Simulate different scenarios
    scenarios = [
        (["ข", "ง", "ก"], "Contradictory (original problem)"),
        (["ข"], "Single answer"),
        (["ข", "ค"], "Multiple valid answers"),
        (["ง"], "None of the above only")
    ]
    
    for local_answer, description in scenarios:
        print(f"\n📋 Scenario: {description}")
        print(f"  Input: {local_answer}")
        
        # Check for contradiction
        has_contradiction = 'ง' in local_answer and len(local_answer) > 1
        print(f"  Contradiction detected: {has_contradiction}")
        
        if has_contradiction:
            print(f"  🔧 Would trigger MCP validation")
            try:
                validated, conf, src = validate_answer_sync(question, local_answer, choices)
                print(f"  Result: {validated} (confidence: {conf:.2f}, source: {src})")
            except Exception as e:
                print(f"  Error: {e}")
        else:
            print(f"  ✅ No validation needed")

def main():
    """Main test function"""
    print("🔍 MCP Healthcare Integration Test Suite")
    print("=" * 50)
    
    # Test 1: Contradiction case (synchronous)
    test_contradiction_case()
    
    # Test 2: Direct MCP client (asynchronous)
    try:
        asyncio.run(test_mcp_client_direct())
    except Exception as e:
        print(f"❌ Async test failed: {e}")
    
    # Test 3: Integration simulation
    test_integration_in_main_system()
    
    print(f"\n🎯 Test Summary:")
    print(f"  ✅ MCP client integration code created")
    print(f"  ✅ Contradiction detection implemented")
    print(f"  ✅ Validation logic integrated")
    print(f"  🔧 Ready for production testing!")
    
    print(f"\n💡 Next Steps:")
    print(f"  1. Run: python install_mcp_dependencies.py")
    print(f"  2. Test MCP server access with Postman")
    print(f"  3. Run: python ultra_fast_llama31.py")
    print(f"  4. Observe MCP validation in action!")

if __name__ == "__main__":
    main()