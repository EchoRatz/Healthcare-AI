from flask import Flask, request, jsonify
import os
from ultra_fast_llama31 import UltraFastQA

app = Flask(__name__)

# Initialize UltraFastQA
qa_system = UltraFastQA()

# Check Llama 3.1 availability and load documents
if not qa_system.check_llama31():
    raise RuntimeError("Llama 3.1 is not available. Ensure 'ollama serve' is running.")
if not qa_system.load_documents_once():
    raise RuntimeError("Failed to load knowledge documents.")


@app.route("/process", methods=["POST"])
def process_questions():
    """
    Endpoint to process questions using UltraFastQA.
    Expects a JSON payload with a 'questions' key containing the input string.
    """
    data = request.get_json()
    if not data or "questions" not in data:
        return jsonify({"error": "Invalid input. 'questions' key is required."}), 400

    questions = data["questions"]
    if not isinstance(questions, str):
        return jsonify({"error": "'questions' must be a string."}), 400

    try:
        # Process the input string
        results = qa_system.process_ultra_fast_string(questions)
        return jsonify({"results": results}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
