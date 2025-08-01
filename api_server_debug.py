from flask import Flask, request, jsonify
import os
import asyncio
import re
from improved_healthcare_qa_system import ImprovedHealthcareQA

# Initialize ImprovedHealthcareQA
qa_system = ImprovedHealthcareQA()

# Check Llama 3.1 availability and load documents
if not qa_system.check_llama31():
    raise RuntimeError("Llama 3.1 is not available. Ensure 'ollama serve' is running.")
qa_system.load_knowledge_base()  # Load the knowledge base

# Initialize async session
async def init_system():
    try:
        await qa_system.initialize()
        print("✅ Optimized LLM system initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        raise e

# Run initialization
asyncio.run(init_system())

app = Flask(__name__)

def debug_parse_question(question_text: str):
    """Debug the question parsing"""
    print(f"🔍 DEBUG: Parsing question: {question_text}")
    
    parts = question_text.split("ก.")
    print(f"🔍 DEBUG: Split parts: {parts}")
    
    if len(parts) < 2:
        print(f"🔍 DEBUG: Not enough parts, returning: {question_text}, {{}}")
        return question_text, {}
    
    question = parts[0].strip()
    choices_text = "ก." + parts[1]
    print(f"🔍 DEBUG: Question: {question}")
    print(f"🔍 DEBUG: Choices text: {choices_text}")
    
    # Extract choices ก, ข, ค, ง
    choice_pattern = re.compile(r"([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)")
    choices = {}
    
    for match in choice_pattern.finditer(choices_text):
        choice_letter = match.group(1)
        choice_text = match.group(2).strip()
        choices[choice_letter] = choice_text
        print(f"🔍 DEBUG: Found choice {choice_letter}: {choice_text}")
    
    print(f"🔍 DEBUG: Final choices: {choices}")
    return question, choices

@app.route("/eval", methods=["POST"])
def evaluate_question():
    """
    Debug endpoint to see what's happening at each step
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Invalid input. 'question' key is required."}), 400

    question = data["question"]
    if not isinstance(question, str):
        return jsonify({"error": "'question' must be a string."}), 400

    try:
        print(f"\n🚀 DEBUG: Starting evaluation for: {question}")
        
        # Parse the question and extract choices
        parsed_question, choices = debug_parse_question(question)
        print(f"🔍 DEBUG: Parsed question: {parsed_question}")
        print(f"🔍 DEBUG: Extracted choices: {choices}")
        
        if not parsed_question or not choices:
            return (
                jsonify({"error": "Failed to parse the question or extract choices."}),
                400,
            )

        # Get context for the question using optimized system
        analysis = qa_system.analyze_question(parsed_question)
        print(f"🔍 DEBUG: Question analysis: {analysis}")
        
        context = qa_system.search_context(analysis)
        print(f"🔍 DEBUG: Context length: {len(context)}")
        print(f"🔍 DEBUG: Context preview: {context[:200]}...")

        # Query the optimized LLM with context
        async def query_async():
            return await qa_system.query_llama31_enhanced(parsed_question, choices, context)
        
        answers, confidence = asyncio.run(query_async())
        print(f"🔍 DEBUG: LLM answers: {answers}")
        print(f"🔍 DEBUG: LLM confidence: {confidence}")

        # Validate the answer using the optimized system
        validation = qa_system.validate_answer_enhanced(parsed_question, choices, answers, context)
        print(f"🔍 DEBUG: Validation: {validation}")

        # Construct detailed reasoning
        reasoning = f"Based on the optimized LLM analysis: {validation.reasoning}"

        return jsonify({
            "answer": answers[0] if answers else "No answer found", 
            "reason": reasoning, 
            "confidence": confidence,
            "choices": choices,
            "validation": {
                "is_valid": validation.is_valid,
                "confidence": validation.confidence,
                "suggested_corrections": validation.suggested_corrections
            },
            "debug": {
                "parsed_question": parsed_question,
                "analysis_type": analysis.question_type,
                "analysis_keywords": analysis.keywords,
                "context_length": len(context),
                "llm_answers": answers,
                "llm_confidence": confidence
            }
        }), 200
    except Exception as e:
        print(f"❌ DEBUG: Error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "OK",
        "llm_available": qa_system.check_llama31(),
        "knowledge_base_loaded": len(qa_system.knowledge_base) > 0,
        "mcp_available": qa_system.mcp_available
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000) 