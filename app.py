import streamlit as st
import requests
import json
from uuid import uuid4
import os
from bs4 import BeautifulSoup

# Load environment variables from Streamlit secrets
API_KEY = st.secrets["secrets"]["TRIEVE_API_KEY"]
DATASET_ID = st.secrets["secrets"]["TRIEVE_DATASET_ID"]
SEARCH_URL = 'https://api.trieve.ai/api/chunk/search'

headers = {
    'Content-Type': 'application/json',
    'TR-Dataset': DATASET_ID,
    'Authorization': API_KEY,
}

def search_articles(query, page=1, page_size=10):
    data = {
        "query": query,
        "search_type": "hybrid",
        "highlight_results": True,
        "highlight_delimiters": ["?", ",", ".", "!"],
        "highlight_threshold": 0.5,
        "page": page,
        "page_size": page_size
    }
    response = requests.post(SEARCH_URL, headers=headers, json=data)
    if response.status_code == 200:
        try:
            return response.json()
        except json.JSONDecodeError:
            st.error("Error decoding JSON from response.")
            st.write("Response content:", response.text)
            return {}
    else:
        st.error(f"Request failed with status code {response.status_code}")
        return {}

def display_results(results):
    for result in results.get('score_chunks', []):
        metadata = result.get('metadata', [])[0]
        link = metadata.get('link')
        score = result.get('score')
        description = metadata.get('chunk_html')[:250] + "..."  # Displaying a part of the description

        st.markdown(f"### Article Title: {get_title_from_link(link)}")
        st.write(f"**Article Link:** [{link}]({link})")
        st.write(f"**Similarity Score:** :green[{score*100:.2f}%]")
        st.write(f"**Description:** {description}")
        st.write("---")

def get_title_from_link(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('title')
            if title_tag:
                return title_tag.get_text().strip()
            else:
                return "No Title Found"
        else:
            return "Failed to Retrieve Page"
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    st.title("Search Articles")
    
    with st.form(key='search_form'):
        query = st.text_area("Enter your search query:", height=10)
        submit_button = st.form_submit_button(label='Search')

    if submit_button:
        results = search_articles(query)
        display_results(results)

if __name__ == "__main__":
    main()
