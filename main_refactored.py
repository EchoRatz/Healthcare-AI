#!/usr/bin/env python3
"""
Thai RAG System - Main Application

Complete Thai language RAG (Retrieval-Augmented Generation) system
with CLI interface, batch processing, and comprehensive configuration.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

from vector_database import create_thai_vector_database, ThaiTextVectorDatabase
from llm_client_refactored import create_llm_client, LLMClient, LLMConfig
from rag_system_refactored import create_thai_rag_system, ThaiRAGSystem, RAGConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('thai_rag.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class ThaiRAGApp:
    """Main application class for Thai RAG System."""

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the Thai RAG application.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.vector_db: Optional[ThaiTextVectorDatabase] = None
        self.llm_client: Optional[LLMClient] = None
        self.rag_system: Optional[ThaiRAGSystem] = None
        
        # Default configuration
        self.config = {
            "vector_db": {
                "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
                "vector_dim": 384,
                "index_file": "thai_vector_index.faiss",
                "metadata_file": "thai_metadata.json"
            },
            "llm": {
                "client_type": "mock",
                "model": "llama3",
                "base_url": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 500
            },
            "rag": {
                "default_top_k": 5,
                "min_relevance_threshold": 0.3,
                "distance_threshold": 2.0,
                "max_context_length": 2000
            }
        }
        
        logger.info("Thai RAG Application initialized")

    def setup_vector_database(
        self, 
        text_file: Optional[str] = None, 
        force_rebuild: bool = False
    ) -> bool:
        """
        Setup the vector database.
        
        Args:
            text_file: Optional text file to load data from
            force_rebuild: Force rebuilding the database
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create vector database
            self.vector_db = create_thai_vector_database(
                model_name=self.config["vector_db"]["model_name"],
                vector_dim=self.config["vector_db"]["vector_dim"]
            )
            
            # Try to load existing database
            index_file = self.config["vector_db"]["index_file"]
            metadata_file = self.config["vector_db"]["metadata_file"]
            
            if not force_rebuild and Path(index_file).exists() and Path(metadata_file).exists():
                if self.vector_db.load(index_file, metadata_file):
                    logger.info(f"Loaded existing database with {self.vector_db.size()} entries")
                    return True
            
            # Load data from text file if provided
            if text_file and Path(text_file).exists():
                count = self.vector_db.add_texts_from_file(text_file)
                logger.info(f"Added {count} texts from {text_file}")
            else:
                # Add sample Thai healthcare data
                self._add_sample_data()
            
            # Save the database
            self.vector_db.save(index_file, metadata_file)
            logger.info("Vector database setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup vector database: {e}")
            return False

    def setup_llm_client(
        self, 
        client_type: str = None, 
        model: str = None, 
        **kwargs
    ) -> bool:
        """
        Setup the LLM client.
        
        Args:
            client_type: Type of LLM client
            model: Model name
            **kwargs: Additional configuration
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Use provided values or fall back to config
            client_type = client_type or self.config["llm"]["client_type"]
            model = model or self.config["llm"]["model"]
            
            # Create LLM configuration
            llm_config = LLMConfig(
                model=model,
                base_url=self.config["llm"]["base_url"],
                temperature=self.config["llm"]["temperature"],
                max_tokens=self.config["llm"]["max_tokens"],
                **kwargs
            )
            
            # Create LLM client
            self.llm_client = create_llm_client(client_type, llm_config)
            
            # Test connection
            if hasattr(self.llm_client, 'test_connection'):
                if self.llm_client.test_connection():
                    logger.info(f"LLM client connected: {client_type}")
                else:
                    logger.warning(f"LLM client connection failed: {client_type}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup LLM client: {e}")
            return False

    def setup_rag_system(self) -> bool:
        """
        Setup the RAG system.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.vector_db:
                logger.error("Vector database not initialized")
                return False
            
            # Create RAG configuration
            rag_config = RAGConfig(**self.config["rag"])
            
            # Create RAG system
            self.rag_system = create_thai_rag_system(
                self.vector_db, 
                self.llm_client, 
                rag_config
            )
            
            logger.info("RAG system setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup RAG system: {e}")
            return False

    def interactive_mode(self):
        """Run the application in interactive mode."""
        print("\n" + "="*60)
        print("🇹🇭 Thai RAG System - Interactive Mode")
        print("="*60)
        print("\nCommands:")
        print("  - Type a question to get an answer")
        print("  - 'add: <text>' to add new knowledge")
        print("  - 'search: <query>' to search the database")
        print("  - 'info' to show system information")
        print("  - 'config' to show current configuration")
        print("  - 'help' to show this help message")
        print("  - 'quit' to exit")
        print("-"*60)
        
        if not self.rag_system:
            print("❌ RAG system not initialized. Please setup first.")
            return
        
        while True:
            try:
                user_input = input("\n💬 Question: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Thank you for using Thai RAG System!")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                
                elif user_input.lower() == 'info':
                    self.show_system_info()
                
                elif user_input.lower() == 'config':
                    self.show_config()
                
                elif user_input.startswith('add:'):
                    text = user_input[4:].strip()
                    if self.vector_db and self.vector_db.add_text(text):
                        print(f"✅ Added: {text[:50]}...")
                    else:
                        print("❌ Failed to add text")
                
                elif user_input.startswith('search:'):
                    query = user_input[7:].strip()
                    self.debug_search(query)
                
                else:
                    # Answer the question
                    response = self.rag_system.answer_question(user_input)
                    self.display_result(response)
            
            except KeyboardInterrupt:
                print("\n👋 Thank you for using Thai RAG System!")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"❌ An error occurred: {e}")

    def debug_search(self, query: str):
        """Debug search functionality."""
        if not self.vector_db:
            print("❌ Vector database not initialized")
            return
        
        try:
            results = self.vector_db.search(query, k=5)
            
            if results:
                print(f"🔍 Found {len(results)} results for '{query}':")
                for i, result in enumerate(results, 1):
                    print(f"  {i}. [{result.relevance_score:.2f}] {result.text[:100]}...")
            else:
                print(f"❌ No results found for '{query}'")
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
            print(f"❌ Search error: {e}")

    def batch_mode(self, questions: List[str]):
        """Process questions in batch mode."""
        if not self.rag_system:
            logger.error("RAG system not initialized")
            return
        
        print(f"\n📋 Processing {len(questions)} questions in batch mode...")
        
        responses = self.rag_system.batch_answer(questions)
        
        for i, response in enumerate(responses, 1):
            print(f"\n--- Question {i} ---")
            self.display_result(response)

    def display_result(self, response):
        """Display a RAG response."""
        print(f"\n🎯 Question: {response.query}")
        print(f"📝 Answer: {response.answer}")
        print(f"🎲 Confidence: {response.confidence:.2f}")
        print(f"⏱️  Processing Time: {response.processing_time:.2f}s")
        
        if response.sources:
            print(f"📚 Sources ({len(response.sources)}):")
            for i, source in enumerate(response.sources[:3], 1):  # Show top 3
                print(f"  {i}. [{source.relevance_score:.2f}] {source.text[:80]}...")

    def show_help(self):
        """Show help information."""
        help_text = """
🇹🇭 Thai RAG System Help

Available Commands:
  - Type any question in Thai or English
  - add: <text>     Add new knowledge to the database
  - search: <query> Search the vector database
  - info           Show system information and statistics
  - config         Show current configuration
  - help           Show this help message
  - quit           Exit the application

Tips:
  - Ask specific questions for better results
  - Use Thai language for healthcare-related queries
  - The system learns from added knowledge
        """
        print(help_text)

    def show_system_info(self):
        """Show system information."""
        if self.rag_system:
            info = self.rag_system.get_system_info()
            print(f"\n📊 System Information:")
            print(f"  System: {info['system_name']} v{info['version']}")
            print(f"  Vector DB Size: {info['vector_database']['size']} entries")
            print(f"  Vector Dimension: {info['vector_database']['dimension']}")
            print(f"  Model: {info['vector_database']['model']}")
            print(f"  Memory Usage: {info['vector_database']['memory_usage_mb']:.1f} MB")
            print(f"  LLM Configured: {info['llm_client']['configured']}")
            if info['llm_client']['configured']:
                print(f"  LLM Type: {info['llm_client']['type']}")
        else:
            print("❌ System not initialized")

    def show_config(self):
        """Show current configuration."""
        print(f"\n⚙️  Current Configuration:")
        for section, config in self.config.items():
            print(f"  [{section}]")
            for key, value in config.items():
                print(f"    {key}: {value}")

    def _add_sample_data(self):
        """Add sample Thai healthcare data."""
        sample_data = [
            "โรงพยาบาลมีแผนกฉุกเฉินเปิดให้บริการตลอด 24 ชั่วโมง",
            "สิทธิการรักษาพยาบาลในระบบประกันสุขภาพแห่งชาติครอบคลุมการรักษาพยาบาลทั่วไป",
            "การตรวจสุขภาพประจำปีสำหรับผู้สูงอายุควรทำอย่างน้อยปีละ 1 ครั้ง",
            "การใช้ยาควรปฏิบัติตามคำแนะนำของแพทย์และเภสัชกรเท่านั้น",
            "การป้องกันโรคติดเชื้อไวรัสทำได้โดยการล้างมือบ่อยๆ และสวมหน้ากากอนามัย",
            "แผนกออร์โธปิดิกส์ให้บริการรักษาโรคกระดูกและข้อ",
            "แผนกอายุรกรรมดูแลผู้ป่วยโรคภายในต่างๆ",
            "แผนกกุมารเวชกรรมเฉพาะการรักษาเด็กและทารก",
            "ค่าบริการการตรวจคัดกรองมะเร็งเต้านมด้วยแมมโมแกรม",
            "สิทธิประกันสุขภาพครอบคลุมการรักษาแบบผู้ป่วยในและผู้ป่วยนอก"
        ]
        
        for text in sample_data:
            self.vector_db.add_text(text, {"category": "healthcare", "language": "thai"})
        
        logger.info(f"Added {len(sample_data)} sample healthcare entries")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Thai RAG System - Retrieval Augmented Generation for Thai Text",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Database options
    parser.add_argument(
        "--text-file", 
        type=str, 
        help="Path to Thai text file to load into database"
    )
    parser.add_argument(
        "--rebuild-db", 
        action="store_true", 
        help="Force rebuild vector database"
    )

    # LLM options
    parser.add_argument(
        "--llm-type",
        choices=["ollama", "mock", "openai"],
        default="mock",
        help="Type of LLM client to use"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="llama3", 
        help="Model name for LLM"
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama server URL"
    )

    # Mode options
    parser.add_argument(
        "--batch-file",
        type=str,
        help="File containing questions for batch processing"
    )
    parser.add_argument(
        "--question",
        type=str,
        help="Single question to answer"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode (default)"
    )

    # Logging
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create application
    app = ThaiRAGApp()

    # Update configuration with CLI arguments
    if args.ollama_url:
        app.config["llm"]["base_url"] = args.ollama_url
    
    app.config["llm"]["client_type"] = args.llm_type
    app.config["llm"]["model"] = args.model

    # Setup components
    print("🚀 Setting up Thai RAG System...")
    
    if not app.setup_vector_database(args.text_file, args.rebuild_db):
        print("❌ Failed to setup vector database")
        sys.exit(1)
    
    if not app.setup_llm_client():
        print("❌ Failed to setup LLM client")
        sys.exit(1)
    
    if not app.setup_rag_system():
        print("❌ Failed to setup RAG system")
        sys.exit(1)
    
    print("✅ Setup completed successfully!")

    # Run in requested mode
    if args.question:
        # Single question mode
        response = app.rag_system.answer_question(args.question)
        app.display_result(response)
    
    elif args.batch_file:
        # Batch processing mode
        try:
            with open(args.batch_file, 'r', encoding='utf-8') as f:
                questions = [line.strip() for line in f if line.strip()]
            app.batch_mode(questions)
        except Exception as e:
            print(f"❌ Error reading batch file: {e}")
            sys.exit(1)
    
    else:
        # Interactive mode (default)
        app.interactive_mode()


if __name__ == "__main__":
    main()
