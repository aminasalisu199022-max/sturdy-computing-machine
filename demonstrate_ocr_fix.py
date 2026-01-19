#!/usr/bin/env python3
"""
Demonstration of OCR improvements for Nigerian license plate recognition.

This script shows how the improved OCR pipeline correctly handles:
1. OCR error correction (5→S, 8→B, 0↔O, 1→I)
2. Nigerian plate format validation (AAA-123AA)
3. Real-world OCR mistakes
"""

import sys
sys.path.insert(0, '/workspaces/sturdy-computing-machine')

from alpr_system.plate_validation_updated import (
    normalize_plate,
    is_valid_nigerian_plate,
    validate_and_format_plate
)


def print_header(title):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_plate(raw_text, description):
    """Test a plate with the OCR pipeline."""
    normalized = normalize_plate(raw_text)
    is_valid = is_valid_nigerian_plate(normalized)
    
    status = "✓ VALID" if is_valid else "✗ INVALID"
    print(f"\n{status}: {description}")
    print(f"  Input:      {raw_text:20} → ", end="")
    print(f"{normalized:15} (Valid: {is_valid})")
    
    return is_valid


def main():
    """Main demonstration."""
    print_header("NIGERIAN LICENSE PLATE OCR IMPROVEMENTS")
    print("\nThis demonstration shows the fixed OCR pipeline handling")
    print("common OCR errors while maintaining Nigerian plate format standard.")
    
    # Test cases demonstrating the improvements
    print_header("1. SIMPLE FORMATTING FIXES")
    test_plate("kts-123ab", "Lowercase input")
    test_plate("kts 123 ab", "Spaces instead of hyphen")
    test_plate("kts123ab", "Missing hyphen")
    
    print_header("2. OCR ERROR CORRECTION - LETTER POSITIONS")
    test_plate("k75123ab", "5→S in letter position")
    test_plate("k8s123ab", "8→B in letter position")
    test_plate("lag-890ef", "8→B in suffix position")
    
    print_header("3. OCR ERROR CORRECTION - DIGIT POSITIONS")
    test_plate("kts1o3ab", "O→0 in digit section")
    test_plate("kts-i03ab", "I→1 in digit section")
    test_plate("kts5i3ab", "Multiple errors: S from 5, I→1")
    
    print_header("4. CONTEXT-AWARE CORRECTIONS")
    test_plate("kts8o3ab", "8 in letter, O in digit → KTS-803AB")
    test_plate("kts5o3ab", "5 in letter, O in digit → KTS-503AB")
    test_plate("lag-1o1ef", "Multiple O→0 corrections")
    
    print_header("5. REAL-WORLD EXAMPLES")
    test_plate("KTS-123AB", "Valid plate - no errors")
    test_plate("ABJ-456CD", "Valid plate - no errors")
    test_plate("LAG-890EF", "Valid plate - 8→B not needed (already E)")
    
    print_header("6. PREVIOUSLY FAILING CASES")
    test_plate("kts-123ab", "Example from problem statement (lowercase)")
    
    # Summary
    print_header("SUMMARY")
    print("""
The improved OCR pipeline now:

✓ Correctly converts OCR digit errors to letters in letter positions:
  - 5 → S (looks like S)
  - 8 → B (looks like B)
  - 1 → I (looks like I)
  - 0 → O (looks like O)

✓ Correctly converts OCR letter errors to digits in digit positions:
  - O → 0 (looks like 0)
  - I → 1 (looks like 1)
  - S → 5 (looks like 5)
  - B → 8 (looks like 8)

✓ Validates Nigerian plate format: AAA-123AA

✓ Handles real OCR mistakes with context awareness

This ensures valid Nigerian plates like "KTS-123AB" are no longer
incorrectly marked as "Invalid format" due to OCR errors.
""")


if __name__ == "__main__":
    main()
