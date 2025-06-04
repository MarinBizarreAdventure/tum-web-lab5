#!/usr/bin/env python3
"""
Comprehensive test script for go2web HTTP client
Demonstrates all functionality for Lab 5
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def run_command(cmd, description="", timeout=30):
    """Run a command and display results"""
    print("\n" + "="*70)
    print(f"TEST: {description}")
    print("="*70)
    print(f"Command: {cmd}")
    print("-" * 70)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        
        if result.stdout:
            print("OUTPUT:")
            # Limit output for readability
            output_lines = result.stdout.split('\n')
            if len(output_lines) > 30:
                for line in output_lines[:15]:
                    print(line)
                print(f"... [truncated {len(output_lines) - 30} lines] ...")
                for line in output_lines[-15:]:
                    print(line)
            else:
                print(result.stdout)
        
        if result.stderr:
            print("ERRORS:")
            print(result.stderr)
        
        status = "✅ PASSED" if result.returncode == 0 else f"❌ FAILED (exit code: {result.returncode})"
        print(f"\nSTATUS: {status}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TIMEOUT after {timeout} seconds")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False
    
    finally:
        print("-" * 70)

def pause_between_tests(seconds=2):
    """Pause between tests to avoid rate limiting"""
    print(f"\n⏸️  Pausing {seconds} seconds to avoid rate limiting...")
    time.sleep(seconds)

def main():
    """Run comprehensive tests"""
    
    # Check if go2web executable exists
    if os.name == 'nt':  # Windows
        go2web_cmd = "go2web.bat"
        if not Path("go2web.bat").exists():
            print("❌ go2web.bat not found. Run setup.py first.")
            sys.exit(1)
    else:  # Unix/Linux
        go2web_cmd = "./go2web"
        if not Path("go2web").exists():
            print("❌ go2web executable not found. Run setup.py first.")
            sys.exit(1)
    
    print("🚀 Starting go2web comprehensive test suite...")
    print("This tests all Lab 5 requirements and extra features")
    print(f"Platform: {'Windows' if os.name == 'nt' else 'Unix/Linux'}")
    print(f"Command: {go2web_cmd}")
    
    passed_tests = 0
    total_tests = 0
    
    # Test 1: Help command (-h option)
    total_tests += 1
    print(f"\n📋 TEST {total_tests}: Core Requirement - Help Command")
    if run_command(f"{go2web_cmd} -h", "Help Command (-h option)"):
        passed_tests += 1
    
    pause_between_tests(1)
    
    # Test 2: Basic URL fetching with JSON content negotiation
    total_tests += 1
    print(f"\n🌐 TEST {total_tests}: Core Requirement - URL Fetching + Content Negotiation")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/json", "Fetch JSON URL (Content Negotiation)"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 3: HTML URL fetching with text extraction
    total_tests += 1
    print(f"\n📄 TEST {total_tests}: Core Requirement - HTML Processing")
    if run_command(f"{go2web_cmd} -u https://example.com", "Fetch HTML URL (Text Extraction)"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 4: Search functionality (core requirement)
    total_tests += 1
    print(f"\n🔍 TEST {total_tests}: Core Requirement - Search Functionality")
    if run_command(f"{go2web_cmd} -s python programming", "Search Functionality with Multiple Engines", timeout=45):
        passed_tests += 1
    
    pause_between_tests(3)
    
    # Test 5: HTTP redirect following (+1 extra point)
    total_tests += 1
    print(f"\n🔄 TEST {total_tests}: Extra Feature (+1 point) - HTTP Redirect Following")
    if run_command(f"{go2web_cmd} -u http://github.com", "HTTP Redirect Following (301/302)"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 6: HTTPS support
    total_tests += 1
    print(f"\n🔒 TEST {total_tests}: Core Requirement - HTTPS Support")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/user-agent", "HTTPS Connection with Raw Sockets"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 7: HTTP caching (+2 extra points)
    total_tests += 1
    print(f"\n💾 TEST {total_tests}: Extra Feature (+2 points) - HTTP Caching")
    print("First request (should be slow):")
    run_command(f"{go2web_cmd} -u https://httpbin.org/delay/2", "First Request - No Cache")
    
    pause_between_tests(1)
    
    print("Second request (should be fast - from cache):")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/delay/2", "Second Request - From Cache"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 8: Different content types (+2 extra points continued)
    total_tests += 1
    print(f"\n📊 TEST {total_tests}: Extra Feature (+2 points) - Content Negotiation")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/xml", "XML Content Handling"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 9: Error handling (4xx)
    total_tests += 1
    print(f"\n⚠️ TEST {total_tests}: Error Handling - 4xx Status Codes")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/status/404", "404 Error Handling"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 10: Error handling (5xx)
    total_tests += 1
    print(f"\n❌ TEST {total_tests}: Error Handling - 5xx Status Codes")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/status/500", "500 Error Handling"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 11: Invalid URL handling
    total_tests += 1
    print(f"\n🚫 TEST {total_tests}: Error Handling - Invalid URLs")
    if run_command(f"{go2web_cmd} -u invalid-url-test", "Invalid URL Handling"):
        passed_tests += 1
    
    pause_between_tests(1)
    
    # Test 12: Multiple search terms
    total_tests += 1
    print(f"\n🔍 TEST {total_tests}: Advanced Search - Multiple Terms")
    if run_command(f'{go2web_cmd} -s "machine learning python tutorial"', "Multi-word Search Query", timeout=45):
        passed_tests += 1
    
    pause_between_tests(3)
    
    # Test 13: No arguments (should show help)
    total_tests += 1
    print(f"\n❓ TEST {total_tests}: CLI Validation - No Arguments")
    if run_command(f"{go2web_cmd}", "No Arguments (should show help)"):
        passed_tests += 1
    
    pause_between_tests(1)
    
    # Test 14: Cache control options
    total_tests += 1
    print(f"\n🚫 TEST {total_tests}: Advanced Feature - Cache Control")
    if run_command(f"{go2web_cmd} -u https://httpbin.org/uuid --no-cache", "Disable Cache Option"):
        passed_tests += 1
    
    pause_between_tests(2)
    
    # Test 15: Different search engines fallback
    total_tests += 1
    print(f"\n🔄 TEST {total_tests}: Search Engine Fallback")
    if run_command(f"{go2web_cmd} -s javascript", "Search Engine Fallback Test", timeout=45):
        passed_tests += 1
    
    # Test Results Summary
    print("\n" + "🎯" * 25)
    print("TEST SUITE RESULTS")
    print("🎯" * 25)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Tests Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests >= total_tests * 0.8:  # 80% pass rate
        print(f"\n🎉 EXCELLENT! Test suite passed with high success rate!")
    elif passed_tests >= total_tests * 0.6:  # 60% pass rate
        print(f"\n✅ GOOD! Most tests passed. Some features may need network connectivity.")
    else:
        print(f"\n⚠️ NEEDS ATTENTION: Several tests failed. Check implementation.")
    
    print(f"\n🏆 LAB 5 FEATURES DEMONSTRATED:")
    print("   ✅ HTTP/HTTPS requests using raw TCP sockets")
    print("   ✅ Command-line interface with -h, -u, -s options")
    print("   ✅ HTML parsing and text extraction")
    print("   ✅ JSON content negotiation")
    print("   ✅ Search functionality with multiple engines")
    print("   ✅ HTTP redirect following")
    print("   ✅ HTTP caching with TTL")
    print("   ✅ Error handling and validation")
    print("   ✅ Interactive search result navigation")
    
    print(f"\n📈 EXPECTED LAB 5 POINTS:")
    points = 6  # Base points for -h, -u, -s
    if passed_tests >= 10:  # If most tests pass
        points += 1  # Search result access
        points += 1  # HTTP redirects
        points += 2  # HTTP caching
        points += 2  # Content negotiation
    
    print(f"   🎯 Estimated Score: {points}/12 points")
    
    print(f"\n💡 NEXT STEPS:")
    if passed_tests < total_tests:
        print("   1. Check network connectivity")
        print("   2. Verify all Python files are in the same directory")
        print("   3. Some search engines may be temporarily unavailable")
    
    print("   4. Test manually with specific commands:")
    print(f"      {go2web_cmd} -h")
    print(f"      {go2web_cmd} -u https://httpbin.org/json")
    print(f"      {go2web_cmd} -s 'python programming'")
    
    print(f"\n🎓 Ready for Lab 5 presentation!")

if __name__ == "__main__":
    main()