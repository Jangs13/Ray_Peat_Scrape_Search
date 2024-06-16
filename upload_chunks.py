import json
import requests
import time

API_KEY = 'tr-cXLsw2BU7bgBhoikpZvYipErlztAhg7A' 
DATASET_ID = 'a9a3a3df-e0c8-470f-805c-68aafbc00ced'
CREATE_CHUNK_URL = 'https://api.trieve.ai/api/chunk'

headers = {
    'Content-Type': 'application/json',
    'TR-Dataset': DATASET_ID,
    'Authorization': API_KEY,
}
payload = None
with open("prepared_chunks_payload.json",  encoding='utf-8') as f:
    payload = json.load(f)

def upload_chunk(dataset_id, chunk):
    
    try:
        response = requests.post(CREATE_CHUNK_URL, headers=headers, json=chunk)
        response.raise_for_status()  # Raise an HTTPError if the response was unsuccessful
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except requests.exceptions.RequestException as err:
        print(f"Other error occurred: {err}")  # Python 3.6
        
    except ValueError:
        print("Response content is not valid JSON")
        print(response.text)
            
    
    



uploaded_chunks = set()
print(f"UPLOADING {len(payload)} chunks")
respose_count = 0
for chunk in payload:
    # chunk = chunk.strip()  # Remove any leading/trailing whitespace
    # if not chunk or chunk in uploaded_chunks:  # Skip empty or already uploaded chunks
    #     continue

    response = upload_chunk(DATASET_ID, chunk)
    print(response["chunk_metadata"]["id"])
    respose_count+=1

print("uploaded chunks",respose_count)
