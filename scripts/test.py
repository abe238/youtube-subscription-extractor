#!/usr/bin/env python3
"""
Installation verification script for YouTube Subscription Extractor
"""

import sys
import os
import subprocess
from pathlib import Path

def test_python_version():
    """Test if Python version is compatible"""
    print("🔍 Testing Python version...")
    
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is not compatible (3.7+ required)")
        return False

def test_extract_script():
    """Test if the extract script is accessible and executable"""
    print("🔍 Testing extract script...")
    
    script_path = Path(__file__).parent.parent / "bin" / "extract.py"
    
    if not script_path.exists():
        print(f"❌ Extract script not found at {script_path}")
        return False
    
    # Test help command
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("✅ Extract script help command works")
            return True
        else:
            print(f"❌ Extract script help command failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Extract script help command timed out")
        return False
    except Exception as e:
        print(f"❌ Error testing extract script: {e}")
        return False

def test_import_dependencies():
    """Test if all required modules can be imported"""
    print("🔍 Testing Python module imports...")
    
    required_modules = [
        're', 'csv', 'html', 'argparse', 'sys', 'os', 'pathlib', 'urllib.parse'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            failed_imports.append(module)
    
    if not failed_imports:
        print(f"✅ All {len(required_modules)} required modules available")
        return True
    else:
        print(f"❌ Failed to import modules: {', '.join(failed_imports)}")
        return False

def test_file_structure():
    """Test if all required files and directories exist"""
    print("🔍 Testing file structure...")
    
    base_path = Path(__file__).parent.parent
    
    required_files = [
        "bin/extract.py",
        "README.md",
        "requirements.txt",
        "setup.py"
    ]
    
    required_dirs = [
        "bin",
        "scripts"
    ]
    
    missing_files = []
    missing_dirs = []
    
    # Check files
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
    
    # Check directories
    for dir_path in required_dirs:
        full_path = base_path / dir_path
        if not full_path.is_dir():
            missing_dirs.append(dir_path)
    
    if not missing_files and not missing_dirs:
        print(f"✅ All required files and directories present")
        return True
    else:
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
        if missing_dirs:
            print(f"❌ Missing directories: {', '.join(missing_dirs)}")
        return False

def main():
    """Run all tests"""
    print("🧪 YouTube Subscription Extractor - Installation Test")
    print("=" * 55)
    
    tests = [
        ("Python Version", test_python_version),
        ("Import Dependencies", test_import_dependencies),
        ("File Structure", test_file_structure),
        ("Extract Script", test_extract_script),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        success = test_func()
        results.append((test_name, success))
    
    # Summary
    print("\n" + "=" * 55)
    print("📊 Test Summary")
    print("=" * 55)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Installation is successful.")
        print("\n📚 Quick Start:")
        print("   python bin/extract.py --help")
        print("   python bin/extract.py your_subscriptions.mhtml")
        return 0
    else:
        print("❌ Some tests failed. Please check the installation.")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Python 3.7+ is installed")
        print("   2. Run the installation script: ./scripts/install.sh")
        print("   3. Check file permissions")
        return 1

if __name__ == "__main__":
    sys.exit(main())