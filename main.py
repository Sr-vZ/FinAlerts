from typing import Union

from fastapi import FastAPI
import requests
import json
from datetime import datetime as datetime
from datetime import timedelta as timedelta
from io import StringIO
import pandas as pd

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/nse_data/")
async def get_nse_data(symbol: str, startdate: str=None, enddate: str=None, interval: int=None):
    if symbol == None:
        symbol = "TCS-EQ"
    return fetch_nse_data(symbol,startdate,enddate,interval)

@app.get("/scripcodes/")
def scripCode(symbol: str=None):
    return get_scrip_code(symbol)


headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json; charset=utf-8',
    'origin': 'https://charting.nseindia.com',
    'sec-ch-ua': '"Opera GX";v="109", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0',
}


def fetch_nse_data(symbol, startdate, enddate, interval=5, period ="I")-> json:
    
    # json_data = {
    #     'exch': 'N',
    #     'tradingSymbol': 'MAPMYINDIA-EQ',
    #     'fromDate': 0,
    #     'toDate': 1719780024,
    #     'timeInterval': 5,
    #     'chartPeriod': 'I',
    #     'chartStart': 0,
    # }
    
    if symbol == None:
        symbol = "TCS-EQ"
    
    if startdate == None:
        startdate = datetime.now() - timedelta(days=7)
        startdate = startdate.strftime('%d-%m-%Y')
    if enddate == None:
        enddate = datetime.now().strftime('%d-%m-%Y')
   
    startdate = datetime.strptime(startdate,'%d-%m-%Y').timestamp()
    enddate = datetime.strptime(enddate,'%d-%m-%Y').timestamp()

    data = {
        'exch': 'N',
        'tradingSymbol': symbol,
        'fromDate': int(startdate),
        'toDate': int(enddate),
        'timeInterval': interval,
        'chartPeriod': 'I',
        'chartStart': 0,      
    }

    response = requests.post('https://charting.nseindia.com//Charts/ChartData/', headers=headers, json=data)

    return response.json()

def get_scrip_code(symbol=None) -> json:
    response = requests.get('https://charting.nseindia.com//Charts/GetEQMasters', headers=headers)
    # print(response.text)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep="|")
    # print(df)
    if symbol in df.values:
        df = df[df['TradingSymbol']==symbol]
        # return json.loads(df[].to_json(orient='records'))
    return json.loads(df.to_json(orient='records'))

def fetch_hist_nse_data(symbol, startdate, enddate, interval=5, period ="I")-> json:
    
   
    if symbol == None:
        symbol = "TCS-EQ"
    
    if startdate == None:
        startdate = datetime.now() - timedelta(days=7)
        startdate = startdate.strftime('%d-%m-%Y')
    if enddate == None:
        enddate = datetime.now().strftime('%d-%m-%Y')
   
    startdate = datetime.strptime(startdate,'%d-%m-%Y').timestamp()
    enddate = datetime.strptime(enddate,'%d-%m-%Y').timestamp()

    data = {
        'exch': 'N',
        'instrType': 'C',
        'tradingSymbol': symbol,
        'fromDate': int(startdate),
        'toDate': int(enddate),
        'timeInterval': interval,
        'chartPeriod': 'I',
        'chartStart': 0,      
        'scripCode': 26000,
        'ulToken': 26000,
    }

    response = requests.post('https://charting.nseindia.com//Charts/symbolhistoricaldata/', headers=headers, json=data)

    return response.json()

