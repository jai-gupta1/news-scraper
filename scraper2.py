from bs4 import BeautifulSoup
import requests
from datetime import datetime, timedelta
from openai import OpenAI
from dotenv import load_dotenv
from email_sender import send_email
import os

load_dotenv(override=True)

client = OpenAI()

def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Please summarize the following:\n\n{text}"}
        ],
        temperature=0.5,
        max_tokens=500  # Controls the length of the summary
    )
    
    summary = response.choices[0].message.content
    return summary

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
    title_list = []
    list_items = soup.find_all('h2', class_='wp-block-post-title')
    for item in list_items:
        link_tag = item.find('a')
        if link_tag:
            href = link_tag['href']
            if fetch_date(href) >= datetime.now() - timedelta(days=days):
                cont_href.append(href)
                title_list.append(item.text.strip())
            else:
                break
                
    return cont_href, title_list

def fetch_news_text(gravy):
    paragraphs = gravy.find_all('p')
    news_text = []
    for p in paragraphs:
        news_text.append(p.text.strip())
    return news_text

def fetch_news(days):
    cont_href, title_list = fetch_article(days)
    news_list = []
    for href in cont_href:
        response = requests.get(href, headers=headers)
        gravy = BeautifulSoup(response.text, 'html.parser')
        all_news_text = fetch_news_text(gravy)
        summary = summarize_text(all_news_text)
        news_list.append(summary)

    news_string = create_news_string(news_list, title_list)
    return news_string

def create_news_string(news_list, title_list):
    news_string = ""
    for i, news in enumerate(news_list):
        news_string += f"📰 {title_list[i]}\n{news}\n\n"
    return news_string


if __name__ == '__main__':
    news_string = fetch_news(2)
    success = send_email(
        sender_email= os.getenv("EMAIL_USERNAME1"),
        sender_password= os.getenv("EMAIL_PASSWORD"),
        recipient_emails= [os.getenv("EMAIL_USERNAME2")],
        subject="Daily White House News",
        body=news_string
    )
    if success:
        print("success!")
    else:
        print("failed!")

