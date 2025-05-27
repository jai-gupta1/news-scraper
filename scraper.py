import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def clean_text(text):
    """Clean up text by removing extra whitespace"""
    if not text:
        return ""
    return ' '.join(text.strip().split())

def parse_date(date_text):
    """Parse date from White House format (e.g., 'May 27, 2025')"""
    try:
        return datetime.strptime(date_text.strip(), '%B %d, %Y')
    except Exception as e:
        print(f"Error parsing date '{date_text}': {str(e)}")
        return None

def get_weekly_highlights(days_back=1):
    """Get White House news highlights for the specified number of days"""
    url = "https://www.whitehouse.gov/news/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"\n🏛️ WHITE HOUSE HIGHLIGHTS (Last {days_back} Days) 🏛️")
    print("=" * 50)
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days_back)
        
        # Find all news items (they're in li elements with post- classes)
        for item in soup.find_all('li', class_=lambda x: x and 'post-' in str(x)):
            try:
                # Get title
                title_elem = item.find(['h1', 'h2', 'h3', 'h4'])
                if not title_elem:
                    continue
                
                title = clean_text(title_elem.get_text())
                if not title:
                    continue

                # Get date from the item text
                date_text = None
                # Date is usually right after the title
                for sibling in title_elem.next_siblings:
                    if sibling.string and any(month in sibling.string for month in [
                        'January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'
                    ]):
                        date_text = clean_text(sibling.string)
                        break
                
                if not date_text:
                    continue
                
                parsed_date = parse_date(date_text)
                if not parsed_date:
                    continue
                
                # Set time to midnight for fair comparison
                parsed_date = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                if parsed_date < cutoff_date:
                    continue

                # Get link
                link_elem = title_elem.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                link = link_elem['href']
                if not link.startswith('http'):
                    link = 'https://www.whitehouse.gov' + link

                # Get category
                category = "General"
                categories_text = item.get_text().lower()
                if "executive order" in categories_text:
                    category = "Executive Order"
                elif "fact sheet" in categories_text:
                    category = "Fact Sheet"
                elif "statement" in categories_text:
                    category = "Statement"
                elif "proclamation" in categories_text:
                    category = "Proclamation"
                elif "briefing" in categories_text:
                    category = "Briefing"

                # Get excerpt if available
                excerpt = ""
                excerpt_elem = item.find('p')
                if excerpt_elem and excerpt_elem.get_text() != title:
                    excerpt = clean_text(excerpt_elem.get_text())

                # Only add if we haven't seen this title before
                if not any(item['title'] == title for item in news_items):
                    news_items.append({
                        'title': title,
                        'date': parsed_date.strftime("%B %d, %Y"),
                        'category': category,
                        'excerpt': excerpt,
                        'link': link
                    })

            except Exception as e:
                print(f"Error processing item: {str(e)}")
                continue

        # Display results
        if news_items:
            # Sort by date
            news_items.sort(key=lambda x: parse_date(x['date']), reverse=True)
            
            # Group by date
            current_date = None
            for item in news_items:
                if item['date'] != current_date:
                    current_date = item['date']
                    print(f"\n📅 {item['date']}")
                    print("=" * 50)
                
                print(f"\n📰 {item['title']}")
                print(f"📋 Category: {item['category']}")
                if item['excerpt']:
                    print(f"\n💡 {item['excerpt']}")
                print(f"\n🔗 {item['link']}")
                print("-" * 50)
        else:
            print("\nNo news items found within the specified date range.")

    except Exception as e:
        print(f"Error fetching news: {str(e)}")

if __name__ == "__main__":
    get_weekly_highlights(days_back=7)  # Changed to 7 days for testing