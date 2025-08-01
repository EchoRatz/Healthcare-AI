from flask import Flask, request, jsonify
import os
import asyncio
import re
from improved_healthcare_qa_system import ImprovedHealthcareQA, AnswerValidation

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
        print("✅ Production Healthcare AI API initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        raise e

# Run initialization
asyncio.run(init_system())

app = Flask(__name__)

def parse_question_production(question_text: str):
    """Production-grade question parsing for Thai healthcare questions"""
    
    # Handle the format: "question text ก. choice1 ข. choice2 ค. choice3 ง. choice4"
    if "ก." in question_text:
        parts = question_text.split("ก.")
        if len(parts) >= 2:
            question = parts[0].strip()
            choices_text = "ก." + parts[1]
        else:
            return question_text, {}
    else:
        return question_text, {}
    
    # Extract choices ก, ข, ค, ง
    choices = {}
    choice_pattern = re.compile(r"([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)")
    
    for match in choice_pattern.finditer(choices_text):
        choice_letter = match.group(1)
        choice_text = match.group(2).strip()
        choices[choice_letter] = choice_text
    
    return question, choices

@app.route("/eval", methods=["POST"])
def evaluate_question():
    """
    Production API endpoint for healthcare question evaluation.
    
    Request Body:
    {
        "question": "ผมปวดท้องมาก อ้วกด้วย ไปแผนกไหนดี? ก. Endocrinology ข. Orthopedics ค. Emergency ง. Internal Medicine"
    }
    
    Response Body:
    {
        "answer": "ค",
        "reason": "หากมีอาการปวดท้องและอาเจียน ควรไปพบแพทย์ที่ แผนกอายุรกรรม (Internal Medicine) ดังนั้น จึงตอบข้อ ค."
    }
    """
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Invalid input. 'question' key is required."}), 400

    question = data["question"]
    if not isinstance(question, str):
        return jsonify({"error": "'question' must be a string."}), 400

    try:
        # Parse the question and extract choices
        parsed_question, choices = parse_question_production(question)
        
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
        
        # If LLM didn't return answers, try direct approach
        if not answers:
            # Create a production-ready prompt for reasoning
            reasoning_prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านการแพทย์ วิเคราะห์คำถามและให้คำแนะนำพร้อมเหตุผล

คำถาม: {parsed_question}

ตัวเลือก:
"""
            for letter, text in choices.items():
                reasoning_prompt += f"{letter}. {text}\n"
            
            reasoning_prompt += f"""
ข้อมูลเพิ่มเติม: {context[:500]}...

คำแนะนำ: วิเคราะห์อาการและเลือกแผนกที่เหมาะสมที่สุด พร้อมให้เหตุผลในภาษาไทย
ตอบด้วยตัวอักษรเดียว: ก, ข, ค, หรือ ง

คำตอบ:"""
            
            # Direct LLM query for both answer and reasoning
            async def direct_query():
                try:
                    async with qa_system.session.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": qa_system.model_name,
                            "prompt": reasoning_prompt,
                            "stream": False,
                            "options": {"temperature": 0.1}
                        }
                    ) as response:
                        if response.status == 200:
                            result = await response.json()
                            answer_text = result.get("response", "").strip()
                            # Extract any ก-ง from the response
                            found_answers = re.findall(r'[ก-ง]', answer_text)
                            return found_answers[:1], 0.8, answer_text
                        return [], 0.0, ""
                except:
                    return [], 0.0, ""
            
            answers, confidence, llm_response = asyncio.run(direct_query())

        # Use AI agent's answer and generate reasoning
        if answers:
            answer = answers[0]
            choice_text = choices.get(answer, "")
            
            # Use the AI agent's response for reasoning, or generate based on context
            if 'llm_response' in locals() and llm_response:
                # Extract reasoning from LLM response
                reason = llm_response.strip()
                # Clean up the response to focus on reasoning
                if "คำตอบ:" in reason:
                    reason = reason.split("คำตอบ:")[0].strip()
            else:
                # Use the optimized system's validation for reasoning
                validation = qa_system.validate_answer_enhanced(parsed_question, choices, answers, context)
                reason = validation.reasoning if validation.reasoning else f"ตามการวิเคราะห์ของระบบ AI ควรเลือกข้อ {answer} ({choice_text})"
        else:
            answer = "ง"  # Default to "none of the above"
            reason = "ไม่พบคำตอบที่เหมาะสมจากตัวเลือกที่ให้มา"

        # Return the exact format specified
        return jsonify({
            "answer": answer,
            "reason": reason
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
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