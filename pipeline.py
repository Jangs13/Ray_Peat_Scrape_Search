import datetime
import json
import requests
from bs4 import BeautifulSoup
from uuid import uuid4
import argparse
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

API_KEY = os.getenv('TRIEVE_API_KEY')
DATASET_ID = os.getenv('TRIEVE_DATASET_ID')
CREATE_CHUNK_URL = 'https://api.trieve.ai/api/chunk'

def get_empty_chunk():
    return {
        "chunk_html": "",
        "chunk_vector": None,
        "convert_html_to_text": False,
        "group_ids": [],
        "link": " ",
        "metadata": {},
        "split_avg": False,
        "tag_set": [],
        "time_stamp": datetime.datetime.utcnow().isoformat() + 'Z',
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
        
        articles.append((title, content, link))
        print(f"Scraped article: {title}")

    return articles

def chunk_content(content, chunk_size=1000):
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

def save_chunks_to_file(chunks, filename='prepared_chunks_payload.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(chunks, file, ensure_ascii=False, indent=4)

def upload_chunk(headers, chunk):
    try:
        response = requests.post(CREATE_CHUNK_URL, headers=headers, json=chunk)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")
    except ValueError:
        print("Response content is not valid JSON")
        print(response.text)

def upload_chunks_from_file(filename='prepared_chunks_payload.json'):
    with open(filename, encoding='utf-8') as f:
        payload = json.load(f)

    headers = {
        'Content-Type': 'application/json',
        'TR-Dataset': DATASET_ID,
        'Authorization': API_KEY,
    }

    uploaded_chunks = set()
    print(f"UPLOADING {len(payload)} chunks")
    response_count = 0

    for chunk in payload:
        response = upload_chunk(headers, chunk)
        if response:
            print(response["chunk_metadata"]["id"])
            response_count += 1

    print("Uploaded chunks:", response_count)

def main():
    parser = argparse.ArgumentParser(description="Scrape articles and upload chunks to Trieve API")
    parser.add_argument('--scrape', action='store_true', help="Scrape articles from Ray Peat website")
    parser.add_argument('--upload', action='store_true', help="Upload chunks to Trieve API")
    args = parser.parse_args()

    if args.scrape:
        articles = scrape_articles()
        chunks = []

        for title, content, link in articles:
            chunk_payload = get_empty_chunk()
            chunk_payload["chunk_html"] = f'''{title + content}'''
            chunk_payload["link"] = link
            chunks.append(chunk_payload)

        save_chunks_to_file(chunks)

    if args.upload:
        upload_chunks_from_file()

if __name__ == '__main__':
    main()
