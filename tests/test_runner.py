"""
Comprehensive test runner for the Word Formatter system.
Provides organized test execution with detailed reporting.
"""

import os
import sys
import pytest
import time
from pathlib import Path
from typing import Dict, List, Optional


class TestRunner:
    """Comprehensive test runner with organized test suites."""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.results = {}
        
    def run_unit_tests(self, verbose: bool = True) -> Dict:
        """Run all unit tests."""
        print("=" * 80)
        print("RUNNING UNIT TESTS")
        print("=" * 80)
        
        unit_args = [
            str(self.test_dir / "unit"),
            "-v" if verbose else "",
            "-m", "unit",
            "--tb=short",
            "--durations=5"
        ]
        unit_args = [arg for arg in unit_args if arg]  # Remove empty strings
        
        start_time = time.time()
        result = pytest.main(unit_args)
        end_time = time.time()
        
        self.results['unit'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nUnit tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['unit']['status']}")
        
        return self.results['unit']
    
    def run_integration_tests(self, verbose: bool = True) -> Dict:
        """Run all integration tests."""
        print("\n" + "=" * 80)
        print("RUNNING INTEGRATION TESTS")
        print("=" * 80)
        
        integration_args = [
            str(self.test_dir / "integration"),
            "-v" if verbose else "",
            "-m", "integration",
            "--tb=short",
            "--durations=5"
        ]
        integration_args = [arg for arg in integration_args if arg]
        
        start_time = time.time()
        result = pytest.main(integration_args)
        end_time = time.time()
        
        self.results['integration'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nIntegration tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['integration']['status']}")
        
        return self.results['integration']
    
    def run_performance_tests(self, verbose: bool = True) -> Dict:
        """Run performance tests."""
        print("\n" + "=" * 80)
        print("RUNNING PERFORMANCE TESTS")
        print("=" * 80)
        
        perf_args = [
            str(self.test_dir / "test_performance.py"),
            "-v" if verbose else "",
            "-m", "performance",
            "--tb=short",
            "--durations=10"
        ]
        perf_args = [arg for arg in perf_args if arg]
        
        start_time = time.time()
        result = pytest.main(perf_args)
        end_time = time.time()
        
        self.results['performance'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nPerformance tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['performance']['status']}")
        
        return self.results['performance']
    
    def run_edge_case_tests(self, verbose: bool = True) -> Dict:
        """Run edge case tests."""
        print("\n" + "=" * 80)
        print("RUNNING EDGE CASE TESTS")
        print("=" * 80)
        
        edge_args = [
            str(self.test_dir / "test_edge_cases.py"),
            "-v" if verbose else "",
            "--tb=short",
            "--durations=5"
        ]
        edge_args = [arg for arg in edge_args if arg]
        
        start_time = time.time()
        result = pytest.main(edge_args)
        end_time = time.time()
        
        self.results['edge_cases'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nEdge case tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['edge_cases']['status']}")
        
        return self.results['edge_cases']
    
    def run_claude_tests(self, verbose: bool = True) -> Dict:
        """Run tests specific to Claude AI integration."""
        print("\n" + "=" * 80)
        print("RUNNING CLAUDE AI INTEGRATION TESTS")
        print("=" * 80)
        
        claude_args = [
            str(self.test_dir),
            "-v" if verbose else "",
            "-m", "claude",
            "--tb=short",
            "--durations=5"
        ]
        claude_args = [arg for arg in claude_args if arg]
        
        start_time = time.time()
        result = pytest.main(claude_args)
        end_time = time.time()
        
        self.results['claude'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nClaude AI tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['claude']['status']}")
        
        return self.results['claude']
    
    def run_slow_tests(self, verbose: bool = True) -> Dict:
        """Run slow tests (performance and large file tests)."""
        print("\n" + "=" * 80)
        print("RUNNING SLOW TESTS")
        print("=" * 80)
        print("WARNING: These tests may take several minutes to complete.")
        
        slow_args = [
            str(self.test_dir),
            "-v" if verbose else "",
            "-m", "slow",
            "--tb=short",
            "--durations=10"
        ]
        slow_args = [arg for arg in slow_args if arg]
        
        start_time = time.time()
        result = pytest.main(slow_args)
        end_time = time.time()
        
        self.results['slow'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nSlow tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['slow']['status']}")
        
        return self.results['slow']
    
    def run_coverage_tests(self) -> Dict:
        """Run tests with coverage reporting."""
        print("\n" + "=" * 80)
        print("RUNNING COVERAGE ANALYSIS")
        print("=" * 80)
        
        coverage_args = [
            str(self.test_dir),
            "--cov=document_converter",
            "--cov=document_converter_ai",
            "--cov=document_converter_simple",
            "--cov-report=term-missing",
            "--cov-report=html:tests/coverage_html",
            "--cov-fail-under=75",
            "-x"  # Stop on first failure for faster feedback
        ]
        
        start_time = time.time()
        result = pytest.main(coverage_args)
        end_time = time.time()
        
        self.results['coverage'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        coverage_html_path = self.test_dir / "coverage_html" / "index.html"
        if coverage_html_path.exists():
            print(f"\nCoverage HTML report available at: {coverage_html_path}")
        
        print(f"\nCoverage analysis completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['coverage']['status']}")
        
        return self.results['coverage']
    
    def run_quick_tests(self) -> Dict:
        """Run a quick subset of tests for rapid feedback."""
        print("=" * 80)
        print("RUNNING QUICK TEST SUITE")
        print("=" * 80)
        print("Running essential tests for rapid feedback...")
        
        quick_args = [
            str(self.test_dir),
            "-x",  # Stop on first failure
            "--tb=short",
            "-q",  # Quiet mode
            "-m", "not slow and not performance",  # Exclude slow tests
            "--durations=3"
        ]
        
        start_time = time.time()
        result = pytest.main(quick_args)
        end_time = time.time()
        
        self.results['quick'] = {
            'exit_code': result,
            'duration': end_time - start_time,
            'status': 'PASSED' if result == 0 else 'FAILED'
        }
        
        print(f"\nQuick tests completed in {end_time - start_time:.2f} seconds")
        print(f"Status: {self.results['quick']['status']}")
        
        return self.results['quick']
    
    def run_all_tests(self, include_slow: bool = False, verbose: bool = True) -> Dict:
        """Run complete test suite."""
        print("=" * 80)
        print("RUNNING COMPLETE TEST SUITE")
        print("=" * 80)
        
        total_start_time = time.time()
        
        # Run test suites in order
        self.run_unit_tests(verbose)
        self.run_integration_tests(verbose)
        self.run_edge_case_tests(verbose)
        self.run_claude_tests(verbose)
        
        if include_slow:
            self.run_performance_tests(verbose)
            self.run_slow_tests(verbose)
        
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # Summary
        print("\n" + "=" * 80)
        print("TEST SUITE SUMMARY")
        print("=" * 80)
        
        passed_suites = 0
        total_suites = 0
        
        for suite_name, result in self.results.items():
            if suite_name != 'summary':
                total_suites += 1
                if result['status'] == 'PASSED':
                    passed_suites += 1
                
                status_symbol = "✓" if result['status'] == 'PASSED' else "✗"
                print(f"{status_symbol} {suite_name.upper()}: {result['status']} ({result['duration']:.2f}s)")
        
        overall_status = 'PASSED' if passed_suites == total_suites else 'FAILED'
        print(f"\nOVERALL: {overall_status} ({passed_suites}/{total_suites} test suites passed)")
        print(f"Total execution time: {total_duration:.2f} seconds")
        
        self.results['summary'] = {
            'overall_status': overall_status,
            'passed_suites': passed_suites,
            'total_suites': total_suites,
            'total_duration': total_duration
        }
        
        return self.results
    
    def validate_test_environment(self) -> bool:
        """Validate that the test environment is properly set up."""
        print("Validating test environment...")
        
        # Check required files exist
        required_files = [
            self.project_root / "document_converter.py",
            self.project_root / "document_converter_ai.py", 
            self.project_root / "document_converter_simple.py",
            self.test_dir / "conftest.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not file_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print("ERROR: Missing required files:")
            for file_path in missing_files:
                print(f"  - {file_path}")
            return False
        
        # Check Python path includes project root
        if str(self.project_root) not in sys.path:
            sys.path.insert(0, str(self.project_root))
        
        # Try importing main modules
        try:
            from document_converter import DocumentConverter, StyleExtractor
            from document_converter_ai import AIDocumentConverter
            print("✓ All required modules can be imported")
        except ImportError as e:
            print(f"ERROR: Cannot import required modules: {e}")
            return False
        
        print("✓ Test environment validation passed")
        return True


def main():
    """Main entry point for the test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Word Formatter Test Runner")
    parser.add_argument("--suite", choices=[
        "unit", "integration", "performance", "edge", "claude", "slow", "coverage", "quick", "all"
    ], default="quick", help="Test suite to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--include-slow", action="store_true", help="Include slow tests in 'all' suite")
    parser.add_argument("--validate-only", action="store_true", help="Only validate test environment")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Validate environment
    if not runner.validate_test_environment():
        print("Test environment validation failed!")
        sys.exit(1)
    
    if args.validate_only:
        print("Test environment validation successful!")
        sys.exit(0)
    
    # Run selected test suite
    if args.suite == "unit":
        result = runner.run_unit_tests(args.verbose)
    elif args.suite == "integration":
        result = runner.run_integration_tests(args.verbose)
    elif args.suite == "performance":
        result = runner.run_performance_tests(args.verbose)
    elif args.suite == "edge":
        result = runner.run_edge_case_tests(args.verbose)
    elif args.suite == "claude":
        result = runner.run_claude_tests(args.verbose)
    elif args.suite == "slow":
        result = runner.run_slow_tests(args.verbose)
    elif args.suite == "coverage":
        result = runner.run_coverage_tests()
    elif args.suite == "quick":
        result = runner.run_quick_tests()
    elif args.suite == "all":
        result = runner.run_all_tests(args.include_slow, args.verbose)
    
    # Exit with appropriate code
    if args.suite == "all":
        exit_code = 0 if result['summary']['overall_status'] == 'PASSED' else 1
    else:
        exit_code = result['exit_code']
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()