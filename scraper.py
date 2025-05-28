import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re

def clean_text(text):
    """Clean up text by removing extra whitespace"""
    if not text:
        return ""
    return ' '.join(text.strip().split())

def parse_date(date_text):
    """Parse date from White House format (e.g., 'May 27, 2025' or '2025-05-27T12:40:25-04:00')"""
    try:
        # Clean up the date text first
        date_text = clean_text(date_text)
        
        # Try ISO format first (2025-05-27T12:40:25-04:00)
        iso_pattern = r'\d{4}-\d{2}-\d{2}'
        iso_match = re.search(iso_pattern, date_text)
        if iso_match:
            date_str = iso_match.group(0)
            return datetime.strptime(date_str, '%Y-%m-%d')
            
        # Try standard format (May 27, 2025)
        date_pattern = r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        match = re.search(date_pattern, date_text)
        if match:
            date_str = match.group(0)
            # Remove any extra commas
            date_str = date_str.replace(',', '')
            return datetime.strptime(date_str, '%B %d %Y')
            
        return None
    except Exception as e:
        print(f"Error parsing date '{date_text}': {str(e)}")
        return None

def fetch_article_content(url, headers):
    """Fetch and parse an individual article page"""
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main article content
        article = soup.find('article')
        if not article:
            return None

        # Get the full content
        content_div = article.find(['div', 'section'], class_=lambda x: x and ('body-content' in x or 'entry-content' in x))
        full_content = ""
        if content_div:
            # Remove any script or style tags
            for script in content_div.find_all(['script', 'style']):
                script.decompose()
            
            # Get all paragraphs and headers
            paragraphs = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            full_content = "\n\n".join(clean_text(p.get_text()) for p in paragraphs)

        # Get metadata
        metadata = {}
        
        # Try to find author
        author_elem = soup.find('meta', {'name': 'author'}) or soup.find(class_=lambda x: x and 'author' in str(x).lower())
        if author_elem:
            metadata['author'] = author_elem.get('content', '') or clean_text(author_elem.get_text())

        # Try to find publication time
        time_elem = soup.find('time') or soup.find(class_=lambda x: x and 'date' in str(x).lower())
        if time_elem:
            metadata['published_time'] = time_elem.get('datetime', '') or clean_text(time_elem.get_text())

        # Try to find tags/topics
        topics = []
        topic_links = soup.find_all('a', href=lambda x: x and '/topics/' in str(x).lower())
        if topic_links:
            topics = [clean_text(link.get_text()) for link in topic_links]
            metadata['topics'] = list(set(topics))  # Remove duplicates

        return {
            'full_content': full_content,
            'metadata': metadata,
            'word_count': len(full_content.split()),
            'has_images': bool(article.find_all('img')),
            'has_videos': bool(article.find_all(['video', 'iframe'])),
        }

    except Exception as e:
        print(f"Error fetching article {url}: {str(e)}")
        return None

def get_weekly_highlights(days_back=7):
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
        
        # Find all news items
        for item in soup.find_all(['li', 'article', 'div'], class_=lambda x: x and ('post-' in str(x) or 'article' in str(x).lower())):
            try:
                # Get title
                title_elem = item.find(['h1', 'h2', 'h3', 'h4']) or item.find(class_=lambda x: x and 'title' in str(x).lower())
                if not title_elem:
                    continue
                
                title = clean_text(title_elem.get_text())
                if not title:
                    continue

                # Get date from the item text
                date_text = None
                # Look for date in multiple places
                date_containers = [
                    item.find('time'),
                    item.find(class_=lambda x: x and 'date' in str(x).lower()),
                    item.find(string=re.compile(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'))
                ]
                
                for container in date_containers:
                    if container:
                        date_text = container.get('datetime', '') or clean_text(container.string)
                        if date_text:
                            break

                if not date_text:
                    # Try finding date in siblings
                    for sibling in title_elem.next_siblings:
                        if sibling.string and re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}', str(sibling.string)):
                            date_text = clean_text(sibling.string)
                            break
                
                if not date_text:
                    print(f"No date found for article: {title}")
                    continue
                
                parsed_date = parse_date(date_text)
                if not parsed_date:
                    print(f"Could not parse date '{date_text}' for article: {title}")
                    continue
                
                # Set time to midnight for fair comparison
                parsed_date = parsed_date.replace(hour=0, minute=0, second=0, microsecond=0)
                    
                if parsed_date < cutoff_date:
                    print(f"Skipping old article from {parsed_date.strftime('%B %d, %Y')}: {title}")
                    continue

                # Get link
                link_elem = title_elem.find('a') or item.find('a', href=True)
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

                # Fetch full article content
                print(f"Fetching article: {title}")
                article_content = fetch_article_content(link, headers)

                # Only add if we haven't seen this title before
                if not any(item['title'] == title for item in news_items):
                    news_items.append({
                        'title': title,
                        'date': parsed_date.strftime("%B %d, %Y"),
                        'category': category,
                        'excerpt': excerpt,
                        'link': link,
                        'article_content': article_content
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
                
                if item['article_content']:
                    content = item['article_content']
                    print("\n📝 FULL ARTICLE DETAILS:")
                    print(f"Word Count: {content['word_count']}")
                    if content['metadata'].get('author'):
                        print(f"Author: {content['metadata']['author']}")
                    if content['metadata'].get('topics'):
                        print(f"Topics: {', '.join(content['metadata']['topics'])}")
                    print(f"Has Images: {'Yes' if content['has_images'] else 'No'}")
                    print(f"Has Videos: {'Yes' if content['has_videos'] else 'No'}")
                    print("\n💡 Full Content Preview (first 300 chars):")
                    print(f"{content['full_content'][:300]}...")
                elif item['excerpt']:
                    print(f"\n💡 {item['excerpt']}")
                
                print(f"\n🔗 {item['link']}")
                print("-" * 50)
        else:
            print("\nNo news items found within the specified date range.")

    except Exception as e:
        print(f"Error fetching news: {str(e)}")

if __name__ == "__main__":
    get_weekly_highlights(days_back=7)  # Changed to 7 days for testing