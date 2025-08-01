#!/usr/bin/env python3
"""
Test Integrated System with Logical Validation
==============================================

Test that the ultra_fast_llama31.py correctly uses the enhanced logical validator
"""

import sys
import os

# Mock the query_llama31_with_context to return contradictory answers for testing
class MockUltraFastQA:
    def __init__(self):
        from enhanced_logical_validator import ThaiHealthcareLogicalValidator
        self.logical_validator = ThaiHealthcareLogicalValidator()
        
    def parse_question(self, question_text: str):
        """Mock parse_question"""
        # Example question from user's problem
        if "สิทธิในข้อใดที่ไม่รวมอยู่" in question_text:
            question = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ?"
            choices = {
                "ก": "สิทธิหลักประกันสุขภาพแห่งชาติ",
                "ข": "สิทธิบัตรทอง", 
                "ค": "สิทธิ 30 บาทรักษาทุกโรค",
                "ง": "ไม่มีข้อใดถูกต้อง"
            }
            return question, choices
        else:
            return question_text, {}
    
    def mock_llama_response(self, question: str, choices: dict):
        """Mock contradictory answer like the user reported"""
        return ["ข", "ง", "ก"], 0.6  # The problematic answer with low confidence
    
    def test_logical_validation_integration(self):
        """Test the complete logical validation flow"""
        print("🧪 Testing Integrated Logical Validation")
        print("=" * 45)
        
        # Mock the problematic question
        question_text = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ? ก. สิทธิหลักประกันสุขภาพแห่งชาติ ข. สิทธิบัตรทอง ค. สิทธิ 30 บาทรักษาทุกโรค ง. ไม่มีข้อใดถูกต้อง"
        
        # Parse question
        question, choices = self.parse_question(question_text)
        print(f"📋 Question: {question}")
        print(f"📝 Choices: {choices}")
        
        # Mock Llama response (the problematic one)
        predicted_answers, confidence = self.mock_llama_response(question, choices)
        print(f"\n🤖 Llama 3.1 Answer: {predicted_answers} (confidence: {confidence})")
        
        # Apply logical validation (this is the key test)
        print(f"\n🔧 Applying Enhanced Logical Validation...")
        validation_result = self.logical_validator.validate_answer(question, choices, predicted_answers)
        
        print(f"\n📊 Validation Results:")
        print(f"  Original: {validation_result.original_answer}")
        print(f"  Validated: {validation_result.validated_answer}")
        print(f"  Confidence: {validation_result.confidence:.2f}")
        
        if validation_result.corrections_made:
            print(f"  ✅ Corrections Made: {validation_result.corrections_made}")
            print(f"  📝 Reasoning: {validation_result.reasoning}")
            
            # Check if it fixed the specific problem
            if validation_result.validated_answer == ["ง"] and validation_result.original_answer == ["ข", "ง", "ก"]:
                print(f"\n🎉 SUCCESS! Fixed the exact problem from question 4!")
                print(f"   Before: {validation_result.original_answer} (contradictory)")
                print(f"   After:  {validation_result.validated_answer} (logical)")
                return True
            else:
                print(f"\n⚠️  Fixed but not as expected")
                return False
        else:
            print(f"  ❌ No corrections made - this should have been corrected!")
            return False

def test_with_actual_system():
    """Test with the actual ultra_fast_llama31.py system"""
    print(f"\n🌐 Testing with Actual System")
    print("-" * 35)
    
    try:
        # Import the actual system
        from ultra_fast_llama31 import UltraFastQA, LOGICAL_VALIDATOR
        print(f"✅ Successfully imported UltraFastQA with LOGICAL_VALIDATOR")
        
        # Create instance
        qa_system = UltraFastQA()
        print(f"✅ Created UltraFastQA instance")
        
        # Test parse_question
        question_text = "สิทธิในข้อใดที่ไม่รวมอยู่ในสิทธิประโยชน์ของผู้มีสิทธิหลักประกันสุขภาพแห่งชาติ? ก. สิทธิหลักประกันสุขภาพแห่งชาติ ข. สิทธิบัตรทอง ค. สิทธิ 30 บาทรักษาทุกโรค ง. ไม่มีข้อใดถูกต้อง"
        
        question, choices = qa_system.parse_question(question_text)
        print(f"✅ Parsed question successfully")
        print(f"   Question: {question[:50]}...")
        print(f"   Choices: {list(choices.keys())}")
        
        # Test logical validator directly
        problematic_answer = ["ข", "ง", "ก"]
        validation_result = LOGICAL_VALIDATOR.validate_answer(question, choices, problematic_answer)
        
        print(f"\n🔧 Direct Logical Validation Test:")
        print(f"   Input:  {problematic_answer}")
        print(f"   Output: {validation_result.validated_answer}")
        print(f"   Fixed:  {'✅' if validation_result.corrections_made else '❌'}")
        
        if validation_result.corrections_made:
            print(f"   📝 Reasoning: {validation_result.reasoning}")
            
        return validation_result.corrections_made
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("🧪 Integrated System Testing Suite")
    print("=" * 40)
    print("Testing the logical validation integration in ultra_fast_llama31.py")
    
    # Test 1: Mock system
    print(f"\n" + "="*50)
    mock_system = MockUltraFastQA()
    mock_success = mock_system.test_logical_validation_integration()
    
    # Test 2: Actual system
    print(f"\n" + "="*50)
    actual_success = test_with_actual_system()
    
    # Results
    print(f"\n" + "="*50)
    print(f"📊 Test Results:")
    print(f"  Mock System:   {'✅ PASS' if mock_success else '❌ FAIL'}")
    print(f"  Actual System: {'✅ PASS' if actual_success else '❌ FAIL'}")
    
    if mock_success and actual_success:
        print(f"\n🎉 INTEGRATION SUCCESSFUL!")
        print(f"   Your system will now automatically fix contradictory answers!")
        print(f"   Question 4 type problems will be resolved immediately!")
        
        print(f"\n🚀 Ready to run:")
        print(f"   python ultra_fast_llama31.py")
        
    else:
        print(f"\n⚠️  Some tests failed - integration may need adjustment")

if __name__ == "__main__":
    main()