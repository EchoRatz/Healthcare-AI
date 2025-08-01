"""
Enhanced Thai Healthcare Q&A System with Advanced AI
===================================================

Improved version using modern AI techniques for higher accuracy:
1. Sentence Transformers for better embeddings
2. OpenAI GPT-4 for reasoning (optional)
3. FAISS for efficient vector search
4. Ensemble methods for robust predictions
"""

import os
import json
import csv
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

# Advanced AI libraries
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

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Fallback to sklearn if advanced libraries not available
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EnhancedQAResult:
    """Enhanced result with multiple AI techniques"""
    id: int
    question: str
    choices: Dict[str, str]
    predicted_answers: List[str]
    confidence: float
    reasoning_chain: List[str]
    evidence: List[str]
    method_used: str  # 'embedding', 'llm', 'tfidf', 'ensemble'

class EnhancedThaiHealthcareQA:
    """
    Enhanced Thai Healthcare Q&A with multiple AI approaches
    """
    
    def __init__(self, knowledge_files: List[str], use_openai: bool = False, openai_api_key: str = None):
        """
        Initialize enhanced system
        
        Args:
            knowledge_files: Healthcare document files
            use_openai: Whether to use OpenAI GPT for reasoning
            openai_api_key: OpenAI API key if using GPT
        """
        self.knowledge_files = knowledge_files
        self.use_openai = use_openai and OPENAI_AVAILABLE
        self.knowledge_base = {}
        
        # Initialize AI models
        self.embedding_model = None
        self.faiss_index = None
        self.openai_client = None
        self.tfidf_vectorizer = None
        
        if self.use_openai and openai_api_key:
            self.openai_client = OpenAI(api_key=openai_api_key)
        
        logger.info("Initializing Enhanced Thai Healthcare Q&A System...")
        self._load_knowledge_base()
        self._initialize_ai_models()
    
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
        """Initialize AI models based on availability"""
        logger.info("Initializing AI models...")
        
        # Collect all sentences
        all_sentences = []
        for kb_data in self.knowledge_base.values():
            all_sentences.extend(kb_data['sentences'])
        
        # Method 1: Sentence Transformers (Best for Thai)
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info("Loading multilingual embedding model...")
                self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-large')
                
                # Create embeddings
                logger.info(f"Creating embeddings for {len(all_sentences)} sentences...")
                embeddings = self.embedding_model.encode(all_sentences, show_progress_bar=True)
                
                # Initialize FAISS if available
                if FAISS_AVAILABLE:
                    dimension = embeddings.shape[1]
                    self.faiss_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
                    # Normalize embeddings for cosine similarity
                    faiss.normalize_L2(embeddings)
                    self.faiss_index.add(embeddings.astype('float32'))
                    logger.info("FAISS index created successfully")
                
                self.sentences = all_sentences
                self.embeddings = embeddings
                logger.info("Sentence Transformers initialized successfully")
                
            except Exception as e:
                logger.warning(f"Failed to initialize Sentence Transformers: {e}")
                self.embedding_model = None
        
        # Method 2: Fallback to TF-IDF
        if self.embedding_model is None:
            logger.info("Using TF-IDF as fallback...")
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),
                analyzer='char'
            )
            self.tfidf_vectors = self.tfidf_vectorizer.fit_transform(all_sentences)
            self.sentences = all_sentences
    
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
    
    def _find_relevant_content_embedding(self, question: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Find relevant content using embeddings"""
        if not self.embedding_model:
            return []
        
        # Encode question
        question_embedding = self.embedding_model.encode([question])
        
        if FAISS_AVAILABLE and self.faiss_index:
            # Use FAISS for fast search
            faiss.normalize_L2(question_embedding.astype('float32'))
            similarities, indices = self.faiss_index.search(question_embedding.astype('float32'), top_k)
            
            results = []
            for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                if similarity > 0.1:  # Threshold
                    results.append((self.sentences[idx], float(similarity)))
            return results
        else:
            # Manual cosine similarity
            similarities = cosine_similarity(question_embedding, self.embeddings)[0]
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:
                    results.append((self.sentences[idx], similarities[idx]))
            return results
    
    def _find_relevant_content_tfidf(self, question: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Fallback TF-IDF method"""
        if not self.tfidf_vectorizer:
            return []
        
        question_vector = self.tfidf_vectorizer.transform([question])
        similarities = cosine_similarity(question_vector, self.tfidf_vectors)[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:
                results.append((self.sentences[idx], similarities[idx]))
        return results
    
    def _llm_reasoning(self, question: str, choices: Dict[str, str], evidence: List[str]) -> Tuple[List[str], float, List[str]]:
        """Use LLM for reasoning"""
        if not self.openai_client:
            return [], 0.0, ["LLM not available"]
        
        try:
            # Prepare context
            evidence_text = "\n".join(evidence[:5])  # Top 5 evidence
            choices_text = "\n".join([f"{k}. {v}" for k, v in choices.items()])
            
            prompt = f"""คุณเป็นผู้เชี่ยวชาญด้านสุขภาพไทย วิเคราะห์คำถามต่อไปนี้จากข้อมูลที่ให้มา:

คำถาม: {question}

ตัวเลือก:
{choices_text}

หลักฐานจากเอกสาร:
{evidence_text}

วิเคราะห์:
1. ใช้หลักฐานจากเอกสารเป็นหลัก
2. เลือกตัวเลือกที่ถูกต้องที่สุด (สามารถเลือกได้หลายข้อ)
3. อธิบายเหตุผล

ตอบในรูปแบบ JSON:
{{
    "answers": ["ก", "ข"],
    "confidence": 0.8,
    "reasoning": "เหตุผลการเลือก..."
}}"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("answers", []), result.get("confidence", 0.5), [result.get("reasoning", "")]
            
        except Exception as e:
            logger.error(f"LLM reasoning failed: {e}")
            return [], 0.0, [f"LLM error: {str(e)}"]
    
    def _ensemble_prediction(self, question: str, choices: Dict[str, str]) -> EnhancedQAResult:
        """Combine multiple AI methods for best accuracy"""
        reasoning_chain = []
        all_evidence = []
        method_scores = {}
        
        # Method 1: Embedding-based
        if self.embedding_model:
            reasoning_chain.append("Method 1: Using semantic embeddings")
            embedding_evidence = self._find_relevant_content_embedding(question, top_k=8)
            if embedding_evidence:
                all_evidence.extend([ev[0] for ev in embedding_evidence[:3]])
                embedding_prediction = self._score_choices_embedding(choices, embedding_evidence)
                method_scores['embedding'] = embedding_prediction
                reasoning_chain.append(f"Embedding prediction: {embedding_prediction}")
        
        # Method 2: LLM reasoning (if available)
        llm_prediction = {}
        if self.openai_client and all_evidence:
            reasoning_chain.append("Method 2: Using LLM reasoning")
            llm_answers, llm_conf, llm_reasoning = self._llm_reasoning(question, choices, all_evidence)
            if llm_answers:
                llm_prediction = {answer: llm_conf for answer in llm_answers}
                method_scores['llm'] = llm_prediction
                reasoning_chain.extend(llm_reasoning)
        
        # Method 3: TF-IDF fallback
        if not method_scores:
            reasoning_chain.append("Method 3: Using TF-IDF fallback")
            tfidf_evidence = self._find_relevant_content_tfidf(question, top_k=8)
            if tfidf_evidence:
                all_evidence.extend([ev[0] for ev in tfidf_evidence[:3]])
                tfidf_prediction = self._score_choices_tfidf(choices, tfidf_evidence)
                method_scores['tfidf'] = tfidf_prediction
        
        # Ensemble: Combine predictions
        final_scores = {}
        for method, predictions in method_scores.items():
            weight = {'embedding': 0.4, 'llm': 0.5, 'tfidf': 0.1}.get(method, 0.1)
            for choice, score in predictions.items():
                final_scores[choice] = final_scores.get(choice, 0) + score * weight
        
        # Select best answers
        if final_scores:
            max_score = max(final_scores.values())
            threshold = max_score * 0.8
            predicted_answers = [choice for choice, score in final_scores.items() if score >= threshold and score > 0.1]
            confidence = max_score
            method_used = 'ensemble'
        else:
            predicted_answers = ['ข']  # Default
            confidence = 0.1
            method_used = 'fallback'
        
        reasoning_chain.append(f"Final prediction: {predicted_answers} (confidence: {confidence:.3f})")
        
        return EnhancedQAResult(
            id=0,
            question=question,
            choices=choices,
            predicted_answers=predicted_answers,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            evidence=all_evidence[:5],
            method_used=method_used
        )
    
    def _score_choices_embedding(self, choices: Dict[str, str], evidence: List[Tuple[str, float]]) -> Dict[str, float]:
        """Score choices using embedding similarity"""
        if not self.embedding_model:
            return {}
        
        choice_scores = {}
        choice_texts = [f"{label}: {text}" for label, text in choices.items()]
        
        if evidence:
            choice_embeddings = self.embedding_model.encode(choice_texts)
            evidence_texts = [ev[0] for ev in evidence[:5]]
            evidence_embeddings = self.embedding_model.encode(evidence_texts)
            
            # Calculate similarities
            similarities = cosine_similarity(choice_embeddings, evidence_embeddings)
            
            for i, (choice_label, _) in enumerate(choices.items()):
                # Weight by evidence relevance scores
                weighted_score = 0
                for j, (_, evidence_score) in enumerate(evidence[:5]):
                    weighted_score += similarities[i][j] * evidence_score
                choice_scores[choice_label] = weighted_score / len(evidence)
        
        return choice_scores
    
    def _score_choices_tfidf(self, choices: Dict[str, str], evidence: List[Tuple[str, float]]) -> Dict[str, float]:
        """Score choices using TF-IDF similarity"""
        choice_scores = {}
        
        for choice_label, choice_text in choices.items():
            choice_chars = set(choice_text.lower())
            total_score = 0
            
            for evidence_text, evidence_score in evidence:
                evidence_chars = set(evidence_text.lower())
                if choice_chars:
                    intersection = choice_chars.intersection(evidence_chars)
                    char_match = len(intersection) / len(choice_chars)
                    total_score += char_match * evidence_score
            
            choice_scores[choice_label] = total_score / len(evidence) if evidence else 0
        
        return choice_scores
    
    def process_test_file(self, test_file: str, output_file: str = "enhanced_submission.csv") -> List[EnhancedQAResult]:
        """Process test file with enhanced AI"""
        results = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                total = sum(1 for _ in open(test_file, encoding='utf-8')) - 1
                
                logger.info(f"Processing {total} questions with enhanced AI...")
                
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
                    
                    if i % 20 == 0:
                        logger.info(f"Processed {i}/{total} questions...")
        
        except Exception as e:
            logger.error(f"Error processing test file: {e}")
        
        # Save results
        self._save_submission(results, output_file)
        return results
    
    def _save_submission(self, results: List[EnhancedQAResult], output_file: str):
        """Save enhanced results"""
        # Main submission file
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'answer'])
            
            for result in results:
                answer_str = ','.join(result.predicted_answers)
                writer.writerow([result.id, f'"{answer_str}"'])
        
        logger.info(f"Enhanced submission saved to {output_file}")
        
        # Detailed analysis
        detailed_file = output_file.replace('.csv', '_analysis.json')
        with open(detailed_file, 'w', encoding='utf-8') as f:
            analysis = []
            for result in results:
                analysis.append({
                    'id': result.id,
                    'question': result.question,
                    'predicted_answers': result.predicted_answers,
                    'confidence': result.confidence,
                    'method_used': result.method_used,
                    'reasoning_chain': result.reasoning_chain,
                    'evidence_count': len(result.evidence)
                })
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed analysis saved to {detailed_file}")

def main():
    """Run enhanced system"""
    print("🚀 Enhanced Thai Healthcare Q&A System")
    print("=" * 50)
    
    # Configuration
    knowledge_files = [
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
    
    # Initialize with best available AI
    use_openai = os.getenv('OPENAI_API_KEY') is not None
    qa_system = EnhancedThaiHealthcareQA(
        knowledge_files,
        use_openai=use_openai,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Process questions
    results = qa_system.process_test_file(test_file)
    
    # Analysis
    print(f"\n📊 Enhanced Processing Results:")
    print(f"Total questions: {len(results)}")
    print(f"Average confidence: {np.mean([r.confidence for r in results]):.3f}")
    
    method_counts = {}
    for result in results:
        method_counts[result.method_used] = method_counts.get(result.method_used, 0) + 1
    
    print(f"Methods used:")
    for method, count in method_counts.items():
        print(f"  {method}: {count} ({count/len(results)*100:.1f}%)")

if __name__ == "__main__":
    main()