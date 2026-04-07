"""
Master test runner - executes all validation tests.

This script runs all OpenEnv compliance tests in sequence and reports results.
"""

import subprocess
import sys


def run_test(test_name, test_file):
    """Run a single test and return success status."""
    print("\n" + "=" * 70)
    print(f"Running: {test_name}")
    print("=" * 70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=False,
            text=True,
            check=True
        )
        print(f"\n✅ {test_name} PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_name} FAILED")
        return False


def main():
    """Run all tests and report final status."""
    print("\n" + "=" * 70)
    print(" " * 20 + "RUNNING ALL VALIDATION TESTS")
    print("=" * 70)
    
    tests = [
        ("Async Interface Test", "test_async_env.py"),
        ("Log Format Test", "test_log_format.py"),
        ("OpenEnv Compliance Test", "test_openenv_compliance.py"),
    ]
    
    results = []
    for test_name, test_file in tests:
        success = run_test(test_name, test_file)
        results.append((test_name, success))
    
    # Final summary
    print("\n" + "=" * 70)
    print(" " * 25 + "FINAL SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}  {test_name}")
    
    print("\n" + "=" * 70)
    print(f" " * 20 + f"RESULTS: {passed}/{total} TESTS PASSED")
    print("=" * 70)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - ENVIRONMENT IS SUBMISSION READY! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
