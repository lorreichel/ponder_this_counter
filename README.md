# Ponder This Solver Analysis

This project scrapes and analyzes solver lists from IBM's "Ponder This" monthly puzzle challenge.

## Overview

IBM's Ponder This publishes a mathematical/computational puzzle each month and then releases a list of solvers. This project:
1. Scrapes all solver lists from May 1998 to present
2. Handles different page formats across the years
3. Identifies and suggests name deduplication
4. Analyzes top solvers across different time periods

## Files

- **scrape_solvers.py** - Scrapes solver lists from all monthly puzzle pages
- **analyze_names.py** - Analyzes names and identifies potential duplicates
- **top_solvers.py** - Generates top solver reports using cleaned data
- **solver_lists_raw.json** - Raw scraped data (generated)
- **name_mapping_config.json** - Name mapping configuration (generated)
- **top_solvers_results.json** - Final analysis results (generated)

## Usage

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Scrape Solver Lists

```bash
python scrape_solvers.py
```

This will create `solver_lists_raw.json` containing all scraped solver data.

### Step 3: Analyze and Deduplicate Names

```bash
python analyze_names.py
```

This creates `name_mapping_config.json` with suggested name mappings. **Review and edit this file** to ensure names are correctly mapped to their canonical forms.

### Step 4: Generate Top Solver Reports

```bash
python top_solvers.py
```

This generates reports for:
- All-time top solvers
- Top solvers through June 2024
- Top solvers through November 2025

Results are saved to `top_solvers_results.json` and printed to console.

## Data Format

### solver_lists_raw.json

```json
[
  {
    "year": 2024,
    "month": "January",
    "month_num": 1,
    "url": "https://research.ibm.com/haifa/ponderthis/challenges/January2024.html",
    "solver_text": "John Doe, Jane Smith, ...",
    "status": "success"
  }
]
```

### name_mapping_config.json

```json
{
  "description": "Name mapping configuration for Ponder This solvers",
  "name_mapping": {
    "J. Doe": "John Doe",
    "Jon Doe": "John Doe"
  }
}
```

## Notes

- Asterisks (*) in names are automatically removed
- The scraper is polite to the server with 0.5s delays between requests
- Different page formats are handled with multiple extraction methods
- Name matching uses similarity algorithms but requires manual review for accuracy

## Future Improvements

- Add more sophisticated name matching algorithms
- Include solver streak analysis (consecutive months solved)
- Add visualization of solver trends over time
- Track difficulty ratings if available
