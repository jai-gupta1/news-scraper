from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta

url = 'https://www.whitehouse.gov/news/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

def clean_text(text):
    if not text:   
        return ''
    return ' '.join(text.strip().split())

def fetch_date(url):
    response = requests.get(url, headers=headers)
    sauce = BeautifulSoup(response.text, 'html.parser')
    date_tag = sauce.find('time')
    parsed_date = datetime.strptime(date_tag.text, '%B %d, %Y')
    return parsed_date

def fetch_article(days):
    cont_href = []
    list_items = soup.find_all('h2', class_='wp-block-post-title')
    for item in list_items:
        link_tag = item.find('a')
        if link_tag:
            href = link_tag['href']
            if fetch_date(href) >= datetime.now() - timedelta(days=days):
                cont_href.append(href)
            else:
                break
                
    return cont_href

def fetch_news(days):
    cont_href = fetch_article(days)
    print(cont_href)


    # if parsed_date < datetime.now() - timedelta(days=days):
    #     continue



    # title_tag = soup.find('h2', class_='title')
    # title = title_tag.text.strip()
    # link_tag = title_tag.find('a')
    # link = link_tag['href']
    # print(f'{parsed_date} - {title} - {link}')

if __name__ == '__main__':
    fetch_news(1)
