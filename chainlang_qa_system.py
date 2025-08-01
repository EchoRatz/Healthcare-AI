"""
ChainLang Q&A System with Agentic Reasoning
==========================================

A Chain of Thought + Agentic reasoning system that processes questions from CSV,
consults text files as knowledge base, and maintains memory of previous Q&A pairs.

Architecture: Load → Parse → Retrieve → Reason → Answer → Store
"""

import csv
import json
import re
import os
from typing import Dict, List, Tuple, Optional, Any
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
class QuestionAnswer:
    """Data structure for storing Q&A pairs with metadata"""
    question: str
    answer: str
    source: str  # 'docs', 'memory', or 'not_found'
    confidence: float
    timestamp: str
    reasoning_chain: List[str]

@dataclass
class ReasoningStep:
    """Individual step in the chain of thought reasoning"""
    step_type: str  # 'retrieve', 'analyze', 'infer', 'conclude'
    description: str
    evidence: List[str]
    confidence: float

class ChainLangQASystem:
    """
    Main Q&A System implementing ChainLang (Chain of Thought + Agentic Reasoning)
    """
    
    def __init__(self, knowledge_files: List[str], memory_file: str = "qa_memory.json"):
        """
        Initialize the Q&A system
        
        Args:
            knowledge_files: List of .txt files to use as knowledge base
            memory_file: JSON file to persist Q&A memory
        """
        self.knowledge_files = knowledge_files
        self.memory_file = memory_file
        self.knowledge_base = {}
        self.qa_memory = {}
        self.vectorizer = None
        self.doc_vectors = None
        self.memory_vectors = None
        
        # Chain of Thought reasoning steps
        self.reasoning_chain = []
        
        logger.info("Initializing ChainLang Q&A System...")
        self._load_knowledge_base()
        self._load_memory()
        self._initialize_embeddings()
    
    def _load_knowledge_base(self) -> None:
        """Load and parse text files into knowledge base"""
        logger.info("Loading knowledge base from text files...")
        
        for file_path in self.knowledge_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Clean and preprocess text
                    cleaned_content = self._preprocess_text(content)
                    self.knowledge_base[file_path] = {
                        'content': cleaned_content,
                        'sentences': self._split_into_sentences(cleaned_content)
                    }
                logger.info(f"Loaded {file_path}: {len(cleaned_content)} characters")
            except FileNotFoundError:
                logger.warning(f"Knowledge file not found: {file_path}")
            except Exception as e:
                logger.error(f"Error loading {file_path}: {str(e)}")
    
    def _load_memory(self) -> None:
        """Load previous Q&A pairs from memory file"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                    for item in memory_data:
                        qa = QuestionAnswer(**item)
                        self.qa_memory[qa.question] = qa
                logger.info(f"Loaded {len(self.qa_memory)} Q&A pairs from memory")
            else:
                logger.info("No existing memory file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading memory: {str(e)}")
    
    def _save_memory(self) -> None:
        """Save current Q&A memory to file"""
        try:
            memory_data = [asdict(qa) for qa in self.qa_memory.values()]
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.qa_memory)} Q&A pairs to memory")
        except Exception as e:
            logger.error(f"Error saving memory: {str(e)}")
    
    def _preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for better matching"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:-]', '', text)
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for granular search"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _initialize_embeddings(self) -> None:
        """Initialize TF-IDF vectorizer for similarity search"""
        logger.info("Initializing embeddings for similarity search...")
        
        # Collect all documents for vectorization
        all_docs = []
        for kb_entry in self.knowledge_base.values():
            all_docs.extend(kb_entry['sentences'])
        
        if all_docs:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            self.doc_vectors = self.vectorizer.fit_transform(all_docs)
            logger.info(f"Created embeddings for {len(all_docs)} document sentences")
    
    def load_questions_from_csv(self, csv_file: str) -> List[str]:
        """
        Load questions from CSV file
        
        Args:
            csv_file: Path to the CSV file containing questions
            
        Returns:
            List of questions
        """
        questions = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Skip header if present
                header = next(reader, None)
                if header and 'question' not in header[0].lower():
                    questions.append(header[0])  # First row is a question, not header
                
                for row in reader:
                    if row and row[0].strip():  # Non-empty question
                        questions.append(row[0].strip())
            
            logger.info(f"Loaded {len(questions)} questions from {csv_file}")
            return questions
        except FileNotFoundError:
            logger.error(f"Questions file not found: {csv_file}")
            return []
        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            return []
    
    def _find_relevant_documents(self, question: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
        """
        Find relevant document sentences using TF-IDF similarity
        
        Args:
            question: The input question
            top_k: Number of top relevant sentences to return
            
        Returns:
            List of (sentence, source_file, similarity_score) tuples
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
            if similarities[idx] > 0.1:  # Minimum similarity threshold
                results.append((
                    doc_sentences[idx],
                    doc_sources[idx],
                    similarities[idx]
                ))
        
        return results
    
    def _search_memory_for_answer(self, question: str, threshold: float = 0.3) -> Optional[QuestionAnswer]:
        """
        Search memory for similar questions using keyword matching and TF-IDF
        
        Args:
            question: The current question
            threshold: Minimum similarity threshold
            
        Returns:
            Most similar Q&A pair from memory or None
        """
        if not self.qa_memory:
            return None
        
        best_match = None
        best_score = 0
        
        # Simple keyword-based similarity for now
        question_words = set(question.lower().split())
        
        for stored_question, qa_pair in self.qa_memory.items():
            stored_words = set(stored_question.lower().split())
            
            # Calculate Jaccard similarity
            intersection = question_words.intersection(stored_words)
            union = question_words.union(stored_words)
            
            if union:
                similarity = len(intersection) / len(union)
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = qa_pair
        
        return best_match
    
    def _chain_of_thought_reasoning(self, question: str) -> QuestionAnswer:
        """
        Apply Chain of Thought reasoning to answer the question
        
        Args:
            question: The input question
            
        Returns:
            QuestionAnswer object with reasoning chain
        """
        reasoning_chain = []
        
        # Step 1: Document Retrieval
        reasoning_chain.append("Step 1: Searching knowledge base for relevant information...")
        relevant_docs = self._find_relevant_documents(question, top_k=5)
        
        if relevant_docs:
            reasoning_chain.append(f"Found {len(relevant_docs)} relevant document segments")
            
            # Step 2: Direct Answer Extraction
            reasoning_chain.append("Step 2: Attempting direct answer extraction from documents...")
            direct_answer = self._extract_direct_answer(question, relevant_docs)
            
            if direct_answer:
                reasoning_chain.append("Step 3: Direct answer found in knowledge base")
                return QuestionAnswer(
                    question=question,
                    answer=direct_answer,
                    source="docs",
                    confidence=0.8,
                    timestamp=datetime.now().isoformat(),
                    reasoning_chain=reasoning_chain
                )
        
        # Step 3: Memory Search
        reasoning_chain.append("Step 3: Searching memory for similar questions...")
        memory_match = self._search_memory_for_answer(question)
        
        if memory_match:
            reasoning_chain.append("Step 4: Found similar question in memory, adapting answer...")
            adapted_answer = self._adapt_memory_answer(question, memory_match)
            return QuestionAnswer(
                question=question,
                answer=adapted_answer,
                source="memory",
                confidence=0.6,
                timestamp=datetime.now().isoformat(),
                reasoning_chain=reasoning_chain
            )
        
        # Step 4: Inference Attempt
        reasoning_chain.append("Step 4: Attempting inference from available information...")
        if relevant_docs:
            inferred_answer = self._attempt_inference(question, relevant_docs)
            if inferred_answer:
                reasoning_chain.append("Step 5: Generated plausible answer through inference")
                return QuestionAnswer(
                    question=question,
                    answer=inferred_answer,
                    source="docs",
                    confidence=0.4,
                    timestamp=datetime.now().isoformat(),
                    reasoning_chain=reasoning_chain
                )
        
        # Step 5: No Answer Found
        reasoning_chain.append("Step 5: No sufficient information found")
        return QuestionAnswer(
            question=question,
            answer="Answer not found in provided documents or memory.",
            source="not_found",
            confidence=0.0,
            timestamp=datetime.now().isoformat(),
            reasoning_chain=reasoning_chain
        )
    
    def _extract_direct_answer(self, question: str, relevant_docs: List[Tuple[str, str, float]]) -> Optional[str]:
        """
        Attempt to extract a direct answer from relevant documents
        
        Args:
            question: The input question
            relevant_docs: List of relevant document segments
            
        Returns:
            Direct answer if found, None otherwise
        """
        question_lower = question.lower()
        
        # Look for direct answers in highly relevant documents
        for doc_text, source, similarity in relevant_docs:
            if similarity > 0.3:  # High similarity threshold
                # Simple pattern matching for common question types
                if any(word in question_lower for word in ['what is', 'define', 'definition']):
                    # Look for definitions
                    sentences = doc_text.split('.')
                    for sentence in sentences:
                        if any(word in sentence.lower() for word in question_lower.split()[2:]):
                            return sentence.strip()
                
                elif any(word in question_lower for word in ['how', 'why', 'when', 'where']):
                    # Look for explanatory content
                    if len(doc_text) > 20:  # Substantial content
                        return doc_text[:200] + "..." if len(doc_text) > 200 else doc_text
        
        return None
    
    def _adapt_memory_answer(self, question: str, memory_match: QuestionAnswer) -> str:
        """
        Adapt a memory answer to the current question
        
        Args:
            question: Current question
            memory_match: Similar Q&A pair from memory
            
        Returns:
            Adapted answer
        """
        base_answer = memory_match.answer
        if base_answer == "Answer not found in provided documents or memory.":
            return base_answer
        
        # Simple adaptation - add context about similarity
        return f"Based on a similar question, {base_answer}"
    
    def _attempt_inference(self, question: str, relevant_docs: List[Tuple[str, str, float]]) -> Optional[str]:
        """
        Attempt to infer an answer from relevant documents
        
        Args:
            question: The input question
            relevant_docs: List of relevant document segments
            
        Returns:
            Inferred answer if possible, None otherwise
        """
        if not relevant_docs:
            return None
        
        # Combine top relevant documents for inference
        combined_context = " ".join([doc[0] for doc in relevant_docs[:3]])
        
        if len(combined_context) > 50:  # Enough context for inference
            return f"Based on available information: {combined_context[:150]}..."
        
        return None
    
    def answer_question(self, question: str) -> QuestionAnswer:
        """
        Main method to answer a question using ChainLang reasoning
        
        Args:
            question: The input question
            
        Returns:
            QuestionAnswer object with complete reasoning chain
        """
        logger.info(f"Processing question: {question}")
        
        # Apply Chain of Thought reasoning
        qa_result = self._chain_of_thought_reasoning(question)
        
        # Store in memory if we found an answer
        if qa_result.source != "not_found":
            self.qa_memory[question] = qa_result
        
        return qa_result
    
    def process_csv_questions(self, csv_file: str, output_file: str = "answers.csv") -> List[QuestionAnswer]:
        """
        Process all questions from CSV file and generate answers
        
        Args:
            csv_file: Input CSV file with questions
            output_file: Output CSV file for answers
            
        Returns:
            List of all Q&A results
        """
        questions = self.load_questions_from_csv(csv_file)
        results = []
        
        logger.info(f"Processing {len(questions)} questions...")
        
        for i, question in enumerate(questions, 1):
            logger.info(f"Question {i}/{len(questions)}: {question[:50]}...")
            
            qa_result = self.answer_question(question)
            results.append(qa_result)
            
            # Print progress
            print(f"\nQ{i}: {question}")
            print(f"A{i}: {qa_result.answer}")
            print(f"Source: {qa_result.source} (Confidence: {qa_result.confidence:.2f})")
            print(f"Reasoning: {' → '.join(qa_result.reasoning_chain[-2:])}")  # Last 2 steps
            print("-" * 80)
        
        # Save results to CSV
        self._save_results_to_csv(results, output_file)
        # Save memory
        self._save_memory()
        
        return results
    
    def _save_results_to_csv(self, results: List[QuestionAnswer], output_file: str) -> None:
        """Save Q&A results to CSV file"""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Question', 'Answer', 'Source', 'Confidence', 'Timestamp'])
                
                for qa in results:
                    writer.writerow([
                        qa.question,
                        qa.answer,
                        qa.source,
                        qa.confidence,
                        qa.timestamp
                    ])
            
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")

def main():
    """
    Main function to run the ChainLang Q&A System
    """
    print("🔗 ChainLang Q&A System with Agentic Reasoning")
    print("=" * 50)
    
    # Configuration
    knowledge_files = ['file1.txt', 'file2.txt', 'file3.txt']
    questions_file = 'questions.csv'
    
    # Initialize the system
    qa_system = ChainLangQASystem(knowledge_files)
    
    # Process questions
    results = qa_system.process_csv_questions(questions_file)
    
    # Summary
    print(f"\n📊 Processing Summary:")
    print(f"Total questions processed: {len(results)}")
    print(f"Answered from documents: {sum(1 for r in results if r.source == 'docs')}")
    print(f"Answered from memory: {sum(1 for r in results if r.source == 'memory')}")
    print(f"Not found: {sum(1 for r in results if r.source == 'not_found')}")
    print(f"Average confidence: {np.mean([r.confidence for r in results]):.2f}")

if __name__ == "__main__":
    main()