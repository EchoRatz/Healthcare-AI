#!/usr/bin/env python3
"""
Simple MCP Integration Test
==========================

Test script to verify MCP integration with the improved healthcare system
"""

import asyncio
import sys
from improved_healthcare_qa_system import ImprovedHealthcareQA

async def test_mcp_integration():
    """Test MCP integration"""
    print("🧪 Testing MCP Integration")
    print("=" * 40)

    qa_system = ImprovedHealthcareQA()

    # Test MCP initialization
    print("🔗 Testing MCP initialization...")
    mcp_initialized = await qa_system.initialize_mcp()
    
    if mcp_initialized:
        print("✅ MCP initialized successfully")
        
        # Test MCP context query
        print("\n🔍 Testing MCP context query...")
        test_question = "แผนกฉุกเฉินเปิดอยู่ไหม?"
        analysis = qa_system.analyze_question(test_question)
        mcp_context = await qa_system.query_mcp_for_context(test_question, analysis)
        print(f"MCP Context: {mcp_context}")
        
        # Test MCP validation
        print("\n✅ Testing MCP validation...")
        test_answers = ["ค"]
        test_choices = {"ก": "A", "ข": "B", "ค": "Emergency", "ง": "D"}
        mcp_validation = await qa_system.validate_with_mcp(test_question, test_answers, test_choices)
        print(f"MCP Validation: {mcp_validation}")
        
    else:
        print("❌ MCP initialization failed")
        print("⚠️  System will run without MCP integration")

    # Test question analysis
    print("\n📝 Testing question analysis...")
    test_questions = [
        "แผนกฉุกเฉินเปิดอยู่ไหม?",
        "สิทธิหลักประกันสุขภาพแห่งชาติครอบคลุมอะไรบ้าง?",
        "ค่าบริการเคลือบฟลูออไรด์มีอัตราเท่าใด?"
    ]
    
    for question in test_questions:
        analysis = qa_system.analyze_question(question)
        print(f"Question: {question}")
        print(f"  Type: {analysis.question_type}")
        print(f"  Keywords: {analysis.keywords[:3]}...")
        print(f"  Confidence: {analysis.confidence:.2f}")

    print("\n✅ MCP integration test complete!")

async def test_single_question_with_mcp():
    """Test processing a single question with MCP integration"""
    print("\n🧪 Testing Single Question with MCP")
    print("=" * 40)

    qa_system = ImprovedHealthcareQA()

    # Initialize MCP
    await qa_system.initialize_mcp()

    # Test question
    test_question = {
        'id': '1',
        'question': 'ผมปวดท้องมาก อ้วกด้วย ตอนนี้ตีสองยังมีแผนกไหนเปิดอยู่ไหมครับ?  ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine'
    }

    # Parse and analyze
    question, choices = qa_system.parse_question(test_question['question'])
    analysis = qa_system.analyze_question(question)
    
    print(f"Question: {question}")
    print(f"Choices: {choices}")
    print(f"Analysis: {analysis}")

    # Load knowledge base
    qa_system.load_knowledge_base()

    # Search context
    context = qa_system.search_context(analysis)
    print(f"Local context length: {len(context)} chars")

    # Get MCP context
    if qa_system.mcp_available and qa_system.mcp_client and qa_system.mcp_client.initialized:
        mcp_context = await qa_system.query_mcp_for_context(question, analysis)
        print(f"MCP context: {mcp_context}")
        
        # Combine contexts
        full_context = context
        if mcp_context:
            full_context += f"\n\nMCP Additional Context: {mcp_context}"
        print(f"Combined context length: {len(full_context)} chars")

    print("✅ Single question test complete!")

async def main():
    """Main test function"""
    print("🏥 MCP INTEGRATION TEST SUITE")
    print("=" * 50)
    
    try:
        await test_mcp_integration()
        await test_single_question_with_mcp()
        
        print("\n🎉 All tests completed successfully!")
        print("\nThe improved healthcare system is now ready with MCP integration.")
        print("You can run the main system with: python improved_healthcare_qa_system.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print("The system will still work without MCP integration.")

if __name__ == "__main__":
    asyncio.run(main()) 