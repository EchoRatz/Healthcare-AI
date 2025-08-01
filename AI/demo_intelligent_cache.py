#!/usr/bin/env python3
"""
Demo script showcasing the intelligent knowledge caching system
This demonstrates how the Thai Healthcare Q&A system learns from questions
and uses that knowledge to answer new questions not in the original dataset.
"""

from thai_qa_processor import ThaiHealthcareQA
import time


def demo_knowledge_extraction():
    """Demonstrate how the system extracts and caches knowledge"""
    print("🧠 Thai Healthcare AI - Intelligent Knowledge Caching Demo")
    print("=" * 70)
    print("This demo shows how the AI learns from each Q&A and builds knowledge")
    print("=" * 70)

    # Initialize the system
    print("\n🚀 Initializing Thai Healthcare Q&A System...")
    qa_system = ThaiHealthcareQA()

    # Show initial cache stats
    print("\n📊 Initial Knowledge Cache:")
    qa_system.show_cache_stats()

    # Test questions that will teach the system new information
    learning_questions = [
        {
            "question": "การรักษาฟันด้วยการเคลือบฟลูออไรด์มีค่าใช้จ่ายเท่าไร? ก. 50 บาท ข. 100 บาท ค. 150 บาท ง. 200 บาท",
            "topic": "Dental fluoride treatment costs",
        },
        {
            "question": "สิทธิ UCEP ครอบคลุมอาการใดบ้าง? ก. ปวดหัวธรรมดา ข. เจ็บหน้าอกรุนแรง ค. ไข้หวัดธรรมดา ง. อุบัติเหตุร้ายแรง",
            "topic": "UCEP coverage symptoms",
        },
        {
            "question": "แผนกใดเปิดให้บริการ 24 ชั่วโมง? ก. ศัลยกรรมทั่วไป ข. ห้องฉุกเฉิน ค. โสต ศอ นาสิก ง. จักษุ",
            "topic": "24-hour hospital departments",
        },
    ]

    print("\n🎓 Teaching the AI with new questions...")
    print("-" * 50)

    for i, q_data in enumerate(learning_questions, 1):
        print(f"\n📚 Learning Question {i}: {q_data['topic']}")
        print(f"Q: {q_data['question'][:80]}...")

        # Answer the question (this will extract and cache knowledge)
        answer = qa_system.answer_question(q_data["question"])

        # Show shortened answer
        short_answer = answer[:100] + "..." if len(answer) > 100 else answer
        print(f"A: {short_answer}")

        time.sleep(1)  # Small delay to show progression

    # Show updated cache stats
    print("\n" + "=" * 50)
    print("📈 Knowledge Cache After Learning:")
    qa_system.show_cache_stats()

    # Export the learned knowledge
    print("\n💾 Exporting learned knowledge...")
    qa_system.export_cache_to_text("demo_learned_knowledge.txt")

    print("\n" + "=" * 50)
    print("🎯 Now testing with NEW questions that use cached knowledge...")
    print("-" * 50)

    # Test questions that should benefit from cached knowledge (mix of multiple choice and open-ended)
    test_questions = [
        {
            "question": "ฉันต้องการเคลือบฟลูออไรด์ ราคาประมาณเท่าไร?",
            "type": "Open-ended (Price inquiry)",
        },
        {
            "question": "อาการเจ็บหน้าอกรุนแรงเข้าข่าย UCEP หรือไม่?",
            "type": "Open-ended (UCEP coverage)",
        },
        {
            "question": "ถ้ามีอุบัติเหตุตอนกลางคืน ควรไปแผนกไหน?",
            "type": "Open-ended (Emergency department)",
        },
        {
            "question": "บริการเคลือบฟลูออไรด์ในระบบประกันสุขภาพมีค่าใช้จ่ายเท่าไร? ก. ฟรี ข. 50 บาท ค. 100 บาท ง. 150 บาท",
            "type": "Multiple choice (using cached price knowledge)",
        },
    ]

    print("\n🎓 Teaching the AI with new questions...")
    print("-" * 50)

    for i, q_data in enumerate(learning_questions, 1):
        print(f"\n📚 Learning Question {i}: {q_data['topic']}")
        print(f"Q: {q_data['question'][:80]}...")

        # Answer the question (this will extract and cache knowledge)
        answer = qa_system.answer_question(q_data["question"])

        # Show shortened answer
        short_answer = answer[:100] + "..." if len(answer) > 100 else answer
        print(f"A: {short_answer}")

    # Show updated cache stats
    print("\n" + "=" * 50)
    print("📈 Knowledge Cache After Learning:")
    qa_system.show_cache_stats()

    # Export the learned knowledge
    print("\n💾 Exporting learned knowledge...")
    qa_system.save_knowledge_cache()


def show_cache_details():
    """Show detailed cache information"""
    print("\n🔍 Detailed Cache Analysis")
    print("-" * 30)

    qa_system = ThaiHealthcareQA()

    facts = qa_system.knowledge_cache.get("facts", [])
    if not facts:
        print("No cached facts found.")
        return

    print(f"Total cached facts: {len(facts)}")
    print("\nCached Knowledge:")

    for i, fact in enumerate(facts, 1):
        print(f"\n{i}. {fact.get('type', 'Unknown Type')}")
        print(f"   Key: {fact.get('key', 'N/A')}")
        print(f"   Value: {fact.get('value', 'N/A')}")
        if fact.get("context"):
            print(f"   Context: {fact['context']}")
        print(f"   Source: {fact.get('source_question', 'Unknown')[:60]}...")


if __name__ == "__main__":
    try:
        demo_knowledge_extraction()

        # Optionally show detailed cache
        user_input = input(
            "\n🤔 Would you like to see detailed cache information? (y/n): "
        )
        if user_input.lower() in ["y", "yes"]:
            show_cache_details()

    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("Make sure Ollama is running and required models are installed")
