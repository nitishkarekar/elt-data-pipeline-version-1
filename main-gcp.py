#add this file in GCP Cloud Run Function and deploy. You can test this out by running it and a parquet file will be placed in the specified bucket.
import functions_framework
import requests
import pandas as pd
from google.cloud import storage
import io
import uuid

@functions_framework.http
def data_elt(request):
    """
    Background Cloud Function to be triggered by an HTTP request.
    """
    
    # --- CONFIGURATION ---
    # REPLACE THIS with your actual bucket name from Step 1
    BUCKET_NAME = '' #replace/add your bucket name you created
    FILE_NAME = f'' #add the file name you want the parquet file to be example: 'abc.parquet'

    try:
        # 1. Fetch Data
        print("Fetching data from API...")
        response_API = requests.get('https://data.wa.gov/resource/f6w7-q2d2.json')
        raw_json_data = response_API.json()

        # 2. Process Data
        print("Processing data into DataFrame...")
        df = pd.json_normalize(raw_json_data)
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # 3. Create Parquet File in Memory (Virtual File)
        # We cannot save to C:/, so we save to a memory buffer (RAM)
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', index=False, compression='snappy')
        
        # Reset the buffer pointer to the start so we can read from it
        parquet_buffer.seek(0)

        # 4. Upload to Google Cloud Storage
        print(f"Uploading {FILE_NAME} to {BUCKET_NAME}...")
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)
        
        # Upload the virtual file from RAM
        blob.upload_from_file(parquet_buffer, content_type='application/octet-stream')

        return f'Success! Uploaded {FILE_NAME} to bucket {BUCKET_NAME}.', 200

    except Exception as e:
        print(f"Error: {e}")
        return f"Error occurred: {e}", 500
