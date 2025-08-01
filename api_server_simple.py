from flask import Flask, request, jsonify
import os
import re
from typing import Dict, List, Tuple

app = Flask(__name__)

def parse_question(question_text: str) -> Tuple[str, Dict[str, str]]:
    """Parse question and extract choices"""
    parts = question_text.split("ก.")
    if len(parts) < 2:
        return question_text, {}
    
    question = parts[0].strip()
    choices_text = "ก." + parts[1]
    
    # Extract choices ก, ข, ค, ง
    choice_pattern = re.compile(r"([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)")
    choices = {}
    
    for match in choice_pattern.finditer(choices_text):
        choice_letter = match.group(1)
        choice_text = match.group(2).strip()
        choices[choice_letter] = choice_text
    
    return question, choices

def mock_llama_response(question: str, choices: Dict[str, str]) -> Tuple[List[str], float]:
    """Mock response for testing without Ollama"""
    # Simple logic to return a mock answer
    if "เบาหวาน" in question and "ปัสสาวะ" in str(choices):
        return ["ก"], 0.85
    elif "เบาหวาน" in question and "ทุกข้อ" in str(choices):
        return ["ง"], 0.90
    else:
        return ["ก"], 0.75

@app.route("/eval", methods=["POST"])
def evaluate_question():
    """
    Endpoint to evaluate a single question.
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
        parsed_question, choices = parse_question(question)
        if not parsed_question or not choices:
            return (
                jsonify({"error": "Failed to parse the question or extract choices."}),
                400,
            )

        # Mock query response
        answers, confidence = mock_llama_response(parsed_question, choices)

        # Construct reasoning
        reasoning = f"Based on the question analysis, the most appropriate answer is '{answers[0]}' with confidence {confidence:.2f}."

        return jsonify({
            "answer": answers[0] if answers else "No answer found", 
            "reason": reasoning, 
            "confidence": confidence,
            "choices": choices
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "OK"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001) 