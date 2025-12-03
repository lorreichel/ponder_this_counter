"""
Script to analyze solver names and identify potential duplicates.
Creates a name mapping configuration file for manual review.
"""

import json
import re
from collections import defaultdict, Counter
from difflib import SequenceMatcher

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

def similarity(a, b):
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def find_similar_names(names, name_occurrences, top_n=100, threshold=0.85):
    """Find names similar to top N solvers using efficient get_close_matches."""
    from difflib import get_close_matches

    # Get list of all unique names
    unique_names = list(set(names))

    # Get top N solvers by occurrence count
    top_solvers = sorted(unique_names, key=lambda x: name_occurrences[x], reverse=True)[:top_n]

    print(f"Analyzing top {len(top_solvers)} solvers for name variations...")

    similar_groups = []
    processed = set()

    for i, top_name in enumerate(top_solvers):
        if top_name in processed:
            continue

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(top_solvers)} top solvers...")

        # Use get_close_matches for fast initial filtering
        # cutoff of 0.8 is slightly lower than our threshold to catch more candidates
        candidates = get_close_matches(top_name, unique_names, n=10, cutoff=0.8)

        # Now apply SequenceMatcher only to the candidates
        group = [top_name]
        processed.add(top_name)

        for candidate in candidates:
            if candidate == top_name or candidate in processed:
                continue

            # Use precise SequenceMatcher on candidates
            if similarity(top_name, candidate) >= threshold:
                group.append(candidate)
                processed.add(candidate)

        if len(group) > 1:
            similar_groups.append(sorted(group, key=lambda x: name_occurrences[x], reverse=True))

    return similar_groups

def analyze_name_variations(names):
    """Analyze different types of name variations."""
    variations = defaultdict(list)

    name_dict = {}
    for name in names:
        name_dict[name] = name

    # Look for common patterns
    for name in names:
        # Extract base name (lowercase, no special chars)
        base = re.sub(r'[^\w\s]', '', name.lower())
        variations[base].append(name)

    # Find variations
    potential_duplicates = {}
    for base, name_list in variations.items():
        if len(name_list) > 1:
            unique_variations = list(set(name_list))
            if len(unique_variations) > 1:
                # Sort by frequency
                canonical = max(unique_variations, key=lambda x: name_list.count(x))
                potential_duplicates[canonical] = sorted(set(unique_variations))

    return potential_duplicates

def main():
    """Main function to analyze names."""
    print("Loading solver data...")
    with open('solver_lists_raw.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("Extracting names...")
    all_names = []
    name_occurrences = defaultdict(int)

    for entry in data:
        if entry['status'] == 'success' and entry['solver_text']:
            names = extract_names_from_text(entry['solver_text'])
            all_names.extend(names)
            for name in names:
                name_occurrences[name] += 1

    print(f"Total name instances: {len(all_names)}")
    print(f"Unique names: {len(set(all_names))}")

    print("\nFinding similar names among top 100 solvers...")
    similar_groups = find_similar_names(all_names, name_occurrences, top_n=100, threshold=0.85)

    print(f"Found {len(similar_groups)} groups of similar names")

    print("\nAnalyzing name variations...")
    variations = analyze_name_variations(all_names)

    print(f"Found {len(variations)} potential duplicate patterns")

    # Create name mapping configuration
    name_mapping = {}

    for group in similar_groups:
        # Use most common name as canonical
        canonical = max(group, key=lambda x: name_occurrences[x])
        for name in group:
            if name != canonical:
                name_mapping[name] = canonical

    for canonical, variants in variations.items():
        if canonical not in name_mapping:
            # Find the most common variant
            most_common = max(variants, key=lambda x: name_occurrences[x])
            for variant in variants:
                if variant != most_common:
                    name_mapping[variant] = most_common

    # Prepare output structure
    output = {
        "description": "Name mapping configuration for Ponder This solvers",
        "instructions": "Review and edit this mapping. The key is the variant name, the value is the canonical name.",
        "name_mapping": name_mapping,
        "similar_groups": similar_groups,
        "top_solvers_preview": []
    }

    # Add top solvers preview
    name_counts = Counter()
    for name in all_names:
        # Apply mapping
        canonical = name_mapping.get(name, name)
        name_counts[canonical] += 1

    output["top_solvers_preview"] = [
        {"name": name, "count": count}
        for name, count in name_counts.most_common(50)
    ]

    # Save configuration
    output_file = 'name_mapping_config.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nName mapping configuration saved to {output_file}")
    print("\nTop 20 solvers (before manual review):")
    for i, (name, count) in enumerate(name_counts.most_common(20), 1):
        print(f"{i:2d}. {name:40s} {count:4d} puzzles")

    print(f"\nPlease review {output_file} and adjust the name mappings as needed.")

if __name__ == "__main__":
    main()
