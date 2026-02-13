#!/usr/bin/env python3
"""
Test runner script for GAFreqTrade.
Provides convenient commands for running different test suites.
"""
import sys
import subprocess
import argparse


def run_command(cmd):
    """Run a command and return the exit code."""
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description="GAFreqTrade Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --all              # Run all tests
  python run_tests.py --unit             # Run unit tests only
  python run_tests.py --integration      # Run integration tests only
  python run_tests.py --fast             # Run fast tests (skip slow)
  python run_tests.py --coverage         # Run with coverage report
  python run_tests.py --module genetic_ops  # Run specific module tests
        """
    )
    
    parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Run all tests'
    )
    
    parser.add_argument(
        '--unit', '-u',
        action='store_true',
        help='Run unit tests only'
    )
    
    parser.add_argument(
        '--integration', '-i',
        action='store_true',
        help='Run integration tests only'
    )
    
    parser.add_argument(
        '--fast', '-f',
        action='store_true',
        help='Run fast tests (exclude slow tests)'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run tests with coverage report'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--module', '-m',
        type=str,
        help='Run tests for specific module (e.g., genetic_ops, fitness)'
    )
    
    parser.add_argument(
        '--marker',
        type=str,
        help='Run tests with specific marker (e.g., mock, slow)'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML coverage report'
    )
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ['pytest']
    
    # Add verbosity
    if args.verbose:
        cmd.append('-v')
    
    # Add coverage options
    if args.coverage or args.html:
        cmd.extend([
            '--cov=ga_core',
            '--cov=evaluation',
            '--cov=orchestration',
            '--cov=storage',
            '--cov=utils',
            '--cov-report=term-missing'
        ])
        
        if args.html:
            cmd.append('--cov-report=html')
    
    # Add test selection
    if args.unit:
        cmd.append('tests/unit/')
    elif args.integration:
        cmd.append('tests/integration/')
    elif args.module:
        cmd.append(f'tests/unit/test_{args.module}.py')
    elif args.all or not any([args.unit, args.integration, args.fast, args.marker, args.module]):
        cmd.append('tests/')
    
    # Add markers
    if args.fast:
        cmd.extend(['-m', 'not slow'])
    
    if args.marker:
        cmd.extend(['-m', args.marker])
    
    # Run the tests
    exit_code = run_command(cmd)
    
    # Print summary
    print("\n" + "="*60)
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("="*60 + "\n")
    
    if args.html:
        print("📊 HTML coverage report generated in: htmlcov/index.html\n")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
