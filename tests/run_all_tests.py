import os
import sys
import unittest
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run_test_suite():
    print("=" * 60)
    print("           PY-FTL AUTOMATED TEST SUITE RUNNER")
    print("=" * 60)
    start_time = time.time()

    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    elapsed = time.time() - start_time
    print("=" * 60)
    print(f"TEST SUMMARY:")
    print(f"  Tests Ran   : {result.testsRun}")
    print(f"  Failures    : {len(result.failures)}")
    print(f"  Errors      : {len(result.errors)}")
    print(f"  Time Taken  : {elapsed:.3f}s")
    print("=" * 60)

    if result.wasSuccessful():
        print("RESULT: ALL TESTS PASSED SUCCESSFULLY! [100% OK]")
        return 0
    else:
        print("RESULT: SOME TESTS FAILED!")
        return 1


if __name__ == "__main__":
    sys.exit(run_test_suite())
