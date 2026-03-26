# Dictionary Scraper for German language

## Description

CLI tool for retrieving German word entries from duden.de by parsing the HTML
directly using `requests` and `BeautifulSoup`.

The goal is to extract structured data (meanings, examples, idioms) to support
vocabulary learning and contextual usage.

## Current Functionality

- Fetches a word from Duden
- Extracts:
  - Title (word + article)
  - Meanings (handles multiple, nested, and single-meaning cases)
  - Examples (Beispiele)
  - Idioms / expressions (Wendungen, Redensarten, Sprichwörter)
- Outputs formatted entries to terminal and file

## Problem Addressed

Existing Python libraries (e.g., `duden`) provide partial structured data but
omit important sections such as:
- idiomatic expressions
- usage examples
- contextual phrases

This project bypasses those limitations by scraping the official Duden website
directly and parsing the full HTML structure, ensuring all relevant linguistic
information is captured.
