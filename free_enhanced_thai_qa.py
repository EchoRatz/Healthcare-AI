"""
Free Enhanced Thai Healthcare Q&A System
=========================================

High-accuracy system using FREE alternatives to GPT-4:
1. Local LLMs via Ollama
2. Free API services (Gemini, Groq, Cohere)
3. Advanced embedding-only methods
4. Ensemble predictions for maximum accuracy
"""

import os
import json
import csv
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging
import requests
import time

# Enhanced AI libraries (fallback gracefully if not available)
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

# Fallback imports
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class FreeQAResult:
    """Result structure for free enhanced system"""
    id: int
    question: str
    choices: Dict[str, str]
    predicted_answers: List[str]
    confidence: float
    reasoning_chain: List[str]
    evidence: List[str]
    method_used: str

class FreeEnhancedThaiQA:
    """
    Free Enhanced Thai Healthcare Q&A System
    No paid APIs required!
    """
    
    def __init__(self, knowledge_files: List[str], use_local_llm: bool = True):
        """
        Initialize free enhanced system
        
        Args:
            knowledge_files: Healthcare document files
            use_local_llm: Whether to try local LLM (Ollama)
        """
        self.knowledge_files = knowledge_files
        self.use_local_llm = use_local_llm
        self.knowledge_base = {}
        
        # Initialize AI models
        self.embedding_model = None
        self.faiss_index = None
        self.tfidf_vectorizer = None
        self.local_llm_available = False
        self.free_api_available = False
        
        logger.info("Initializing Free Enhanced Thai Healthcare Q&A System...")
        self._load_knowledge_base()
        self._initialize_ai_models()
        self._check_llm_availability()
    
    def _load_knowledge_base(self):
        """Load healthcare documents"""
        logger.info("Loading knowledge base...")
        
        for file_path in self.knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    sentences = self._split_thai_sentences(content)
                    
                    self.knowledge_base[file_path] = {
                        'content': content,
                        'sentences': sentences
                    }
                logger.info(f"Loaded {file_path}: {len(sentences)} sentences")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
    
    def _split_thai_sentences(self, text: str) -> List[str]:
        """Split Thai text into sentences"""
        import re
        # Clean text
        text = re.sub(r'--- Page \d+ ---', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Split by periods and other punctuation
        sentences = []
        parts = re.split(r'[.!?]+', text)
        for part in parts:
            if part.strip() and len(part.strip()) > 20:
                sentences.append(part.strip())
        return sentences
    
    def _initialize_ai_models(self):
        """Initialize the best available AI models"""
        logger.info("Initializing AI models...")
        
        # Collect all sentences
        all_sentences = []
        for kb_data in self.knowledge_base.values():
            all_sentences.extend(kb_data['sentences'])
        
        # Method 1: Try Sentence Transformers (Best free option)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info("Loading free multilingual embedding model...")
                # Try multiple models in order of preference
                models_to_try = [
                    'intfloat/multilingual-e5-large',  # Best for Thai
                    'sentence-transformers/paraphrase-multilingual-mpnet-base-v2',  # Good backup
                    'intfloat/multilingual-e5-base'  # Smaller but still good
                ]
                
                for model_name in models_to_try:
                    try:
                        self.embedding_model = SentenceTransformer(model_name)
                        logger.info(f"Loaded embedding model: {model_name}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load {model_name}: {e}")
                        continue
                
                if self.embedding_model:
                    # Create embeddings
                    logger.info(f"Creating embeddings for {len(all_sentences)} sentences...")
                    embeddings = self.embedding_model.encode(all_sentences, show_progress_bar=True)
                    
                    # Initialize FAISS if available
                    if FAISS_AVAILABLE:
                        dimension = embeddings.shape[1]
                        self.faiss_index = faiss.IndexFlatIP(dimension)
                        # Normalize for cosine similarity
                        faiss.normalize_L2(embeddings)
                        self.faiss_index.add(embeddings.astype('float32'))
                        logger.info("FAISS index created successfully")
                    
                    self.sentences = all_sentences
                    self.embeddings = embeddings
                    logger.info("✅ Sentence Transformers initialized successfully")
                
            except Exception as e:
                logger.warning(f"Failed to initialize Sentence Transformers: {e}")
                self.embedding_model = None
        else:
            logger.info("Sentence Transformers not available, using TF-IDF")
        
        # Method 2: Fallback to enhanced TF-IDF
        if self.embedding_model is None:
            logger.info("Using enhanced TF-IDF as embedding alternative...")
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,  # Increased features
                ngram_range=(1, 4),  # More n-grams
                analyzer='char',     # Character-level for Thai
                min_df=2,           # Remove very rare terms
                max_df=0.95         # Remove very common terms
            )
            self.tfidf_vectors = self.tfidf_vectorizer.fit_transform(all_sentences)
            self.sentences = all_sentences
            logger.info("✅ Enhanced TF-IDF initialized")
    
    def _check_llm_availability(self):
        """Check what LLM options are available"""
        logger.info("Checking LLM availability...")
        
        # Check Ollama (local LLM)
        if self.use_local_llm:
            try:
                response = requests.get('http://localhost:11434/api/tags', timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    available_models = [m['name'] for m in models]
                    
                    # Prefer Llama 3.1 models
                    llama31_models = [m for m in available_models if 'llama3.1' in m.lower()]
                    if llama31_models:
                        self.local_llm_available = True
                        self.local_llm_model = llama31_models[0]
                        logger.info(f"✅ Llama 3.1 available: {self.local_llm_model}")
                    elif available_models:
                        self.local_llm_available = True
                        self.local_llm_model = available_models[0]
                        logger.info(f"✅ Ollama available with model: {self.local_llm_model}")
                    else:
                        logger.info("❌ Ollama running but no models installed")
                        logger.info("💡 Install: ollama pull llama3.1:8b")
                else:
                    logger.info("❌ Ollama not responding")
            except Exception:
                logger.info("❌ Ollama not available")
                logger.info("💡 Install Ollama: https://ollama.ai")
        
        # Check free API options
        self._check_free_apis()
    
    def _check_free_apis(self):
        """Check free API availability"""
        # Check for API keys in environment
        api_keys = {
            'gemini': os.getenv('GEMINI_API_KEY'),
            'groq': os.getenv('GROQ_API_KEY'), 
            'cohere': os.getenv('COHERE_API_KEY'),
            'huggingface': os.getenv('HF_API_KEY')
        }
        
        available_apis = [name for name, key in api_keys.items() if key]
        if available_apis:
            self.free_api_available = True
            self.available_apis = available_apis
            logger.info(f"✅ Free APIs available: {', '.join(available_apis)}")
        else:
            logger.info("❌ No free API keys configured")
    
    def parse_question(self, question_text: str) -> Tuple[str, Dict[str, str]]:
        """Parse Thai question with choices"""
        import re
        
        parts = question_text.split('ก.')
        if len(parts) < 2:
            return question_text, {}
        
        question = parts[0].strip()
        choices_text = 'ก.' + parts[1]
        
        # Extract choices
        choice_pattern = re.compile(r'([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)')
        choices = {}
        matches = choice_pattern.findall(choices_text)
        
        for choice_label, choice_text in matches:
            choices[choice_label] = choice_text.strip()
        
        return question, choices
    
    def _find_relevant_content(self, question: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find relevant content using best available method"""
        if self.embedding_model and FAISS_AVAILABLE and self.faiss_index:
            return self._find_with_embeddings(question, top_k)
        elif self.embedding_model:
            return self._find_with_embeddings_basic(question, top_k)
        else:
            return self._find_with_enhanced_tfidf(question, top_k)
    
    def _find_with_embeddings(self, question: str, top_k: int) -> List[Tuple[str, float]]:
        """Find using embeddings + FAISS"""
        question_embedding = self.embedding_model.encode([question])
        faiss.normalize_L2(question_embedding.astype('float32'))
        
        similarities, indices = self.faiss_index.search(question_embedding.astype('float32'), top_k)
        
        results = []
        for similarity, idx in zip(similarities[0], indices[0]):
            if similarity > 0.1:
                results.append((self.sentences[idx], float(similarity)))
        return results
    
    def _find_with_embeddings_basic(self, question: str, top_k: int) -> List[Tuple[str, float]]:
        """Find using embeddings without FAISS"""
        question_embedding = self.embedding_model.encode([question])
        similarities = cosine_similarity(question_embedding, self.embeddings)[0]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                results.append((self.sentences[idx], similarities[idx]))
        return results
    
    def _find_with_enhanced_tfidf(self, question: str, top_k: int) -> List[Tuple[str, float]]:
        """Enhanced TF-IDF search"""
        question_vector = self.tfidf_vectorizer.transform([question])
        similarities = cosine_similarity(question_vector, self.tfidf_vectors)[0]
        
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:
                results.append((self.sentences[idx], similarities[idx]))
        return results
    
    def _local_llm_reasoning(self, question: str, choices: Dict[str, str], evidence: List[str]) -> Tuple[List[str], float, List[str]]:
        """Use local LLM (Ollama) for reasoning"""
        if not self.local_llm_available:
            return [], 0.0, ["Local LLM not available"]
        
        try:
            evidence_text = "\n".join(evidence[:5])
            choices_text = "\n".join([f"{k}. {v}" for k, v in choices.items()])
            
            prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านสุขภาพไทยและระบบประกันสุขภาพแห่งชาติ

คำถาม: {question}

ตัวเลือก:
{choices_text}

หลักฐานจากเอกสารสุขภาพ:
{evidence_text}

วิเคราะห์:
1. ใช้หลักฐานจากเอกสารเป็นหลัก
2. พิจารณาระบบประกันสุขภาพไทย
3. เลือกคำตอบที่ถูกต้องที่สุด

ตอบในรูปแบบ: [ตัวอักษร] เหตุผลสั้นๆ

คำตอบ:"""

                            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': self.local_llm_model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.1,
                        'num_predict': 150,
                        'top_p': 0.9,
                        'repeat_penalty': 1.1
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()['response']
                # Parse answer from response
                import re
                answer_match = re.search(r'[ก-ง]', result)
                if answer_match:
                    answer = answer_match.group()
                    return [answer], 0.7, [f"Local LLM reasoning: {result}"]
            
        except Exception as e:
            logger.error(f"Local LLM error: {e}")
        
        return [], 0.0, ["Local LLM failed"]
    
    def _free_api_reasoning(self, question: str, choices: Dict[str, str], evidence: List[str]) -> Tuple[List[str], float, List[str]]:
        """Use free APIs for reasoning"""
        if not self.free_api_available:
            return [], 0.0, ["No free APIs available"]
        
        # Try Gemini first (good free tier)
        if 'gemini' in self.available_apis:
            return self._gemini_reasoning(question, choices, evidence)
        
        # Try Groq (very fast)
        if 'groq' in self.available_apis:
            return self._groq_reasoning(question, choices, evidence)
        
        return [], 0.0, ["Free API reasoning failed"]
    
    def _gemini_reasoning(self, question: str, choices: Dict[str, str], evidence: List[str]) -> Tuple[List[str], float, List[str]]:
        """Use Google Gemini API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
            
            model = genai.GenerativeModel('gemini-pro')
            
            evidence_text = "\n".join(evidence[:5])
            choices_text = "\n".join([f"{k}. {v}" for k, v in choices.items()])
            
            prompt = f"""Analyze this Thai healthcare question:

Question: {question}

Choices:
{choices_text}

Evidence:
{evidence_text}

Select the best answer(s) based on the evidence. Respond with just the letter(s) (ก, ข, ค, ง) and brief reasoning.

Answer:"""

            response = model.generate_content(prompt)
            result = response.text
            
            # Parse answer
            import re
            answers = re.findall(r'[ก-ง]', result)
            if answers:
                return answers[:2], 0.75, [f"Gemini reasoning: {result}"]
                
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
        
        return [], 0.0, ["Gemini API failed"]
    
    def _advanced_embedding_reasoning(self, question: str, choices: Dict[str, str], evidence: List[str]) -> Tuple[List[str], float, List[str]]:
        """Advanced reasoning using only embeddings (no LLM needed)"""
        if not self.embedding_model:
            return [], 0.0, ["Embeddings not available"]
        
        reasoning_chain = []
        reasoning_chain.append("Using advanced embedding analysis")
        
        # Score each choice against evidence
        choice_scores = {}
        choice_texts = [f"{question} {text}" for text in choices.values()]
        evidence_texts = evidence[:5]
        
        if evidence_texts:
            # Encode choices and evidence
            choice_embeddings = self.embedding_model.encode(choice_texts)
            evidence_embeddings = self.embedding_model.encode(evidence_texts)
            
            # Calculate semantic similarity
            similarities = cosine_similarity(choice_embeddings, evidence_embeddings)
            
            # Score each choice
            for i, (choice_label, choice_text) in enumerate(choices.items()):
                # Weighted average similarity with evidence
                choice_score = np.mean(similarities[i]) * 0.7  # Base semantic similarity
                
                # Bonus for keyword overlap
                question_words = set(question.lower().split())
                choice_words = set(choice_text.lower().split())
                evidence_words = set(" ".join(evidence_texts).lower().split())
                
                # Keyword alignment bonus
                choice_question_overlap = len(choice_words.intersection(question_words)) / len(choice_words) if choice_words else 0
                choice_evidence_overlap = len(choice_words.intersection(evidence_words)) / len(choice_words) if choice_words else 0
                
                keyword_bonus = (choice_question_overlap + choice_evidence_overlap) * 0.3
                
                final_score = choice_score + keyword_bonus
                choice_scores[choice_label] = final_score
                
                reasoning_chain.append(f"Choice {choice_label}: semantic={choice_score:.3f}, keywords={keyword_bonus:.3f}, total={final_score:.3f}")
        
        # Select best answers
        if choice_scores:
            max_score = max(choice_scores.values())
            threshold = max_score * 0.85  # 85% of max score
            
            selected_answers = [
                choice for choice, score in choice_scores.items() 
                if score >= threshold and score > 0.2
            ]
            
            if not selected_answers:
                selected_answers = [max(choice_scores.keys(), key=choice_scores.get)]
            
            confidence = min(max_score, 0.8)  # Cap confidence for embedding-only
            reasoning_chain.append(f"Selected: {selected_answers} with confidence {confidence:.3f}")
            
            return selected_answers, confidence, reasoning_chain
        
        return [], 0.1, ["No evidence found for embedding analysis"]
    
    def _ensemble_prediction(self, question: str, choices: Dict[str, str]) -> FreeQAResult:
        """Combine multiple free AI methods"""
        reasoning_chain = []
        all_evidence = []
        predictions = {}
        
        # Step 1: Find relevant evidence
        reasoning_chain.append("Step 1: Finding relevant evidence")
        evidence = self._find_relevant_content(question, top_k=12)
        
        if evidence:
            all_evidence = [ev[0] for ev in evidence[:6]]
            reasoning_chain.append(f"Found {len(evidence)} relevant pieces of evidence")
            
            # Method 1: Local LLM (if available)
            if self.local_llm_available:
                reasoning_chain.append("Method 1: Using local LLM reasoning")
                llm_answers, llm_conf, llm_reasoning = self._local_llm_reasoning(question, choices, all_evidence)
                if llm_answers:
                    predictions['local_llm'] = {'answers': llm_answers, 'confidence': llm_conf, 'weight': 0.4}
                    reasoning_chain.extend(llm_reasoning)
            
            # Method 2: Free API (if available)
            if self.free_api_available:
                reasoning_chain.append("Method 2: Using free API reasoning")
                api_answers, api_conf, api_reasoning = self._free_api_reasoning(question, choices, all_evidence)
                if api_answers:
                    predictions['free_api'] = {'answers': api_answers, 'confidence': api_conf, 'weight': 0.4}
                    reasoning_chain.extend(api_reasoning)
            
            # Method 3: Advanced embeddings (always available if embeddings work)
            reasoning_chain.append("Method 3: Using advanced embedding analysis")
            emb_answers, emb_conf, emb_reasoning = self._advanced_embedding_reasoning(question, choices, all_evidence)
            if emb_answers:
                weight = 0.6 if not predictions else 0.2  # Higher weight if it's the only method
                predictions['embeddings'] = {'answers': emb_answers, 'confidence': emb_conf, 'weight': weight}
                reasoning_chain.extend(emb_reasoning)
        
        # Ensemble: Combine predictions
        if predictions:
            reasoning_chain.append("Step 4: Combining predictions")
            final_scores = {}
            method_used = []
            
            for method, pred in predictions.items():
                method_used.append(method)
                weight = pred['weight']
                confidence = pred['confidence']
                
                for answer in pred['answers']:
                    score = confidence * weight
                    final_scores[answer] = final_scores.get(answer, 0) + score
            
            # Select final answers
            max_score = max(final_scores.values())
            threshold = max_score * 0.8
            
            final_answers = [
                answer for answer, score in final_scores.items() 
                if score >= threshold and score > 0.1
            ]
            
            if not final_answers:
                final_answers = [max(final_scores.keys(), key=final_scores.get)]
            
            final_confidence = min(max_score, 0.9)
            method_string = '+'.join(method_used)
            
            reasoning_chain.append(f"Final prediction: {final_answers} (confidence: {final_confidence:.3f})")
        
        else:
            # Fallback: Simple choice scoring
            reasoning_chain.append("Fallback: Using simple choice analysis")
            final_answers = ['ข']  # Default common answer
            final_confidence = 0.1
            method_string = 'fallback'
            all_evidence = []
        
        return FreeQAResult(
            id=0,
            question=question,
            choices=choices,
            predicted_answers=final_answers,
            confidence=final_confidence,
            reasoning_chain=reasoning_chain,
            evidence=all_evidence,
            method_used=method_string
        )
    
    def process_test_file(self, test_file: str, output_file: str = "free_enhanced_submission.csv") -> List[FreeQAResult]:
        """Process test file with free enhanced AI"""
        results = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                total = sum(1 for _ in open(test_file, encoding='utf-8')) - 1
                
                logger.info(f"Processing {total} questions with free enhanced AI...")
                
                f.seek(0)
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader, 1):
                    question_id = int(row['id'])
                    full_question = row['question']
                    
                    question, choices = self.parse_question(full_question)
                    
                    # Use ensemble prediction
                    result = self._ensemble_prediction(question, choices)
                    result.id = question_id
                    results.append(result)
                    
                    if i % 25 == 0:
                        logger.info(f"Processed {i}/{total} questions... (avg conf: {np.mean([r.confidence for r in results[-25:]]):.3f})")
        
        except Exception as e:
            logger.error(f"Error processing test file: {e}")
        
        # Save results
        self._save_submission(results, output_file)
        return results
    
    def _save_submission(self, results: List[FreeQAResult], output_file: str):
        """Save results in submission format"""
        # Main submission file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'answer'])
            
            for result in results:
                answer_str = ','.join(result.predicted_answers)
                writer.writerow([result.id, f'"{answer_str}"'])
        
        logger.info(f"Free enhanced submission saved to {output_file}")
        
        # Analysis file
        analysis_file = output_file.replace('.csv', '_analysis.json')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            analysis = []
            for result in results:
                analysis.append({
                    'id': result.id,
                    'question': result.question[:100],
                    'predicted_answers': result.predicted_answers,
                    'confidence': result.confidence,
                    'method_used': result.method_used,
                    'evidence_count': len(result.evidence),
                    'reasoning_steps': len(result.reasoning_chain)
                })
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Analysis saved to {analysis_file}")

def main():
    """Run free enhanced system"""
    print("🆓 Free Enhanced Thai Healthcare Q&A System")
    print("=" * 50)
    
    # Configuration
    knowledge_files = [
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
    
    # Initialize free enhanced system
    qa_system = FreeEnhancedThaiQA(knowledge_files, use_local_llm=True)
    
    # Show available capabilities
    print(f"\n🔧 Available AI Capabilities:")
    print(f"  📊 Embeddings: {'✅' if qa_system.embedding_model else '❌'}")
    print(f"  🚀 FAISS Search: {'✅' if qa_system.faiss_index else '❌'}")
    print(f"  🤖 Local LLM: {'✅' if qa_system.local_llm_available else '❌'}")
    print(f"  🌐 Free APIs: {'✅' if qa_system.free_api_available else '❌'}")
    
    # Process questions
    results = qa_system.process_test_file(test_file)
    
    # Summary
    print(f"\n📊 Free Enhanced Results:")
    print(f"Total questions: {len(results)}")
    print(f"Average confidence: {np.mean([r.confidence for r in results]):.3f}")
    
    # Method breakdown
    method_counts = {}
    for result in results:
        method_counts[result.method_used] = method_counts.get(result.method_used, 0) + 1
    
    print(f"Methods used:")
    for method, count in method_counts.items():
        print(f"  {method}: {count} ({count/len(results)*100:.1f}%)")
    
    print(f"\n✅ Free enhanced processing complete!")
    print(f"Check 'free_enhanced_submission.csv' for results")

if __name__ == "__main__":
    main()