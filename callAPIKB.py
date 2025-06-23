import httpx
from dotenv import load_dotenv
import os
import json
import glob

# Load API Key
load_dotenv()
API_KEY_KB = os.getenv("API_KEY_KB")

# Set API URL and header
url = 'https://dify.sapocorp.vn/v1/datasets/aa75acc4-f2ce-41c1-9671-c4d249d1cbdd/documents/fe4787d2-90d3-454f-b5a6-433f661e2f57/update-by-file'

headers = {
    'Authorization': f"Bearer {API_KEY_KB}",
}

# Prepare data field (converted to JSON string)
data_field = {
    "name": "Bảng giá Retail.csv",  # You can dynamically set this to the filename later
    "indexing_technique": "high_quality",
    "process_rule": {
        "rules": {
            "pre_processing_rules": [
                {"id": "remove_extra_spaces", "enabled": False},
                {"id": "remove_urls_emails", "enabled": False}
            ],
            "segmentation": {
                "separator": "###",
                "max_tokens": 500
            }
        },
        "mode": "custom"
    }
}

# Folder path
folder_path = './leadChatBotDocument/'

# Find all .csv files in the folder
csv_files = glob.glob(os.path.join(folder_path, '*.csv'))

# Loop through each CSV file and send POST request
for file_path in csv_files:
    file_name = os.path.basename(file_path)
    
    # Update "name" field in data_field
    data_field["name"] = file_name
    
    data_json = json.dumps(data_field)
    
    # Prepare files for POST
    files = {
        'data': (None, data_json, 'text/plain'),
        'file': open(file_path, 'rb')
    }
    
    # Send POST request
    response = httpx.post(url=url, headers=headers, files=files)
    
    # Close the file handle
    files['file'].close()
    
    # Print result
    print(f'Uploaded: {file_name}')
    print(f'Status Code: {response.status_code}')
    print(f'Response: {response.text}\n')
