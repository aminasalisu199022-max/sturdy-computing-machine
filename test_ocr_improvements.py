#!/usr/bin/env python3
"""
Test suite for OCR improvements in Nigerian license plate recognition.

Tests the enhanced preprocessing pipeline and error correction logic.
"""

import sys
sys.path.insert(0, '/workspaces/sturdy-computing-machine')

from alpr_system.plate_validation_updated import (
    normalize_plate,
    is_valid_nigerian_plate,
    validate_and_format_plate,
    correct_ocr_errors
)


def test_normalize_plate():
    """Test the normalize_plate function with various inputs."""
    print("\n" + "="*70)
    print("TEST 1: normalize_plate() - Core Normalization Function")
    print("="*70)
    
    test_cases = [
        # (input, expected_output, description)
        ("KTS-123AB", "KTS-123AB", "Already correctly formatted"),
        ("kts-123ab", "KTS-123AB", "Lowercase input"),
        ("kts123ab", "KTS-123AB", "Missing hyphen"),
        ("KTS 123 AB", "KTS-123AB", "Spaces instead of hyphen"),
        ("k7s123ab", "K7S-123AB", "7 stays 7, s stays s"),
        ("k8s123ab", "KBS-123AB", "8→B conversion in letter position"),
        ("kts1o3ab", "KTS-103AB", "O→0 in digit section"),
        ("kts5o3ab", "KTS-503AB", "5→S in letter section, O→0 in digit section"),
        ("ABJ-456CD", "ABJ-456CD", "Valid plate example 2"),
        ("LAG-890EF", "LAG-890EF", "Valid plate example 3"),
        ("lag-8901f", "LAG-890IF", "Mixed errors with context"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = normalize_plate(input_text)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"{status}: {description}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


def test_ocr_error_correction():
    """Test context-aware OCR error correction."""
    print("\n" + "="*70)
    print("TEST 2: correct_ocr_errors() - Context-Aware Correction")
    print("="*70)
    
    test_cases = [
        # (input, expected, description)
        ("KTS-123AB", "KTS-123AB", "No errors"),
        ("K8S-123AB", "KBS-123AB", "8→B in letter position"),
        ("K00-123AB", "KOO-123AB", "0→O in letter position (prefix)"),
        ("KTS-123OB", "KTS-123OB", "O in letter position (suffix) - stays O, B in letter"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = correct_ocr_errors(input_text)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"{status}: {description}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


def test_validation():
    """Test plate format validation."""
    print("\n" + "="*70)
    print("TEST 3: is_valid_nigerian_plate() - Format Validation")
    print("="*70)
    
    test_cases = [
        # (input, expected_valid, description)
        ("KTS-123AB", True, "Valid format: KTS-123AB"),
        ("ABJ-456CD", True, "Valid format: ABJ-456CD"),
        ("LAG-890EF", True, "Valid format: LAG-890EF"),
        ("KTS123AB", False, "Missing hyphen"),
        ("KTS-123A", False, "Too short"),
        ("KTS-123ABC", False, "Too long"),
        ("12S-123AB", False, "Starts with digits"),
        ("KTS-12A-AB", False, "Extra hyphen"),
        ("KTS-ABC12", False, "Wrong position for letters/digits"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected_valid, description in test_cases:
        result = is_valid_nigerian_plate(input_text)
        status = "✓ PASS" if result == expected_valid else "✗ FAIL"
        if result == expected_valid:
            passed += 1
        else:
            failed += 1
        print(f"{status}: {description}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: {expected_valid}")
        print(f"  Got:      {result}")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


def test_full_pipeline():
    """Test the complete validation pipeline."""
    print("\n" + "="*70)
    print("TEST 4: validate_and_format_plate() - Full Pipeline")
    print("="*70)
    
    test_cases = [
        # (input, should_be_valid, expected_output, description)
        ("KTS-123AB", True, "KTS-123AB", "Already valid"),
        ("kts-123ab", True, "KTS-123AB", "Lowercase normalization"),
        ("kts123ab", True, "KTS-123AB", "Missing hyphen fix"),
        ("kts8o3ab", True, "KTS-803AB", "8→B in letter position, O→0 in digits"),
        ("KTS 123 AB", True, "KTS-123AB", "Space handling"),
        ("ABJ-456CD", True, "ABJ-456CD", "Valid example 2"),
        ("LAG-890EF", True, "LAG-890EF", "Valid example 3"),
        ("KTS12AB", False, None, "Invalid format (too short)"),
        ("INVALID", False, None, "Completely invalid"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected_valid, expected_output, description in test_cases:
        is_valid, formatted = validate_and_format_plate(input_text)
        
        validity_match = is_valid == expected_valid
        output_match = formatted == expected_output if expected_valid else not formatted
        overall_match = validity_match and output_match
        
        status = "✓ PASS" if overall_match else "✗ FAIL"
        if overall_match:
            passed += 1
        else:
            failed += 1
        
        print(f"{status}: {description}")
        print(f"  Input:           '{input_text}'")
        print(f"  Expected Valid:  {expected_valid}, Got: {is_valid}")
        print(f"  Expected Output: '{expected_output}', Got: '{formatted}'")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


def test_ocr_error_scenarios():
    """Test realistic OCR error scenarios."""
    print("\n" + "="*70)
    print("TEST 5: OCR Error Scenarios - Real-world Cases")
    print("="*70)
    
    # Common OCR errors when reading license plates
    test_cases = [
        # OCR mistakes with 5→S, 8→B, 0↔O (context-aware)
        ("kts5i3ab", "KTS-513AB", "5 in digit position stays 5, I→1 in digit position"),
        ("kts8o3ab", "KTS-803AB", "8 in digit position stays 8, O→0 in digit position"),
        ("kts1o3ab", "KTS-103AB", "O in digit section should be 0"),
        ("kts-i03ab", "KTS-103AB", "I in digit section should be 1"),
        ("lag-890ef", "LAG-890EF", "Valid plate - no OCR errors"),
    ]
    
    passed = 0
    failed = 0
    
    for input_text, expected, description in test_cases:
        result = normalize_plate(input_text)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        print(f"{status}: {description}")
        print(f"  Input:    '{input_text}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return failed == 0


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("ALPR SYSTEM - OCR IMPROVEMENTS TEST SUITE")
    print("Nigerian License Plate Recognition")
    print("="*70)
    
    results = []
    
    # Run all test suites
    results.append(("Normalize Plate", test_normalize_plate()))
    results.append(("OCR Error Correction", test_ocr_error_correction()))
    results.append(("Validation", test_validation()))
    results.append(("Full Pipeline", test_full_pipeline()))
    results.append(("OCR Error Scenarios", test_ocr_error_scenarios()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total_passed = sum(1 for _, passed in results if passed)
    total_suites = len(results)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {total_passed}/{total_suites} test suites passed")
    
    if total_passed == total_suites:
        print("\n✓ All tests passed! OCR improvements are working correctly.")
        return 0
    else:
        print(f"\n✗ {total_suites - total_passed} test suite(s) failed. Review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
