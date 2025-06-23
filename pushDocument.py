import httpx
import os
import sys
import csv
from dotenv import load_dotenv

load_dotenv()

JSON_KEY = os.getenv("JSON_KEY")
API_KEY = os.getenv("API_KEY")
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']


creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
client = gspread.authorize(creds)

# Mở Google Sheet theo tên và chọn sheet đầu tiên
sheets = client.open_by_url("https://docs.google.com/spreadsheets/d/1_nlZzcJTL2NkYX8mG9ltDWoNx3WiSEGyXmzdMxPSel0/edit?gid=0#gid=0").worksheets()

for sheet in sheets:
    '''
    Remember first column is 1 not zero
    '''
    print(f"Save sheet: {sheet.title}")
    all_data = sheet.get_all_values()
    csv_file_name = f"{sheet.title}.csv"

    with open(csv_file_name,'w',encoding='utf-8',newline='') as file:
        writer = csv.writer(file)
        writer.writerows(all_data)






