"""
Test script to verify scraping works on sample URLs.
Tests different time periods to check for format changes.
"""

import requests
from bs4 import BeautifulSoup
import re

def test_url(url, expected_year, expected_month):
    """Test scraping a single URL."""
    print(f"\n{'='*70}")
    print(f"Testing: {url}")
    print(f"Expected: {expected_month} {expected_year}")
    print(f"{'='*70}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Show page title
        title = soup.find('title')
        if title:
            print(f"Page title: {title.get_text().strip()}")

        # Method 1: Look for specific headers
        print("\n--- Method 1: Looking for solver headers ---")
        headers = soup.find_all(['h2', 'h3', 'h4', 'p', 'b', 'strong'])
        found_solver_section = False
        for header in headers:
            header_text = header.get_text().strip().lower()
            if any(keyword in header_text for keyword in ['list of solvers', 'solvers', 'correct solvers', 'solver list']):
                print(f"Found header: {header.get_text().strip()}")
                next_elem = header.find_next_sibling()
                if next_elem:
                    solver_text = next_elem.get_text().strip()
                    print(f"Next element text (first 200 chars):\n{solver_text[:200]}")
                    found_solver_section = True
                break

        if not found_solver_section:
            print("No solver header found")

        # Method 2: Look in full text
        print("\n--- Method 2: Searching in full page text ---")
        all_text = soup.get_text()
        lines = all_text.split('\n')
        for i, line in enumerate(lines):
            if 'list of solvers' in line.lower() or 'correct solvers' in line.lower():
                print(f"Found at line {i}: {line.strip()}")
                print("Next 5 lines:")
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip():
                        print(f"  {lines[j].strip()}")
                found_solver_section = True
                break

        if not found_solver_section:
            print("No solver section found in page text")

        # Method 3: Show all paragraphs with commas
        print("\n--- Method 3: Paragraphs with multiple commas ---")
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text.count(',') > 3:
                print(f"Found paragraph with {text.count(',')} commas:")
                print(f"{text[:200]}...")
                found_solver_section = True
                break

        print(f"\nResult: {'SUCCESS' if found_solver_section else 'FAILED'}")

    except Exception as e:
        print(f"ERROR: {e}")

def main():
    """Test scraping on sample URLs from different time periods."""

    test_urls = [
        ("https://research.ibm.com/haifa/ponderthis/challenges/May1998.html", 1998, "May"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/January2000.html", 2000, "January"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/June2005.html", 2005, "June"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/January2010.html", 2010, "January"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/June2015.html", 2015, "June"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/January2020.html", 2020, "January"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/June2024.html", 2024, "June"),
        ("https://research.ibm.com/haifa/ponderthis/challenges/November2024.html", 2024, "November"),
    ]

    for url, year, month in test_urls:
        test_url(url, year, month)
        print("\n")

    print("\n" + "="*70)
    print("Testing complete!")
    print("="*70)

if __name__ == "__main__":
    main()
