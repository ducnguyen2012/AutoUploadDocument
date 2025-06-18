import os
import csv
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
load_dotenv()
app = FastAPI()

API_KEY = os.getenv("API_KEY_KB")
local_path = "./leadChatBotDocument/"

async def download_All_CSV_Files_to_local_path():
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        return JSONResponse(content="Created {local_path} in your system", status_code=200)
    else:
        print(f"Already existed {local_path} in your system, download all files")
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
    client = gspread.authorize(credentials)

    sheets = client.open_by_url("https://docs.google.com/spreadsheets/d/1_nlZzcJTL2NkYX8mG9ltDWoNx3WiSEGyXmzdMxPSel0/edit?gid=0#gid=0").worksheets()

    for sheet in sheets:
        '''
        Remember first column is 1 not zero
        '''
        print(f"Save sheet: {sheet.title}")
        all_data = sheet.get_all_values()
        csv_file_name = local_path + f"{sheet.title}.csv"

        with open(csv_file_name,'w',encoding='utf-8',newline='') as file:
            writer = csv.writer(file)
            writer.writerows(all_data)
    return JSONResponse(content="Done download all Documents into local path!",status_code=200)
async def upload_All_CSV_FILE_to_Dify():
    url = 'https://dify.sapocorp.vn/v1/datasets/7f38c77c-e500-4ed7-97d2-83a11d941c82/documents/ecfb0d64-8d68-4e31-9f5a-7b87c9c2fbbc/update-by-file'
    header = {
        'Authorization': f"Bearer {API_KEY}",
    }

    data_field = {
        "name": "Dify",
        "indexing_technique": "high_quality",
        "process_rule": {
            "rules": {
                "pre_processing_rules": [    
                    {"id": "remove_extra_spaces", "enabled": True},
                    {"id": "remove_urls_emails", "enabled": True}
                ],
                "segmentation": {
                    "separator": "###",      
                    "max_tokens": 500
                }
            },
            "mode": "custom"
        }
    }

    # Convert dict to JSON string
    data_json = json.dumps(data_field)

    #! check if local path dont exist then create it
    

    #! loop through all files:
    for filename in os.listdir(local_path):
        file_path = os.path.join(local_path,filename)
        if os.path.isfile(file_path):
            print(f"Pushing file {file_path} to Dify")
            files = {
                'data': (None, data_json, 'text/plain'),
                'file': open('./Dùng thử fnb.csv', 'rb')
            }
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url = url, headers= header, files = files)
                    return JSONResponse(content=response.raise_for_status())
            except httpx.TimeoutException as timeout:
                return JSONResponse(content=f"Timeout error: {timeout}")
            except httpx.HTTPError as httpError:
                return JSONResponse(content=f"HTTP Error: {httpError}")
            except httpx.ConnectError as connectError:
                return JSONResponse(content=f"Connect Error: {connectError}")
            except httpx.NetworkError as networkError:
                return JSONResponse(content=f"Network Error: {networkError}")
            except httpx.ConnectError as connectError:
                return JSONResponse(content=f"Connection Error: {connectError}")
    return JSONResponse(content="Done udpate all Documents in Dify",status_code=200)
@app.post("/api/lead/chat/updateDocument")
async def updateDocument():
    '''
    1. This function will download all the table in google sheet link
    2. It will save all CSV files in leadChatBOtDocument local path
    3. upload all the files into Dify
    '''
    await download_All_CSV_Files_to_local_path()
    await upload_All_CSV_FILE_to_Dify()
    return JSONResponse(content=f"Process done in download all CSV files and update all CSV files",status_code=200)




    







