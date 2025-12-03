# Ponder This Solver Counter - Instructions

## Quick Start Guide

### Step 1: Run the Scraper (Currently Running)

The scraper is collecting solver data from all Ponder This puzzles from August 1999 to present.

```bash
python scrape_solvers.py
```

**Status**: This script is currently running in the background and will take about 3-5 minutes to complete (317 pages × 0.5 seconds each + processing time).

**Output**: `solver_lists_raw.json` - Contains raw solver data from all puzzles.

### Step 2: Analyze Names and Identify Duplicates

Once the scraper finishes, run the name analysis script:

```bash
python analyze_names.py
```

This will:
- Extract all solver names from the raw data
- Identify potential duplicate names (e.g., "J. Smith" vs "John Smith")
- Generate similarity-based groupings
- Create a configuration file for manual review

**Output**: `name_mapping_config.json` - Configuration file with suggested name mappings.

**ACTION REQUIRED**: Review and edit `name_mapping_config.json` to ensure names are correctly mapped. The file contains:
- `name_mapping`: Dictionary of variant names → canonical names
- `similar_groups`: Groups of names that appear similar
- `top_solvers_preview`: Preview of top solvers before manual adjustments

### Step 3: Generate Top Solver Reports

After reviewing and editing the name mapping configuration, run:

```bash
python top_solvers.py
```

This generates three reports:
1. **All-time top solvers** - From August 1999 to present
2. **Top solvers through June 2024**
3. **Top solvers through November 2025**

**Output**:
- Console output with formatted tables
- `top_solvers_results.json` - Detailed JSON results for all time periods

## Files Overview

### Scripts
- `scrape_solvers.py` - Web scraper for IBM Ponder This solver lists
- `analyze_names.py` - Name deduplication and analysis tool
- `top_solvers.py` - Top solver report generator
- `test_scraper.py` - Test script for debugging scraper on sample URLs

### Data Files (Generated)
- `solver_lists_raw.json` - Raw scraped data
- `name_mapping_config.json` - Name mapping configuration (review and edit this!)
- `top_solvers_results.json` - Final analysis results

### Documentation
- `README.md` - Project overview and usage guide
- `INSTRUCTIONS.md` - This file
- `requirements.txt` - Python dependencies

## Data Cleaning Notes

### Asterisks
Asterisks (*) in solver names indicate bonus solutions. These are automatically removed during scraping.

### Name Variations
Common variations to watch for when reviewing `name_mapping_config.json`:
- Initials vs full names: "J. Smith" → "John Smith"
- Middle initials: "John A. Smith" vs "John Smith"
- Spelling variations or typos
- Different name orderings
- Accented characters vs plain ASCII

### Manual Review Tips

1. Open `name_mapping_config.json` in your editor
2. Look at the `similar_groups` section for automatically detected similarities
3. Review the `name_mapping` dictionary
4. Add or modify mappings as needed
5. Check the `top_solvers_preview` to see if any obvious duplicates remain

Example mapping:
```json
{
  "name_mapping": {
    "J. Doe": "John Doe",
    "Jon Doe": "John Doe",
    "Doe, John": "John Doe"
  }
}
```

## Timeline

- **August 1999**: First puzzle with solver list
- **June 2024**: First analysis cutoff point
- **November 2025**: Second analysis cutoff point
- **December 2024**: Current data (as of script execution)

## Technical Details

- **Total puzzles**: ~317 (August 1999 to December 2024)
- **Scraping rate**: 0.5 seconds per page (polite to server)
- **Name matching**: Uses SequenceMatcher with 85% similarity threshold
- **Format handling**: Multiple HTML formats across different years

## Troubleshooting

### Scraper Issues
- If scraping fails, check internet connection
- Some older pages may not have solver lists (marked as "no_solvers_found")
- Network errors are logged with "error" status

### Name Analysis Issues
- Requires `solver_lists_raw.json` to exist
- If no similarities found, threshold may need adjustment
- Very similar names might be missed if they differ significantly

### Report Generation Issues
- Requires both `solver_lists_raw.json` and `name_mapping_config.json`
- If results look wrong, review name mappings first
- Date filters use inclusive ranges

## Next Steps After Report Generation

1. Review the top solver lists
2. Consider additional analyses:
   - Solver streaks (consecutive months)
   - Difficulty trends
   - Geographic distribution
   - Bonus vs main problem completion rates
3. Visualize trends over time
4. Export to other formats (CSV, Excel, etc.)
