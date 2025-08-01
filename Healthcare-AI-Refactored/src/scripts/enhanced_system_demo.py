#!/usr/bin/env python3
"""
Enhanced Chain-of-Thought System Demo

This script demonstrates the enhanced AI system with:
- Ollama 40GB model for chain-of-thought reasoning
- Pre-plan + fetch-all data retrieval strategy
- MCP, PDF, and Text connectors
- Batch processing capabilities

Usage:
    python enhanced_system_demo.py [--config config_path] [--query "your question"]
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.factories.EnhancedSystemFactory import EnhancedSystemFactory
from shared.logging.LoggerMixin import get_logger


class EnhancedSystemDemo:
    """Demo class for the enhanced chain-of-thought system."""
    
    def __init__(self, config_path: str = "config/enhanced_system.json"):
        self.logger = get_logger(__name__)
        self.factory = EnhancedSystemFactory(config_path)
        self.engine = None
    
    def setup_system(self) -> bool:
        """Set up the enhanced system."""
        try:
            self.logger.info("Setting up enhanced chain-of-thought system...")
            
            # Validate system
            validation = self.factory.validate_system()
            if not validation['valid']:
                self.logger.error("System validation failed:")
                for error in validation['errors']:
                    self.logger.error(f"  - {error}")
                return False
            
            if validation['warnings']:
                self.logger.warning("System warnings:")
                for warning in validation['warnings']:
                    self.logger.warning(f"  - {warning}")
            
            # Create engine
            self.engine = self.factory.create_chain_of_thought_engine()
            self.logger.info("Enhanced system setup complete!")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup system: {e}")
            return False
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information."""
        if not self.engine:
            return {"error": "System not initialized"}
        
        return self.engine.get_system_info()
    
    def process_single_query(self, query: str) -> Dict[str, Any]:
        """Process a single query with timing information."""
        if not self.engine:
            return {"error": "System not initialized"}
        
        try:
            self.logger.info(f"Processing query: {query}")
            start_time = time.time()
            
            result = self.engine.process_query(query)
            
            end_time = time.time()
            result['processing_time_seconds'] = end_time - start_time
            
            self.logger.info(f"Query processed in {result['processing_time_seconds']:.2f} seconds")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to process query: {e}")
            return {
                "query": query,
                "answer": f"Error processing query: {e}",
                "error": str(e),
                "processing_time_seconds": 0
            }
    
    def process_batch_queries(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Process multiple queries in batch."""
        if not self.engine:
            return [{"error": "System not initialized"} for _ in queries]
        
        try:
            self.logger.info(f"Processing {len(queries)} queries in batch...")
            start_time = time.time()
            
            results = self.engine.process_batch(queries)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            self.logger.info(f"Batch processing completed in {total_time:.2f} seconds")
            
            # Add timing information
            for result in results:
                result['batch_processing_time_seconds'] = total_time
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process batch queries: {e}")
            return [{"error": f"Batch processing failed: {e}"} for _ in queries]
    
    def run_demo_queries(self) -> List[Dict[str, Any]]:
        """Run a set of demo queries to showcase the system."""
        demo_queries = [
            "What are the main symptoms of diabetes?",
            "How do I configure the system for optimal performance?",
            "What are the latest treatment guidelines for hypertension?",
            "Can you explain the difference between Type 1 and Type 2 diabetes?",
            "What are the recommended daily exercise guidelines for adults?"
        ]
        
        self.logger.info("Running demo queries...")
        return self.process_batch_queries(demo_queries)
    
    def print_results(self, results: List[Dict[str, Any]], detailed: bool = False):
        """Print results in a formatted way."""
        print("\n" + "="*80)
        print("ENHANCED CHAIN-OF-THOUGHT SYSTEM RESULTS")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Query {i} ---")
            print(f"Question: {result.get('query', 'N/A')}")
            print(f"Answer: {result.get('answer', 'N/A')}")
            
            if detailed:
                if 'plan' in result:
                    plan = result['plan']
                    print(f"Retrieval Plan:")
                    print(f"  - MCP requests: {len(plan.get('mcp', []))}")
                    print(f"  - PDF requests: {len(plan.get('pdf', []))}")
                    print(f"  - Text requests: {len(plan.get('text', []))}")
                
                if 'context_sources' in result:
                    sources = result['context_sources']
                    print(f"Context Sources:")
                    print(f"  - MCP sources: {sources.get('mcp_sources', 0)}")
                    print(f"  - PDF sources: {sources.get('pdf_sources', 0)}")
                    print(f"  - Text sources: {sources.get('text_sources', 0)}")
                    print(f"  - Errors: {sources.get('errors', 0)}")
                
                if 'processing_time_seconds' in result:
                    print(f"Processing time: {result['processing_time_seconds']:.2f} seconds")
            
            if 'error' in result:
                print(f"ERROR: {result['error']}")
            
            print("-" * 40)
    
    def print_system_info(self):
        """Print system information."""
        info = self.get_system_info()
        
        print("\n" + "="*80)
        print("SYSTEM INFORMATION")
        print("="*80)
        
        print(f"Query Planner: {info.get('query_planner', {}).get('type', 'N/A')}")
        print(f"LLM Model: {info.get('llm_client', {}).get('model_info', {}).get('name', 'N/A')}")
        print(f"LLM Available: {info.get('llm_client', {}).get('available', False)}")
        
        connectors = info.get('connectors', {})
        print("\nConnectors:")
        for connector_type, connector_info in connectors.items():
            if connector_info:
                print(f"  - {connector_type.upper()}: Available")
                if 'base_path' in connector_info:
                    print(f"    Base path: {connector_info['base_path']}")
            else:
                print(f"  - {connector_type.upper()}: Not configured")


def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="Enhanced Chain-of-Thought System Demo")
    parser.add_argument("--config", default="config/enhanced_system.json", 
                       help="Path to configuration file")
    parser.add_argument("--query", help="Single query to process")
    parser.add_argument("--demo", action="store_true", help="Run demo queries")
    parser.add_argument("--detailed", action="store_true", help="Show detailed results")
    parser.add_argument("--info", action="store_true", help="Show system information")
    
    args = parser.parse_args()
    
    # Create demo instance
    demo = EnhancedSystemDemo(args.config)
    
    # Setup system
    if not demo.setup_system():
        print("Failed to setup system. Check logs for details.")
        return 1
    
    # Show system info if requested
    if args.info:
        demo.print_system_info()
    
    # Process queries
    if args.query:
        # Single query
        result = demo.process_single_query(args.query)
        demo.print_results([result], args.detailed)
    
    elif args.demo:
        # Demo queries
        results = demo.run_demo_queries()
        demo.print_results(results, args.detailed)
    
    else:
        # Interactive mode
        print("\nEnhanced Chain-of-Thought System Demo")
        print("Type 'quit' to exit, 'info' for system info, 'demo' for demo queries")
        
        while True:
            try:
                query = input("\nEnter your question: ").strip()
                
                if query.lower() == 'quit':
                    break
                elif query.lower() == 'info':
                    demo.print_system_info()
                elif query.lower() == 'demo':
                    results = demo.run_demo_queries()
                    demo.print_results(results, args.detailed)
                elif query:
                    result = demo.process_single_query(query)
                    demo.print_results([result], args.detailed)
                else:
                    print("Please enter a question.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    return 0


if __name__ == "__main__":
    exit(main()) 