"""
Thai Healthcare Q&A System with ChainLang Reasoning
==================================================

Specialized ChainLang system for Thai healthcare multiple-choice question answering
based on healthcare policy documents. Outputs predictions in submission format.

Architecture: Load → Parse → Retrieve → Reason → Classify → Submit
"""

import csv
import json
import re
import os
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ThaiQAResult:
    """Result structure for Thai healthcare Q&A"""
    id: int
    question: str
    choices: Dict[str, str]  # {ก: option1, ข: option2, ค: option3, ง: option4}
    predicted_answers: List[str]  # List of predicted choice labels
    confidence: float
    reasoning_chain: List[str]
    evidence: List[str]  # Supporting text from documents

class ThaiHealthcareQASystem:
    """
    ChainLang Q&A System for Thai Healthcare Classification
    """
    
    def __init__(self, knowledge_files: List[str], memory_file: str = "thai_qa_memory.json"):
        """
        Initialize the Thai Healthcare Q&A system
        
        Args:
            knowledge_files: List of Thai healthcare document files
            memory_file: JSON file to persist Q&A memory
        """
        self.knowledge_files = knowledge_files
        self.memory_file = memory_file
        self.knowledge_base = {}
        self.qa_memory = {}
        self.vectorizer = None
        self.doc_vectors = None
        
        # Thai-specific patterns
        self.choice_pattern = re.compile(r'([ก-ง])\.\s*([^ก-ง]+?)(?=\s*[ก-ง]\.|$)')
        self.thai_sentence_pattern = re.compile(r'[^.!?]*[.!?]+|[^.!?]+$')
        
        logger.info("Initializing Thai Healthcare Q&A System...")
        self._load_knowledge_base()
        self._load_memory()
        self._initialize_embeddings()
    
    def _load_knowledge_base(self) -> None:
        """Load and parse Thai healthcare documents"""
        logger.info("Loading Thai healthcare knowledge base...")
        
        for file_path in self.knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Clean and preprocess Thai text
                    cleaned_content = self._preprocess_thai_text(content)
                    sentences = self._split_thai_sentences(cleaned_content)
                    
                    self.knowledge_base[file_path] = {
                        'content': cleaned_content,
                        'sentences': sentences,
                        'pages': self._extract_pages(content)
                    }
                logger.info(f"Loaded {file_path}: {len(sentences)} sentences")
            except FileNotFoundError:
                logger.warning(f"Knowledge file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
    
    def _preprocess_thai_text(self, text: str) -> str:
        """Clean and preprocess Thai text"""
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep Thai text and punctuation
        text = re.sub(r'[^\u0E00-\u0E7F\w\s.,!?;:()-]', '', text)
        return text.strip()
    
    def _split_thai_sentences(self, text: str) -> List[str]:
        """Split Thai text into sentences"""
        sentences = []
        # Split by periods, question marks, exclamation marks
        parts = re.split(r'[.!?]+', text)
        for part in parts:
            if part.strip() and len(part.strip()) > 10:  # Minimum sentence length
                sentences.append(part.strip())
        return sentences
    
    def _extract_pages(self, content: str) -> Dict[int, str]:
        """Extract page-wise content"""
        pages = {}
        page_pattern = re.compile(r'--- Page (\d+) ---(.*?)(?=--- Page \d+ ---|$)', re.DOTALL)
        matches = page_pattern.findall(content)
        
        for page_num, page_content in matches:
            pages[int(page_num)] = self._preprocess_thai_text(page_content)
        
        return pages
    
    def _load_memory(self) -> None:
        """Load previous Thai Q&A pairs from memory"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.qa_memory = json.load(f)
                logger.info(f"Loaded {len(self.qa_memory)} Thai Q&A pairs from memory")
            else:
                logger.info("No existing Thai Q&A memory found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
    
    def _save_memory(self) -> None:
        """Save current Q&A memory to file"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.qa_memory, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.qa_memory)} Thai Q&A pairs to memory")
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
    
    def _initialize_embeddings(self) -> None:
        """Initialize TF-IDF vectorizer for Thai text similarity"""
        logger.info("Initializing embeddings for Thai text similarity...")
        
        # Collect all Thai sentences
        all_sentences = []
        for kb_entry in self.knowledge_base.values():
            all_sentences.extend(kb_entry['sentences'])
        
        if all_sentences:
            # Use character-level n-grams for Thai text
            self.vectorizer = TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),
                analyzer='char',  # Character-level analysis for Thai
                lowercase=False   # Preserve Thai character casing
            )
            self.doc_vectors = self.vectorizer.fit_transform(all_sentences)
            logger.info(f"Created embeddings for {len(all_sentences)} Thai sentences")
    
    def parse_question(self, question_text: str) -> Tuple[str, Dict[str, str]]:
        """
        Parse Thai question and extract choices
        
        Args:
            question_text: Full question text with choices
            
        Returns:
            Tuple of (question, choices_dict)
        """
        # Split question from choices
        parts = question_text.split('ก.')
        if len(parts) < 2:
            return question_text, {}
        
        question = parts[0].strip()
        choices_text = 'ก.' + parts[1]
        
        # Extract choices
        choices = {}
        matches = self.choice_pattern.findall(choices_text)
        
        for choice_label, choice_text in matches:
            choices[choice_label] = choice_text.strip()
        
        return question, choices
    
    def _find_relevant_content(self, question: str, top_k: int = 10) -> List[Tuple[str, str, float]]:
        """
        Find relevant content from Thai healthcare documents
        
        Args:
            question: Thai question text
            top_k: Number of top relevant sentences
            
        Returns:
            List of (sentence, source_file, similarity_score)
        """
        if not self.vectorizer or self.doc_vectors is None:
            return []
        
        # Vectorize the question
        question_vector = self.vectorizer.transform([question])
        
        # Calculate similarities
        similarities = cosine_similarity(question_vector, self.doc_vectors)[0]
        
        # Get top-k most similar sentences
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        doc_sentences = []
        doc_sources = []
        
        for kb_file, kb_data in self.knowledge_base.items():
            for sentence in kb_data['sentences']:
                doc_sentences.append(sentence)
                doc_sources.append(kb_file)
        
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Minimum similarity threshold
                results.append((
                    doc_sentences[idx],
                    doc_sources[idx],
                    similarities[idx]
                ))
        
        return results
    
    def _search_memory_for_similar(self, question: str, threshold: float = 0.3) -> Optional[Dict]:
        """Search memory for similar Thai questions"""
        if not self.qa_memory:
            return None
        
        best_match = None
        best_score = 0
        
        # Simple keyword-based similarity for Thai text
        question_chars = set(question.lower())
        
        for stored_q, stored_data in self.qa_memory.items():
            stored_chars = set(stored_q.lower())
            
            # Calculate character-level Jaccard similarity
            intersection = question_chars.intersection(stored_chars)
            union = question_chars.union(stored_chars)
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = stored_data
        
        return best_match
    
    def _chain_of_thought_reasoning(self, question: str, choices: Dict[str, str]) -> ThaiQAResult:
        """
        Apply Chain of Thought reasoning for Thai healthcare questions
        
        Args:
            question: Thai question text
            choices: Dictionary of choice options
            
        Returns:
            ThaiQAResult with reasoning and predictions
        """
        reasoning_chain = []
        evidence = []
        
        # Step 1: Document Retrieval
        reasoning_chain.append("Step 1: ค้นหาข้อมูลที่เกี่ยวข้องจากเอกสารสุขภาพ")
        relevant_content = self._find_relevant_content(question, top_k=15)
        
        if relevant_content:
            reasoning_chain.append(f"พบข้อมูลที่เกี่ยวข้อง {len(relevant_content)} รายการ")
            evidence = [content[0] for content in relevant_content[:5]]  # Top 5 evidence
            
            # Step 2: Choice Analysis
            reasoning_chain.append("Step 2: วิเคราะห์ตัวเลือกแต่ละข้อ")
            choice_scores = {}
            
            for choice_label, choice_text in choices.items():
                # Calculate how well each choice matches the evidence
                choice_score = self._calculate_choice_score(choice_text, relevant_content)
                choice_scores[choice_label] = choice_score
                reasoning_chain.append(f"ตัวเลือก {choice_label}: คะแนน {choice_score:.3f}")
            
            # Step 3: Decision Making
            reasoning_chain.append("Step 3: ตัดสินใจเลือกคำตอบ")
            
            # Find best choices (can be multiple if scores are close)
            if choice_scores:
                max_score = max(choice_scores.values())
                threshold = max_score * 0.8  # Allow choices within 80% of max score
                
                predicted_answers = [
                    choice for choice, score in choice_scores.items() 
                    if score >= threshold and score > 0.1
                ]
                
                if not predicted_answers:
                    predicted_answers = [max(choice_scores.keys(), key=choice_scores.get)]
                
                confidence = max_score
                reasoning_chain.append(f"เลือกคำตอบ: {', '.join(predicted_answers)} (ความมั่นใจ: {confidence:.3f})")
            else:
                predicted_answers = ["ก"]  # Default fallback
                confidence = 0.1
                reasoning_chain.append("ไม่พบข้อมูลที่ชัดเจน ใช้คำตอบเริ่มต้น")
        
        else:
            # Step 3: Memory Search
            reasoning_chain.append("Step 3: ค้นหาคำถามที่คล้ายกันในหน่วยความจำ")
            memory_match = self._search_memory_for_similar(question)
            
            if memory_match and 'predicted_answers' in memory_match:
                predicted_answers = memory_match['predicted_answers']
                confidence = 0.5
                reasoning_chain.append("พบคำถามคล้ายกันในหน่วยความจำ")
            else:
                # Step 4: Fallback
                reasoning_chain.append("Step 4: ไม่พบข้อมูลที่เกี่ยวข้อง ใช้การคาดเดาแบบสุ่ม")
                predicted_answers = ["ข"]  # Common default for Thai multiple choice
                confidence = 0.1
        
        return ThaiQAResult(
            id=0,  # Will be set later
            question=question,
            choices=choices,
            predicted_answers=predicted_answers,
            confidence=confidence,
            reasoning_chain=reasoning_chain,
            evidence=evidence
        )
    
    def _calculate_choice_score(self, choice_text: str, relevant_content: List[Tuple[str, str, float]]) -> float:
        """Calculate how well a choice matches the relevant content"""
        if not relevant_content:
            return 0.0
        
        choice_chars = set(choice_text.lower())
        total_score = 0
        
        for content, source, similarity in relevant_content:
            content_chars = set(content.lower())
            
            # Character-level intersection
            intersection = choice_chars.intersection(content_chars)
            
            if choice_chars:
                char_match = len(intersection) / len(choice_chars)
                # Weight by document similarity
                score = char_match * similarity
                total_score += score
        
        return total_score / len(relevant_content) if relevant_content else 0.0
    
    def process_test_file(self, test_file: str, output_file: str = "submission.csv") -> List[ThaiQAResult]:
        """
        Process test CSV file and generate predictions
        
        Args:
            test_file: Input test CSV file
            output_file: Output submission CSV file
            
        Returns:
            List of all prediction results
        """
        results = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                total_questions = sum(1 for _ in open(test_file, encoding='utf-8')) - 1
                
                logger.info(f"Processing {total_questions} Thai healthcare questions...")
                
                f.seek(0)  # Reset file pointer
                reader = csv.DictReader(f)
                
                for i, row in enumerate(reader, 1):
                    question_id = int(row['id'])
                    full_question = row['question']
                    
                    # Parse question and choices
                    question, choices = self.parse_question(full_question)
                    
                    logger.info(f"Question {i}/{total_questions}: ID {question_id}")
                    
                    # Apply Chain of Thought reasoning
                    result = self._chain_of_thought_reasoning(question, choices)
                    result.id = question_id
                    
                    results.append(result)
                    
                    # Store in memory for future reference
                    self.qa_memory[question] = {
                        'predicted_answers': result.predicted_answers,
                        'confidence': result.confidence,
                        'choices': choices
                    }
                    
                    # Progress update
                    if i % 50 == 0 or i == total_questions:
                        logger.info(f"Processed {i}/{total_questions} questions...")
        
        except Exception as e:
            logger.error(f"Error processing test file: {str(e)}")
        
        # Save results to submission file
        self._save_submission_file(results, output_file)
        # Save memory
        self._save_memory()
        
        return results
    
    def _save_submission_file(self, results: List[ThaiQAResult], output_file: str) -> None:
        """Save results in the required submission format"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'answer'])
                
                for result in results:
                    # Format answers as comma-separated quoted string
                    answer_str = ','.join(result.predicted_answers)
                    writer.writerow([result.id, f'"{answer_str}"'])
            
            logger.info(f"Submission file saved to {output_file}")
            
            # Also save detailed results for analysis
            detailed_file = output_file.replace('.csv', '_detailed.json')
            with open(detailed_file, 'w', encoding='utf-8') as f:
                detailed_data = []
                for result in results:
                    detailed_data.append({
                        'id': result.id,
                        'question': result.question,
                        'choices': result.choices,
                        'predicted_answers': result.predicted_answers,
                        'confidence': result.confidence,
                        'reasoning_chain': result.reasoning_chain,
                        'evidence': result.evidence
                    })
                json.dump(detailed_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Detailed results saved to {detailed_file}")
            
        except Exception as e:
            logger.error(f"Error saving submission file: {str(e)}")

def main():
    """Main function to run the Thai Healthcare Q&A System"""
    print("🏥 Thai Healthcare Q&A System with ChainLang Reasoning")
    print("=" * 60)
    
    # Configuration
    knowledge_files = [
        'Healthcare-AI-Refactored/src/infrastructure/results_doc/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc2/direct_extraction_corrected.txt',
        'Healthcare-AI-Refactored/src/infrastructure/results_doc3/direct_extraction_corrected.txt'
    ]
    test_file = 'Healthcare-AI-Refactored/src/infrastructure/test.csv'
    
    # Initialize the system
    qa_system = ThaiHealthcareQASystem(knowledge_files)
    
    # Process test file and generate predictions
    results = qa_system.process_test_file(test_file, 'submission.csv')
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"Total questions processed: {len(results)}")
    print(f"Average confidence: {np.mean([r.confidence for r in results]):.3f}")
    print(f"High confidence predictions (>0.5): {sum(1 for r in results if r.confidence > 0.5)}")
    print(f"Multiple choice answers: {sum(1 for r in results if len(r.predicted_answers) > 1)}")
    print(f"\n📄 Files generated:")
    print(f"  - submission.csv (required format)")
    print(f"  - submission_detailed.json (analysis)")
    print(f"  - thai_qa_memory.json (system memory)")

if __name__ == "__main__":
    main()