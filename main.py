#!/usr/bin/env python3
"""
Main application for Thai RAG System
"""

import os
import sys
from typing import Optional
import argparse

from vector_database import ThaiTextVectorDatabase
from llm_client import create_llm_client, setup_ollama_recommendations
from rag_system import ThaiRAGSystem


class ThaiRAGApp:
    """Main application class for Thai RAG System."""

    def __init__(self):
        self.vector_db = None
        self.llm_client = None
        self.rag_system = None

        # Default file paths
        self.default_text_file = "thai_text.txt"
        self.default_index_file = "thai_vector_index.faiss"
        self.default_metadata_file = "thai_metadata.json"

    def setup_vector_database(
        self, text_file: Optional[str] = None, force_rebuild: bool = False
    ) -> bool:
        """
        Setup vector database from text file or load existing.

        Args:
            text_file: Path to text file
            force_rebuild: Force rebuild even if saved database exists

        Returns:
            True if setup successful
        """
        print("=== Setting up Vector Database ===")

        # Initialize database
        self.vector_db = ThaiTextVectorDatabase(vector_dim=384)

        # Try to load existing database first (unless force rebuild)
        if not force_rebuild and os.path.exists(self.default_index_file):
            if self.vector_db.load(self.default_index_file, self.default_metadata_file):
                print(
                    f"✓ Loaded existing database with {self.vector_db.size()} entries"
                )
                return True

        # Create new database from text file
        text_file = text_file or self.default_text_file

        if not os.path.exists(text_file):
            print(f"✗ Text file not found: {text_file}")
            print("Please provide a text file with one sentence per line")
            return False

        print(f"Creating new database from {text_file}...")
        count = self.vector_db.add_texts_from_file(text_file)

        if count == 0:
            print("✗ No texts were added to the database")
            return False

        # Save the database
        self.vector_db.save(self.default_index_file, self.default_metadata_file)
        print(f"✓ Created and saved database with {count} entries")

        return True

    def setup_llm_client(
        self, client_type: str = "ollama", model: str = "llama2", **kwargs
    ) -> bool:
        """
        Setup LLM client.

        Args:
            client_type: Type of LLM client ('ollama', 'mock')
            model: Model name for Ollama
            **kwargs: Additional client parameters

        Returns:
            True if setup successful
        """
        print("=== Setting up LLM Client ===")

        try:
            if client_type == "ollama":
                self.llm_client = create_llm_client("ollama", model=model, **kwargs)

                # Test connection and model availability
                if not self.llm_client.test_connection():
                    print("✗ Cannot connect to Ollama server")
                    print("Please make sure Ollama is running: ollama serve")
                    return False

                # Check if model is available
                available_models = self.llm_client.list_models()
                if model not in available_models:
                    print(f"✗ Model '{model}' not found")
                    print(f"Available models: {available_models}")
                    print(f"To install: ollama pull {model}")
                    return False

                print(f"✓ Connected to Ollama with model '{model}'")

            elif client_type == "mock":
                self.llm_client = create_llm_client("mock")
                print("✓ Using Mock LLM client for testing")

            else:
                print(f"✗ Unknown client type: {client_type}")
                return False

            return True

        except Exception as e:
            print(f"✗ Error setting up LLM client: {e}")
            return False

    def setup_rag_system(self) -> bool:
        """Setup RAG system with database and LLM client."""
        if not self.vector_db:
            print("✗ Vector database not initialized")
            return False

        print("=== Setting up RAG System ===")
        self.rag_system = ThaiRAGSystem(self.vector_db, self.llm_client)

        info = self.rag_system.get_system_info()
        print(f"✓ RAG system ready with {info['vector_db_size']} documents")
        print(
            f"✓ LLM client: {'Yes' if info['has_llm_client'] else 'No (fallback mode)'}"
        )

        return True

    def interactive_mode(self):
        """Run interactive Q&A mode."""
        if not self.rag_system:
            print("✗ RAG system not initialized")
            return

        print("\n" + "=" * 50)
        print("🤖 Thai RAG System - Interactive Mode")
        print("=" * 50)
        print("Type your questions in Thai or English")
        print("Commands: 'quit', 'exit', 'help', 'stats'")
        print("=" * 50)

        while True:
            try:
                # Get user input
                query = input("\n❓ คำถาม (Question): ").strip()

                if not query:
                    continue

                if query.startswith("debug:"):
                    actual_query = query[6:].strip()
                    self.debug_search(actual_query)
                    continue

                # Handle commands
                if query.lower() in ["quit", "exit", "ออก"]:
                    print("👋 ลาก่อน! (Goodbye!)")
                    break

                elif query.lower() in ["help", "ช่วยเหลือ"]:
                    self.show_help()
                    continue

                elif query.lower() in ["stats", "สถิติ"]:
                    self.show_stats()
                    continue

                # Process question
                print("🔍 กำลังค้นหา... (Searching...)")
                result = self.rag_system.answer_question(query)

                # Display results
                self.display_result(result)

            except KeyboardInterrupt:
                print("\n\n👋 ลาก่อน! (Goodbye!)")
                break
            except Exception as e:
                print(f"❌ เกิดข้อผิดพลาด: {e}")

    def debug_search(self, query: str):
        """Debug search functionality."""
        print(f"\n=== DEBUG SEARCH: {query} ===")

        # Test with different thresholds
        thresholds = [0.05, 0.1, 0.15, 0.2, 0.3]
        for threshold in thresholds:
            results = self.vector_db.search(query, k=5, distance_threshold=5.0)
            relevant = [r for r in results if r.relevance_score >= threshold]
            print(f"Threshold {threshold}: {len(relevant)} results")
            if relevant:
                print(
                    f"  Best match: {relevant[0].text[:50]}... (score: {relevant[0].relevance_score:.3f})"
                )

    def batch_mode(self, questions: list):
        """Run batch processing mode."""
        if not self.rag_system:
            print("✗ RAG system not initialized")
            return

        print(f"\n=== Processing {len(questions)} questions ===")

        results = self.rag_system.batch_answer(questions)

        for i, result in enumerate(results, 1):
            print(f"\n--- Question {i} ---")
            print(f"Q: {result['query']}")
            print(f"A: {result['answer']}")
            print(f"Confidence: {result['confidence']:.2f}")
            if result.get("error"):
                print(f"Error: {result['error']}")

    def display_result(self, result: dict):
        """Display a single result in a formatted way."""
        print("\n" + "─" * 50)
        print("💡 คำตอบ (Answer):")
        print("─" * 50)
        print(result["answer"])

        print(f"\n📊 ความเชื่อมั่น (Confidence): {result['confidence']:.2f}")
        print(f"📄 จำนวนข้อมูลอ้างอิง: {result['num_context_used']}")

        if result["context"] and len(result["context"]) > 0:
            print("\n📚 ข้อมูลอ้างอิง (References):")
            for i, ctx in enumerate(result["context"][:3], 1):  # Show max 3 references
                print(f"   {i}. {ctx}")
            if len(result["context"]) > 3:
                print(f"   ... และอีก {len(result['context']) - 3} รายการ")

    def show_help(self):
        """Show help information."""
        print("\n📖 คำแนะนำการใช้งาน (Usage Guide):")
        print("─" * 40)
        print("• พิมพ์คำถามเป็นภาษาไทยหรือภาषาอังกฤษ")
        print("• 'quit' หรือ 'exit' - ออกจากโปรแกรม")
        print("• 'stats' - แสดงสถิติของระบบ")
        print("• 'help' - แสดงคำแนะนำนี้")
        print("\n💡 ตัวอย่างคำถาม:")
        print("• การเรียนรู้มีความสำคัญอย่างไร")
        print("• วิธีการดูแลสุขภาพ")
        print("• ความสุขคืออะไร")

    def show_stats(self):
        """Show system statistics."""
        if not self.rag_system:
            return

        info = self.rag_system.get_system_info()
        print("\n📈 สถิติระบบ (System Statistics):")
        print("─" * 40)
        print(f"• จำนวนข้อมูลทั้งหมด: {info['vector_db_size']:,}")
        print(f"• มิติของเวกเตอร์: {info['vector_db_stats']['vector_dimension']}")
        print(f"• LLM Client: {info['llm_client_type'] or 'ไม่มี'}")
        print(f"• Top-K เริ่มต้น: {info['default_settings']['top_k']}")
        print(f"• ค่าความเกี่ยวข้องขั้นต่ำ: {info['default_settings']['min_relevance']}")


def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(
        description="Thai RAG System - Retrieval Augmented Generation for Thai Text"
    )

    # Database options
    parser.add_argument(
        "--text-file", type=str, help="Path to Thai text file (one sentence per line)"
    )
    parser.add_argument(
        "--rebuild-db", action="store_true", help="Force rebuild vector database"
    )

    # LLM options
    parser.add_argument(
        "--llm-type",
        choices=["ollama", "mock"],
        default="ollama",
        help="Type of LLM client to use",
    )
    parser.add_argument(
        "--model", type=str, default="llama2", help="Model name for Ollama"
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama server URL",
    )

    # Mode options
    parser.add_argument(
        "--batch", nargs="+", help="Run in batch mode with specified questions"
    )
    parser.add_argument(
        "--setup-ollama", action="store_true", help="Show Ollama setup instructions"
    )

    args = parser.parse_args()

    # Show Ollama setup if requested
    if args.setup_ollama:
        setup_ollama_recommendations()
        return

    # Initialize application
    app = ThaiRAGApp()

    print("🚀 Starting Thai RAG System...")

    # Setup vector database
    if not app.setup_vector_database(args.text_file, args.rebuild_db):
        print("❌ Failed to setup vector database")
        sys.exit(1)

    # Setup LLM client
    llm_kwargs = {}
    if args.llm_type == "ollama":
        llm_kwargs["base_url"] = args.ollama_url

    if not app.setup_llm_client(args.llm_type, args.model, **llm_kwargs):
        print("⚠️  LLM setup failed, using fallback mode")
        app.llm_client = None

    # Setup RAG system
    if not app.setup_rag_system():
        print("❌ Failed to setup RAG system")
        sys.exit(1)

    print("✅ System ready!")

    # Run in appropriate mode
    if args.batch:
        app.batch_mode(args.batch)
    else:
        app.interactive_mode()


if __name__ == "__main__":
    main()
