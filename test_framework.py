#!/usr/bin/env python3
"""
Comprehensive Testing Framework for Healthcare-AI System

This module provides a complete testing framework with unit tests,
integration tests, and performance benchmarks.

Author: Healthcare-AI Team
Date: 2025-08-01
Version: 3.0.0
"""

import time
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single test."""
    
    test_name: str
    success: bool
    duration: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        status = "✅ PASS" if self.success else "❌ FAIL"
        return f"{status} {self.test_name} ({self.duration:.3f}s)"


@dataclass
class TestSuite:
    """Collection of test results."""
    
    name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: float = 0.0
    end_time: float = 0.0
    
    @property
    def total_tests(self) -> int:
        return len(self.results)
    
    @property
    def passed_tests(self) -> int:
        return sum(1 for r in self.results if r.success)
    
    @property
    def failed_tests(self) -> int:
        return self.total_tests - self.passed_tests
    
    @property
    def success_rate(self) -> float:
        return (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0.0
    
    @property
    def total_duration(self) -> float:
        return self.end_time - self.start_time if self.end_time > self.start_time else 0.0
    
    def add_result(self, result: TestResult) -> None:
        """Add a test result to the suite."""
        self.results.append(result)
    
    def get_failed_tests(self) -> List[TestResult]:
        """Get list of failed tests."""
        return [r for r in self.results if not r.success]
    
    def print_summary(self) -> None:
        """Print test suite summary."""
        print(f"\n📊 Test Suite: {self.name}")
        print("=" * 50)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {self.success_rate:.1f}%")
        print(f"Total Duration: {self.total_duration:.3f}s")
        
        if self.failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.get_failed_tests():
                print(f"  - {result.test_name}: {result.error_message}")


class BaseTest(ABC):
    """Base class for all tests."""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def run(self) -> TestResult:
        """Run the test and return result."""
        pass
    
    @contextmanager
    def measure_time(self):
        """Context manager to measure execution time."""
        start_time = time.time()
        yield
        end_time = time.time()
        self.duration = end_time - start_time
    
    def create_result(self, success: bool, error_message: Optional[str] = None, **details) -> TestResult:
        """Create a test result."""
        return TestResult(
            test_name=self.name,
            success=success,
            duration=getattr(self, 'duration', 0.0),
            error_message=error_message,
            details=details
        )


class VectorDatabaseTest(BaseTest):
    """Tests for vector database functionality."""
    
    def __init__(self):
        super().__init__("Vector Database Test")
    
    def run(self) -> TestResult:
        try:
            with self.measure_time():
                # Import here to handle missing dependencies gracefully
                try:
                    from vector_database import create_thai_vector_database
                except ImportError as e:
                    return self.create_result(False, f"Import error: {e}")
                
                # Create database
                db = create_thai_vector_database()
                
                # Test adding text
                test_text = "สวัสดีครับ นี่คือการทดสอบระบบ"
                success = db.add_text(test_text, {"category": "test"})
                if not success:
                    return self.create_result(False, "Failed to add text")
                
                # Test search
                results = db.search("สวัสดี", k=1)
                if not results:
                    return self.create_result(False, "Search returned no results")
                
                # Test stats
                stats = db.get_stats()
                if stats.total_entries != 1:
                    return self.create_result(False, f"Expected 1 entry, got {stats.total_entries}")
                
                return self.create_result(
                    True, 
                    db_size=stats.total_entries,
                    vector_dim=stats.vector_dimension
                )
                
        except Exception as e:
            return self.create_result(False, str(e))


class LLMClientTest(BaseTest):
    """Tests for LLM client functionality."""
    
    def __init__(self):
        super().__init__("LLM Client Test")
    
    def run(self) -> TestResult:
        try:
            with self.measure_time():
                try:
                    from llm_client_refactored import create_llm_client
                except ImportError as e:
                    return self.create_result(False, f"Import error: {e}")
                
                # Test mock client
                client = create_llm_client("mock")
                
                # Test connection
                if not client.test_connection():
                    return self.create_result(False, "Connection test failed")
                
                # Test generation
                response = client.generate("สวัสดี")
                if not response:
                    return self.create_result(False, "Generation returned empty response")
                
                return self.create_result(
                    True,
                    client_type="mock",
                    response_length=len(response)
                )
                
        except Exception as e:
            return self.create_result(False, str(e))


class RAGSystemTest(BaseTest):
    """Tests for RAG system functionality."""
    
    def __init__(self):
        super().__init__("RAG System Test")
    
    def run(self) -> TestResult:
        try:
            with self.measure_time():
                try:
                    from vector_database import create_thai_vector_database
                    from llm_client_refactored import create_llm_client
                    from rag_system_refactored import create_thai_rag_system
                except ImportError as e:
                    return self.create_result(False, f"Import error: {e}")
                
                # Create components
                db = create_thai_vector_database()
                llm_client = create_llm_client("mock")
                rag_system = create_thai_rag_system(db, llm_client)
                
                # Add test data
                test_texts = [
                    "โรงพยาบาลเปิดตลอด 24 ชั่วโมง",
                    "แผนกฉุกเฉินให้บริการทุกวัน",
                    "การรักษาโรคหัวใจ"
                ]
                
                for text in test_texts:
                    db.add_text(text, {"category": "healthcare"})
                
                # Test question answering
                response = rag_system.answer_question("โรงพยาบาลเปิดกี่โมง")
                
                if not response.answer:
                    return self.create_result(False, "No answer generated")
                
                return self.create_result(
                    True,
                    confidence=response.confidence,
                    sources_count=len(response.sources),
                    processing_time=response.processing_time
                )
                
        except Exception as e:
            return self.create_result(False, str(e))


class DataManagerTest(BaseTest):
    """Tests for data manager functionality."""
    
    def __init__(self):
        super().__init__("Data Manager Test")
    
    def run(self) -> TestResult:
        try:
            with self.measure_time():
                try:
                    from data_manager_refactored import create_data_importer, TextProcessor
                except ImportError as e:
                    return self.create_result(False, f"Import error: {e}")
                
                # Test text processor
                processor = TextProcessor()
                
                # Test text cleaning
                dirty_text = "  สวัสดี\t\tครับ  \n\n\nยินดีที่ได้รู้จัก  "
                cleaned = processor.clean_text(dirty_text)
                
                if not cleaned or "สวัสดี" not in cleaned:
                    return self.create_result(False, "Text cleaning failed")
                
                # Test chunking
                long_text = "สวัสดี " * 100
                chunks = processor.split_into_chunks(long_text, chunk_size=50)
                
                if not chunks:
                    return self.create_result(False, "Text chunking failed")
                
                # Test language detection
                thai_text = "สวัสดีครับ ยินดีที่ได้รู้จัก"
                language = processor.detect_language(thai_text)
                
                if language != "thai":
                    return self.create_result(False, f"Expected 'thai', got '{language}'")
                
                return self.create_result(
                    True,
                    chunks_created=len(chunks),
                    detected_language=language
                )
                
        except Exception as e:
            return self.create_result(False, str(e))


class ConfigSystemTest(BaseTest):
    """Tests for configuration system."""
    
    def __init__(self):
        super().__init__("Configuration System Test")
    
    def run(self) -> TestResult:
        try:
            with self.measure_time():
                try:
                    from config_system import ConfigurationManager, ApplicationConfig
                except ImportError as e:
                    return self.create_result(False, f"Import error: {e}")
                
                # Create config manager
                config_manager = ConfigurationManager()
                
                # Load default config
                config = config_manager.load_config()
                
                if not isinstance(config, ApplicationConfig):
                    return self.create_result(False, "Failed to load configuration")
                
                # Test configuration updates
                original_temp = config.llm.temperature
                config_manager.update_config({"llm": {"temperature": 0.9}})
                
                if config_manager.get_config_value("llm.temperature") != 0.9:
                    return self.create_result(False, "Configuration update failed")
                
                # Test validation
                try:
                    config_manager.update_config({"rag": {"default_top_k": -1}})
                    return self.create_result(False, "Validation should have failed")
                except ValueError:
                    pass  # Expected
                
                return self.create_result(
                    True,
                    original_temperature=original_temp,
                    updated_temperature=0.9
                )
                
        except Exception as e:
            return self.create_result(False, str(e))


class PerformanceTest(BaseTest):
    """Performance benchmark tests."""
    
    def __init__(self):
        super().__init__("Performance Benchmark")
    
    def run(self) -> TestResult:
        try:
            with self.measure_time():
                try:
                    from vector_database import create_thai_vector_database
                except ImportError as e:
                    return self.create_result(False, f"Import error: {e}")
                
                # Create database
                db = create_thai_vector_database()
                
                # Benchmark text addition
                start_time = time.time()
                for i in range(100):
                    db.add_text(f"ข้อความทดสอบ {i}", {"id": i})
                add_time = time.time() - start_time
                
                # Benchmark search
                start_time = time.time()
                for i in range(10):
                    results = db.search("ข้อความ", k=5)
                search_time = time.time() - start_time
                
                avg_add_time = add_time / 100
                avg_search_time = search_time / 10
                
                return self.create_result(
                    True,
                    avg_add_time_ms=avg_add_time * 1000,
                    avg_search_time_ms=avg_search_time * 1000,
                    total_entries=db.size()
                )
                
        except Exception as e:
            return self.create_result(False, str(e))


class TestRunner:
    """Main test runner."""
    
    def __init__(self):
        self.test_suites: List[TestSuite] = []
    
    def run_all_tests(self) -> List[TestSuite]:
        """Run all available tests."""
        
        # Define test categories
        test_categories = [
            ("Core Components", [
                VectorDatabaseTest(),
                LLMClientTest(),
                RAGSystemTest(),
                DataManagerTest(),
                ConfigSystemTest()
            ]),
            ("Performance", [
                PerformanceTest()
            ])
        ]
        
        for category_name, tests in test_categories:
            suite = self.run_test_suite(category_name, tests)
            self.test_suites.append(suite)
        
        return self.test_suites
    
    def run_test_suite(self, name: str, tests: List[BaseTest]) -> TestSuite:
        """Run a suite of tests."""
        suite = TestSuite(name)
        suite.start_time = time.time()
        
        print(f"\n🧪 Running {name} Tests...")
        print("-" * 40)
        
        for test in tests:
            print(f"Running {test.name}...", end=" ")
            result = test.run()
            suite.add_result(result)
            
            if result.success:
                print("✅")
            else:
                print(f"❌ {result.error_message}")
        
        suite.end_time = time.time()
        return suite
    
    def print_overall_summary(self) -> None:
        """Print overall test summary."""
        print("\n" + "=" * 60)
        print("📋 OVERALL TEST SUMMARY")
        print("=" * 60)
        
        total_tests = sum(suite.total_tests for suite in self.test_suites)
        total_passed = sum(suite.passed_tests for suite in self.test_suites)
        total_failed = total_tests - total_passed
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0.0
        
        print(f"Total Test Suites: {len(self.test_suites)}")
        print(f"Total Tests: {total_tests}")
        print(f"Total Passed: {total_passed}")
        print(f"Total Failed: {total_failed}")
        print(f"Overall Success Rate: {overall_success_rate:.1f}%")
        
        # Print individual suite summaries
        for suite in self.test_suites:
            suite.print_summary()
        
        # Exit with appropriate code
        if total_failed > 0:
            print(f"\n❌ {total_failed} tests failed!")
            return False
        else:
            print(f"\n✅ All {total_tests} tests passed!")
            return True


def main():
    """Main function to run all tests."""
    print("🚀 Starting Healthcare-AI System Tests")
    print("=" * 60)
    
    runner = TestRunner()
    runner.run_all_tests()
    success = runner.print_overall_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
