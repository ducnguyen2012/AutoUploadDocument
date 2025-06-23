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
def get_all_document_id(list_of_document_id: list):
    url = "https://dify.sapocorp.vn/v1/datasets/aa75acc4-f2ce-41c1-9671-c4d249d1cbdd/documents"
    header = {
        'Authorization': f"Bearer {API_KEY}"
    }

    response = httpx.get(url=url, headers=header)
    response.raise_for_status()
    response_dict = response.json()
    #! process for get all the id of document
    for document in response_dict['data']:
        print(f"This is my document_id: {document['id']}")
        print(f"This is name of document: {document['data_source_detail_dict']['upload_file']['name']}")
get_all_document_id(list_of_document_id=[])
    
    