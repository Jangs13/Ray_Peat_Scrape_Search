import streamlit as st
import requests
import json
from uuid import uuid4
import os

# Debugging: Print available secrets
st.write("Available secrets:", st.secrets)

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
        "search_type": "semantic",
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

def display_all(results):
    for result in results.get('score_chunks', []):
        metadata = result.get('metadata', [])[0]
        link = metadata.get('link')
        
        description = metadata.get('chunk_html')[:250] + "..."  # Displaying a part of the description

        st.markdown(f"### Article Title: {get_title_from_link(link)}")
        st.write(f"**Article Link:** [{link}]({link})")
        st.write(f"**Description:** {description}")
        st.write("---")

def get_title_from_link(link):
    return link.split('/')[-1].replace('-', ' ').replace('.shtml', '').title()

def main():
    page = st.sidebar.selectbox("Navigation", ["Home", "Search Articles", "All Articles"])

    if page == "Home":
        st.title("W E L C O M E")
        st.image("logo.jpg", width=200)
        st.markdown("""
                    :red-background[Although we removed the page for ordering books several months ago, there's still a backlog of orders, so there can be a very long delay, but the orders are still being filled.]
        
        This website currently reports on my research in aging, nutrition, and hormones. You will find this information in the ARTICLES section.
        A variety of health problems are examined (eg., infertility, epilepsy, dementia, diabetes, premenstrual syndrome, arthritis, menopause), and the therapeutic uses of progesterone, pregnenolone, thyroid, and coconut oil are frequently discussed.

        My approach gives priority to environmental influences on development, regenerative processes, and an evolutionary perspective. When biophysics, biochemistry, and physiology are worked into a comprehensive view of the organism, it appears that the degenerative processes are caused by defects in our environment.

        As a supplement to this web site, I've also included examples of my artwork, specifically some of my paintings, which you will find in the ART GALLERY. As I've discussed in my books, I see painting as an essential part of grasping the world scientifically. For a few years, I taught art and painted portraits. I have shown my work in both the US and Mexico.

        :orange[----Ray Peat] """
        )
    elif page == "Search Articles":
        st.title("Search Articles")
        query = st.text_input("Enter your search query:")
        if st.button("Search"):
            results = search_articles(query)
            display_results(results)
    elif page == "All Articles":
        st.title("All Articles")
        results = search_articles(query="", page_size=50)  # Fetching a broad result set
        display_all(results)

if __name__ == "__main__":
    main()
