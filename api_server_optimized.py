from flask import Flask, request, jsonify
import os
import asyncio
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

@app.route("/eval", methods=["POST"])
def evaluate_question():
    """
    Endpoint to evaluate a single question using the optimized LLM.
    Expects a JSON payload with a 'question' key containing the input string.
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Invalid input. 'question' key is required."}), 400

    question = data["question"]
    if not isinstance(question, str):
        return jsonify({"error": "'question' must be a string."}), 400

    try:
        # Parse the question and extract choices
        parsed_question, choices = qa_system.parse_question(question)
        if not parsed_question or not choices:
            return (
                jsonify({"error": "Failed to parse the question or extract choices."}),
                400,
            )

        # Get context for the question using optimized system
        analysis = qa_system.analyze_question(parsed_question)
        context = qa_system.search_context(analysis)

        # Query the optimized LLM with context
        async def query_async():
            return await qa_system.query_llama31_enhanced(parsed_question, choices, context)
        
        answers, confidence = asyncio.run(query_async())

        # Validate the answer using the optimized system
        validation = qa_system.validate_answer_enhanced(parsed_question, choices, answers, context)

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
            }
        }), 200
    except Exception as e:
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