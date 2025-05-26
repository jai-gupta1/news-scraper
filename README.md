# News Scraper

A Python-based web scraper that monitors specific news sites for updates.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file with your configuration:
```
NEWS_SITES=site1.com,site2.com
UPDATE_INTERVAL=30  # minutes
```

## Usage

Run the scraper:
```
python scraper.py 