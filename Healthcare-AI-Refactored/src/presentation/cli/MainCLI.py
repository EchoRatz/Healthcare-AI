"""Main CLI interface for Healthcare AI."""

import sys
from typing import Dict, Any

from core.use_cases.ProcessQuestion import ProcessQuestion
from shared.config.Config import AppConfig
from shared.logging.LoggerMixin import get_logger


class MainCLI:
    """Main command-line interface."""
    
    def __init__(self, process_question: ProcessQuestion, config: AppConfig):
        self.process_question = process_question
        self.config = config
        self.logger = get_logger(__name__)
        self.running = True
    
    def run(self):
        """Run the main CLI loop."""
        print("\n🏥 Healthcare AI Assistant")
        print("=" * 50)
        print("Ask me questions about healthcare topics!")
        print("Commands: 'help', 'quit', 'exit', 'stats'")
        print("-" * 50)
        
        while self.running:
            try:
                user_input = input("\n💬 Your question: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    self._handle_quit()
                elif user_input.lower() in ['help', 'h']:
                    self._handle_help()
                elif user_input.lower() in ['stats', 'status']:
                    self._handle_stats()
                elif user_input.lower().startswith('config'):
                    self._handle_config(user_input)
                else:
                    # Process as question
                    self._handle_question(user_input)
                    
            except KeyboardInterrupt:
                self._handle_quit()
            except Exception as e:
                self.logger.error(f"CLI error: {e}")
                print(f"❌ Error: {e}")
    
    def _handle_question(self, question: str):
        """Handle a user question."""
        try:
            print("\n🤔 Processing your question...")
            
            # Process the question
            result = self.process_question.process(question)
            
            # Display results
            self._display_result(result)
            
        except Exception as e:
            self.logger.error(f"Question processing error: {e}")
            print(f"❌ Sorry, I encountered an error: {e}")
    
    def _display_result(self, result: Dict[str, Any]):
        """Display the processing result."""
        print("\n" + "=" * 60)
        print("🤖 Answer:")
        print("-" * 60)
        print(result.get('answer', 'No answer generated'))
        
        # Display confidence
        confidence = result.get('confidence', 0.0)
        confidence_emoji = "🟢" if confidence > 0.7 else "🟡" if confidence > 0.4 else "🔴"
        print(f"\n{confidence_emoji} Confidence: {confidence:.1%}")
        
        # Display sources
        sources = result.get('sources', [])
        if sources:
            print(f"\n📚 Sources ({len(sources)} documents):")
            print("-" * 30)
            for i, source in enumerate(sources, 1):
                relevance = source.get('relevance_score', 0.0)
                preview = source.get('content_preview', '')[:100] + "..."
                print(f"{i}. Score: {relevance:.3f} | {preview}")
        else:
            print("\n📚 No sources found")
        
        print("=" * 60)
    
    def _handle_help(self):
        """Display help information."""
        print("\n" + "=" * 50)
        print("🆘 Healthcare AI Assistant - Help")
        print("=" * 50)
        print("Commands:")
        print("  help, h       - Show this help message")
        print("  quit, exit, q - Exit the application")
        print("  stats, status - Show system statistics")
        print("  config show   - Show current configuration")
        print("\nUsage:")
        print("  Simply type your healthcare question and press Enter")
        print("  The AI will search relevant documents and provide answers")
        print("\nExamples:")
        print("  'What are the symptoms of diabetes?'")
        print("  'How is hypertension diagnosed?'")
        print("  'What treatments are available for asthma?'")
        print("=" * 50)
    
    def _handle_stats(self):
        """Display system statistics."""
        try:
            doc_count = self.process_question.search_documents.get_document_count()
            
            print("\n" + "=" * 40)
            print("📊 System Statistics")
            print("=" * 40)
            print(f"Documents indexed: {doc_count}")
            print(f"LLM Model: {self.config.llm.model_name}")
            print(f"LLM Status: {'🟢 Available' if self.process_question.llm_client.is_available() else '🔴 Unavailable'}")
            print(f"Vector Dimension: {self.config.database.vector_dimension}")
            print("=" * 40)
            
        except Exception as e:
            self.logger.error(f"Stats error: {e}")
            print(f"❌ Error getting statistics: {e}")
    
    def _handle_config(self, command: str):
        """Handle configuration commands."""
        try:
            parts = command.split()
            if len(parts) > 1 and parts[1].lower() == 'show':
                print("\n" + "=" * 40)
                print("⚙️  Current Configuration")
                print("=" * 40)
                print(f"Log Level: {self.config.log_level}")
                print(f"LLM Base URL: {self.config.llm.base_url}")
                print(f"LLM Model: {self.config.llm.model_name}")
                print(f"Database Path: {self.config.database.storage_path}")
                print(f"Vector Dimension: {self.config.database.vector_dimension}")
                print("=" * 40)
            else:
                print("Usage: config show")
                
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            print(f"❌ Error showing configuration: {e}")
    
    def _handle_quit(self):
        """Handle quit command."""
        print("\n👋 Thank you for using Healthcare AI Assistant!")
        print("Stay healthy! 🏥")
        self.running = False
    
    def display_startup_info(self):
        """Display startup information."""
        try:
            doc_count = self.process_question.search_documents.get_document_count()
            llm_status = "Available" if self.process_question.llm_client.is_available() else "Unavailable"
            
            print(f"📊 System Status:")
            print(f"   Documents: {doc_count}")
            print(f"   LLM: {llm_status}")
            print(f"   Ready to answer your questions!")
            
        except Exception as e:
            self.logger.warning(f"Could not display startup info: {e}")