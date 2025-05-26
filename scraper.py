import os
import time
import schedule
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NewsScraper:
    def __init__(self):
        self.sites = os.getenv('NEWS_SITES', '').split(',')
        self.update_interval = int(os.getenv('UPDATE_INTERVAL', 30))
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.last_headlines = {}

    def scrape_site(self, url):
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # This is a basic example - you'll need to adjust the selectors
            # based on the specific news sites you're targeting
            headlines = soup.find_all('h2')
            current_headlines = [h.text.strip() for h in headlines]
            
            # Check for new headlines
            if url in self.last_headlines:
                new_headlines = set(current_headlines) - set(self.last_headlines[url])
                if new_headlines:
                    print(f"\nNew headlines from {url}:")
                    for headline in new_headlines:
                        print(f"- {headline}")
            
            self.last_headlines[url] = current_headlines
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")

    def run(self):
        print("Starting news scraper...")
        for site in self.sites:
            self.scrape_site(site)

def main():
    scraper = NewsScraper()
    
    # Schedule the scraping job
    schedule.every(scraper.update_interval).minutes.do(scraper.run)
    
    # Run immediately on start
    scraper.run()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 