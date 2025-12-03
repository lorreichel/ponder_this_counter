"""
Script to scrape solver lists from IBM's Ponder This puzzle archive.
Retrieves all solver lists from May 1998 to present.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re

def generate_urls(start_year=1999, start_month=8):
    """Generate all URLs from August 1999 to current month."""
    urls = []
    current_date = datetime.now()

    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    year = start_year
    month_idx = start_month - 1  # Convert to 0-based index

    while year < current_date.year or (year == current_date.year and month_idx <= current_date.month - 1):
        month_name = months[month_idx]
        url = f"https://research.ibm.com/haifa/ponderthis/challenges/{month_name}{year}.html"
        urls.append({
            'url': url,
            'year': year,
            'month': month_name,
            'month_num': month_idx + 1
        })

        month_idx += 1
        if month_idx >= 12:
            month_idx = 0
            year += 1

    return urls

def extract_solver_section(soup):
    """Extract solver list from the page - handles two specific formats."""
    solver_names = []

    # Format A: Look for HTML comments containing "solve" (case-insensitive)
    from bs4 import Comment
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    for comment in comments:
        comment_text = str(comment).strip()
        if 'solve' in comment_text.lower():
            # Found the start marker, now collect all <b> tags until end marker or next comment
            current = comment.next_element
            while current:
                # Check if we hit another HTML comment (end marker)
                if isinstance(current, Comment):
                    break

                # Extract bold tags
                if hasattr(current, 'name') and current.name == 'b':
                    name = current.get_text().strip()
                    if name and name not in solver_names:
                        solver_names.append(name)

                # Also check if current element contains bold tags
                if hasattr(current, 'find_all'):
                    for bold in current.find_all('b'):
                        name = bold.get_text().strip()
                        if name and name not in solver_names:
                            solver_names.append(name)

                current = current.next_sibling

            if solver_names:
                return ', '.join(solver_names)

    # Format B: Look for "People who answered correctly:" text
    all_text_elements = soup.find_all(string=re.compile(r'[Pp]eople who answered correctly', re.IGNORECASE))

    for text_elem in all_text_elements:
        # Found the marker, now collect bold tags from following elements
        current = text_elem.parent

        # Move to next sibling elements
        while current:
            current = current.next_sibling

            if not current:
                break

            # Stop if we hit a div with class "ibm-rule"
            if hasattr(current, 'get') and current.get('class'):
                if 'ibm-rule' in current.get('class'):
                    break

            # Extract all bold tags from this element and its children
            if hasattr(current, 'find_all'):
                for bold in current.find_all('b'):
                    name = bold.get_text().strip()
                    if name and name not in solver_names:
                        solver_names.append(name)

            # Also check if current element itself is a bold tag
            if hasattr(current, 'name') and current.name == 'b':
                name = current.get_text().strip()
                if name and name not in solver_names:
                    solver_names.append(name)

        if solver_names:
            return ', '.join(solver_names)

    return None

def scrape_solver_list(url_info, show_progress=True):
    """Scrape solver list from a single URL."""
    url = url_info['url']
    if show_progress:
        print(f"Scraping {url_info['month']} {url_info['year']}...", end=' ', flush=True)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        solver_text = extract_solver_section(soup)

        if solver_text:
            # Clean up asterisks
            solver_text = re.sub(r'\*+', '', solver_text)

            if show_progress:
                print("OK")
            return {
                'year': url_info['year'],
                'month': url_info['month'],
                'month_num': url_info['month_num'],
                'url': url,
                'solver_text': solver_text,
                'status': 'success'
            }
        else:
            if show_progress:
                print("(no solvers)")
            return {
                'year': url_info['year'],
                'month': url_info['month'],
                'month_num': url_info['month_num'],
                'url': url,
                'solver_text': None,
                'status': 'no_solvers_found'
            }

    except requests.exceptions.RequestException as e:
        if show_progress:
            print(f"ERROR")
        return {
            'year': url_info['year'],
            'month': url_info['month'],
            'month_num': url_info['month_num'],
            'url': url,
            'solver_text': None,
            'status': 'error',
            'error': str(e)
        }

def main():
    """Main function to scrape all solver lists."""
    print("Generating URLs...")
    urls = generate_urls()
    print(f"Total URLs to scrape: {len(urls)}")

    results = []

    for url_info in urls:
        result = scrape_solver_list(url_info)
        results.append(result)

        # Be polite to the server
        time.sleep(0.5)

    # Save to JSON
    output_file = 'solver_lists_raw.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nScraping complete!")
    print(f"Results saved to {output_file}")

    # Print summary
    success = sum(1 for r in results if r['status'] == 'success')
    no_solvers = sum(1 for r in results if r['status'] == 'no_solvers_found')
    errors = sum(1 for r in results if r['status'] == 'error')

    print(f"\nSummary:")
    print(f"  Successful: {success}")
    print(f"  No solvers found: {no_solvers}")
    print(f"  Errors: {errors}")

if __name__ == "__main__":
    main()
