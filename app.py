import os
import csv
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

#! ============================================================ loading all keys related  ===============================================================

load_dotenv()
app = FastAPI()
API_KEY = os.getenv("API_KEY_KB")
local_path = "./leadChatBotDocument/"

#! ============================================================ download all csv file to local path =======================================================
async def download_All_CSV_Files_to_local_path():
    if not os.path.exists(local_path):
        os.makedirs(local_path)
        print("Created f{local_path} in your system")
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
    print("Done download all Documents into local path!")


'''
This is my document_id: d66be3e8-b010-4f3f-aefb-299c4ffa8cbd
This is name of document: Tư vấn Retail.csv
This is my document_id: 7832fb85-db35-4162-9bba-e33bb6744de2
This is name of document: Tư vấn fnb.csv
This is my document_id: 86c7f394-529d-4e2c-978f-487fa214d704
This is name of document: Dùng thử Retail.csv
This is my document_id: fe4787d2-90d3-454f-b5a6-433f661e2f57
This is name of document: Dùng thử fnb.csv
This is my document_id: af366da2-b217-41b7-9411-f8b99b23627b
This is name of document: Bảng giá Retail.csv
This is my document_id: e7ca0074-c9b8-4cf9-8f6c-8ba05ec543c3
This is name of document: Bảng giá fnb.csv
'''
#! ============================== update dictionary ===============================


async def upload_All_CSV_FILE_to_Dify(dictionary_map_DOCUMENT_NAME_with_DOCUMENT_ID):
    #! duyệt toàn bộ file để update lên:
    filenames = os.listdir(local_path)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        for filename in filenames:
            if not filename.endswith(".csv"): continue
            document_id = dictionary_map_DOCUMENT_NAME_with_DOCUMENT_ID.get(filename)
            print(f"This is my document_id: {document_id}")
            url = f"https://dify.sapocorp.vn/v1/datasets/aa75acc4-f2ce-41c1-9671-c4d249d1cbdd/documents/{document_id}/update-by-file"

            header = {
                'Authorization': f"Bearer {API_KEY}",
            }

            data_field = {
                "name": f"{filename}",
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

            
            data_json = json.dumps(data_field) 
            filePath = os.path.join(local_path,filename)  
            files = {
                'data': (None, data_json, 'text/plain'),
                'file': open(filePath, 'rb')
            }
            try:
                response = await client.post(url = url, headers= header, files = files)
                response.raise_for_status()
                print(response.json())
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

#! ============================================================= main function ============================================
@app.post('/api/lead/chat/updateDocument')
async def updateDocument():

    '''
    1. This function will download all the table in google sheet link
    2. It will save all CSV files in leadChatBOtDocument local path
    3. upload all the files into Dify
    '''
    dictionary_map_DOCUMENT_NAME_with_DOCUMENT_ID = {
    "Tư vấn Retail.csv": "d66be3e8-b010-4f3f-aefb-299c4ffa8cbd",
    "Tư vấn fnb.csv":"7832fb85-db35-4162-9bba-e33bb6744de2",
    "Dùng thử Retail.csv": "86c7f394-529d-4e2c-978f-487fa214d704",
    "Dùng thử fnb.csv": "fe4787d2-90d3-454f-b5a6-433f661e2f57",
    "Bảng giá Retail.csv": "af366da2-b217-41b7-9411-f8b99b23627b",
    "Bảng giá fnb.csv": "e7ca0074-c9b8-4cf9-8f6c-8ba05ec543c3"
    }
    await download_All_CSV_Files_to_local_path()
    await upload_All_CSV_FILE_to_Dify(dictionary_map_DOCUMENT_NAME_with_DOCUMENT_ID)
    return JSONResponse(content=f"Process done in download all CSV files and update all CSV files",status_code=200)




    







