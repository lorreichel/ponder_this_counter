"""
Script to analyze solver data and generate top solver reports.
Uses the name mapping configuration to handle duplicate names.
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime

def normalize_name(name):
    """Basic normalization of names."""
    # Remove asterisks
    name = re.sub(r'\*+', '', name)
    # Remove extra whitespace
    name = ' '.join(name.split())
    # Strip
    name = name.strip()
    return name

def extract_names_from_text(text):
    """Extract individual names from solver text."""
    if not text:
        return []

    names = []

    # Try different separators
    # Method 1: Comma-separated
    if ',' in text:
        parts = text.split(',')
        for part in parts:
            part = normalize_name(part)
            if part and len(part) > 1:
                names.append(part)

    # Method 2: Semicolon-separated
    elif ';' in text:
        parts = text.split(';')
        for part in parts:
            part = normalize_name(part)
            if part and len(part) > 1:
                names.append(part)

    # Method 3: Line-separated
    elif '\n' in text:
        lines = text.split('\n')
        for line in lines:
            line = normalize_name(line)
            if line and len(line) > 1 and not line.lower().startswith(('list', 'solver', 'correct')):
                names.append(line)

    # Method 4: Single name or space-separated (if short)
    else:
        text = normalize_name(text)
        if text and len(text) > 1:
            # If text is long, might be multiple names separated by spaces
            if len(text) > 100:
                # Heuristic: split on multiple spaces or specific patterns
                parts = re.split(r'\s{2,}', text)
                for part in parts:
                    part = normalize_name(part)
                    if part and len(part) > 1:
                        names.append(part)
            else:
                names.append(text)

    return names

def load_name_mapping(config_file='name_mapping_config.json'):
    """Load name mapping configuration."""
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config.get('name_mapping', {})
    except FileNotFoundError:
        print(f"Warning: {config_file} not found. Proceeding without name mapping.")
        return {}

def apply_name_mapping(name, mapping):
    """Apply name mapping to get canonical name."""
    return mapping.get(name, name)

def analyze_solvers(data, name_mapping, cutoff_date=None):
    """Analyze solver data and count solves per person."""
    solver_counts = Counter()
    solver_months = defaultdict(list)

    for entry in data:
        if entry['status'] != 'success' or not entry['solver_text']:
            continue

        # Check cutoff date
        if cutoff_date:
            entry_date = datetime(entry['year'], entry['month_num'], 1)
            if entry_date > cutoff_date:
                continue

        names = extract_names_from_text(entry['solver_text'])

        for name in names:
            canonical = apply_name_mapping(name, name_mapping)
            solver_counts[canonical] += 1
            solver_months[canonical].append((entry['year'], entry['month']))

    return solver_counts, solver_months

def generate_report(solver_counts, solver_months, top_n=50, title="Top Solvers"):
    """Generate a formatted report of top solvers with proper tied ranking."""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")

    print(f"{'Rank':<6} {'Name':<40} {'Puzzles Solved':>12}")
    print(f"{'-'*70}")

    top_solvers = solver_counts.most_common(top_n)
    current_rank = 1

    for i, (name, count) in enumerate(top_solvers):
        # Update rank only if count is different from previous
        if i > 0 and top_solvers[i-1][1] != count:
            current_rank = i + 1

        # Handle Unicode encoding issues on Windows
        try:
            print(f"{current_rank:<6} {name:<40} {count:>12}")
        except UnicodeEncodeError:
            # Replace problematic characters with ASCII equivalents
            name_safe = name.encode('ascii', 'replace').decode('ascii')
            print(f"{current_rank:<6} {name_safe:<40} {count:>12}")

    print(f"{'-'*70}")
    print(f"Total unique solvers: {len(solver_counts)}")
    print(f"{'='*70}\n")

def main():
    """Main function to generate top solver reports."""
    print("Loading solver data...")
    with open('solver_lists_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Loading name mapping configuration...")
    name_mapping = load_name_mapping()
    print(f"Loaded {len(name_mapping)} name mappings")

    # Overall analysis
    print("\nAnalyzing all-time solver statistics...")
    solver_counts, solver_months = analyze_solvers(data, name_mapping)

    generate_report(solver_counts, solver_months, top_n=50, title="All-Time Top Solvers")

    # Analysis up to June 2024
    print("\n\nAnalyzing solver statistics up to June 2024...")
    june_2024_cutoff = datetime(2024, 6, 30)
    solver_counts_june_2024, solver_months_june_2024 = analyze_solvers(
        data, name_mapping, cutoff_date=june_2024_cutoff
    )

    generate_report(
        solver_counts_june_2024,
        solver_months_june_2024,
        top_n=50,
        title="Top Solvers (Through June 2024)"
    )

    # Analysis up to November 2025
    print("\n\nAnalyzing solver statistics up to November 2025...")
    nov_2025_cutoff = datetime(2025, 11, 30)
    solver_counts_nov_2025, solver_months_nov_2025 = analyze_solvers(
        data, name_mapping, cutoff_date=nov_2025_cutoff
    )

    generate_report(
        solver_counts_nov_2025,
        solver_months_nov_2025,
        top_n=50,
        title="Top Solvers (Through November 2025)"
    )

    # Helper function to assign proper tied ranks
    def assign_ranks(solver_list):
        """Assign ranks with ties handled properly."""
        ranked = []
        current_rank = 1
        for i, (name, count) in enumerate(solver_list):
            if i > 0 and solver_list[i-1][1] != count:
                current_rank = i + 1
            ranked.append({"rank": current_rank, "name": name, "count": count})
        return ranked

    # Save detailed results to JSON
    output = {
        "all_time": assign_ranks(solver_counts.most_common()),
        "through_june_2024": assign_ranks(solver_counts_june_2024.most_common()),
        "through_november_2025": assign_ranks(solver_counts_nov_2025.most_common())
    }

    with open('top_solvers_results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print("\n\nDetailed results saved to top_solvers_results.json")

if __name__ == "__main__":
    main()
