# White House News Scraper

A Python script that scrapes and displays recent news from the White House website (whitehouse.gov).

## Features

- Fetches recent news articles from the White House website
- Categorizes news items (Executive Orders, Fact Sheets, Statements, etc.)
- Displays article titles, dates, excerpts, and links
- Filters news by date range
- Cleans and formats text for better readability

## Requirements

- Python 3.6+
- requests
- beautifulsoup4

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install requests beautifulsoup4
```

## Usage

Run the script with:
```bash
python scraper.py
```

By default, it will show news from the last 7 days. You can modify the `days_back` parameter in the script to change this. 