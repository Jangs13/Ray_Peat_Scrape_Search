import datetime
import json
import requests
from bs4 import BeautifulSoup
from uuid import uuid4
def getEmptyChunk():
    return {
            "chunk_html": "",
            "chunk_vector": None,  
            "convert_html_to_text": False,
            "group_ids": [], 
            "link": " ",
            "metadata": {},  
            "split_avg": False,
            "tag_set": [],  
            "time_stamp":  datetime.datetime.utcnow().isoformat() + 'Z',
            "tracking_id": f"{uuid4()}",  
            "upsert_by_tracking_id": True,
            "weight": 1.0
        }
def scrape_articles():
    base_url = "https://raypeat.com"
    url = base_url + "/articles/"
    
    response = requests.get(url)    
    if response.status_code != 200:
        print(f"Failed to retrieve the page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    links = soup.find_all('a', href=True)
    
    article_links = [link['href'] for link in links if "/articles/articles/" in link['href']]
    print(f"Filtered to {len(article_links)} article links.")
    
    for link in article_links:
        article_url = link if link.startswith('http') else base_url + link
        print(f"Fetching article from: {article_url}")
        article_response = requests.get(article_url)
        
        if article_response.status_code != 200:
            print(f"Failed to retrieve the article: {article_url}")
            continue
        
        article_soup = BeautifulSoup(article_response.text, 'html.parser')
        
        # Find the title
        title_tag = article_soup.find('font', {'size': '4'})
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            # Remove "A R T I C L E" from the title
            title = title_text.replace('A R T I C L E', '').strip()
        else:
            title = "No Title"
        
        # Find the content
        content_tags = article_soup.find_all('font', {'size': '3'})
        content = ' '.join(tag.get_text(strip=True) for tag in content_tags)

        if not content:
            print(f"No content found for article: {article_url}")
            continue
        
        articles.append((title, content,link))
        print(f"Scraped article: {title}")

    return articles

def chunk_content(content, chunk_size=1000):
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

articles = scrape_articles()
chunks = []

for title, content,link in articles:
    chunkPayload = getEmptyChunk()
    chunkPayload["chunk_html"] = f'''{title + content}'''
    chunkPayload["link"] = link
    chunks.append(chunkPayload)

with open('prepared_chunks_payload.json', 'w', encoding='utf-8') as file:
    json.dump(chunks, file, ensure_ascii=False, indent=4)
