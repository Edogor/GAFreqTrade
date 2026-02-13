#!/usr/bin/env python3
"""
Test Docker Setup for GAFreqTrade

This script tests whether Docker mode is properly configured for Freqtrade backtesting.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import subprocess
from pathlib import Path

def test_docker_available():
    """Test if Docker is available"""
    print("=" * 60)
    print("Testing Docker availability...")
    print("=" * 60)
    
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print(f"✓ Docker found: {result.stdout.strip()}")
            return True
        else:
            print("✗ Docker command failed")
            return False
    except FileNotFoundError:
        print("✗ Docker not found. Please install Docker.")
        return False
    except Exception as e:
        print(f"✗ Error checking Docker: {e}")
        return False

def test_freqtrade_image():
    """Test if Freqtrade Docker image is available"""
    print("\n" + "=" * 60)
    print("Testing Freqtrade Docker image...")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', 'freqtradeorg/freqtrade:stable', '--version'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            version_output = result.stdout.strip() if result.stdout else result.stderr.strip()
            print(f"✓ Freqtrade image works: {version_output}")
            return True
        else:
            print("✗ Freqtrade image test failed")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error testing Freqtrade image: {e}")
        print("\nTry pulling the image manually:")
        print("  docker pull freqtradeorg/freqtrade:stable")
        return False

def test_user_data_directory():
    """Test if user_data directory exists"""
    print("\n" + "=" * 60)
    print("Testing user_data directory...")
    print("=" * 60)
    
    user_data_path = Path("freqtrade/user_data")
    
    if not user_data_path.exists():
        print(f"✗ Directory not found: {user_data_path}")
        print("\nCreate it with:")
        print(f"  mkdir -p {user_data_path}")
        return False
    
    # Check subdirectories
    required_dirs = ['strategies', 'data']
    missing_dirs = []
    
    for dir_name in required_dirs:
        dir_path = user_data_path / dir_name
        if dir_path.exists():
            print(f"✓ Found: {dir_path}")
        else:
            print(f"⚠ Missing: {dir_path} (will be created automatically)")
            missing_dirs.append(dir_path)
    
    # Check config file
    config_path = user_data_path / "config.json"
    if config_path.exists():
        print(f"✓ Config found: {config_path}")
    else:
        print(f"⚠ Config not found: {config_path}")
        print("  You'll need to create this file with your Freqtrade configuration")
    
    return True

def test_docker_mount():
    """Test if Docker can mount the user_data directory"""
    print("\n" + "=" * 60)
    print("Testing Docker volume mount...")
    print("=" * 60)
    
    user_data_path = Path("freqtrade/user_data").absolute()
    
    try:
        # Try to mount and list directory
        result = subprocess.run(
            ['docker', 'run', '--rm',
             '-v', f'{user_data_path}:/freqtrade/user_data',
             'freqtradeorg/freqtrade:stable',
             'ls', '-la', '/freqtrade/user_data'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("✓ Docker can mount user_data directory")
            print("\nDirectory contents:")
            print(result.stdout)
            return True
        else:
            print("✗ Failed to mount directory")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"✗ Error testing mount: {e}")
        return False

def test_backtester_config():
    """Test if the backtester can be initialized with Docker"""
    print("\n" + "=" * 60)
    print("Testing Backtester with Docker configuration...")
    print("=" * 60)
    
    try:
        from evaluation.backtester import Backtester
        
        backtester = Backtester(
            use_docker=True,
            docker_image="freqtradeorg/freqtrade:stable",
            docker_user_data_path="./freqtrade/user_data"
        )
        
        print("✓ Backtester initialized successfully with Docker mode")
        return True
        
    except Exception as e:
        print(f"✗ Error initializing Backtester: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║           GAFreqTrade Docker Setup Test                  ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print("\n")
    
    tests = [
        ("Docker Installation", test_docker_available),
        ("Freqtrade Image", test_freqtrade_image),
        ("User Data Directory", test_user_data_directory),
        ("Docker Volume Mount", test_docker_mount),
        ("Backtester Configuration", test_backtester_config),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Docker mode is ready to use.")
        print("\nTo use Docker mode, ensure config/eval_config.yaml has:")
        print("  use_docker: true")
        print("\nThen run:")
        print("  python run_evolution.py --no-mock --generations 4 --population 10")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        print("\nQuick fixes:")
        print("  - Install Docker: https://docs.docker.com/get-docker/")
        print("  - Pull image: docker pull freqtradeorg/freqtrade:stable")
        print("  - Create directories: mkdir -p freqtrade/user_data/{data,strategies}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
