from typing import Union

from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}




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


def fetch_nse_data(str: symbol, startdate, enddate, interval, period)-> dict{
    
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
        symbol = nifty50
    
    if startdate == None:
        startdate = 0
        
    if enddate == None:
        enddate = 
    
    data = {
        'exch': 'N',
        'tradingSymbol': symbol,
        'fromDate': startdate,
        'toDate': enddate,
        'timeInterval': 5,
        'chartPeriod': 'I',
        'chartStart': 0,      
    }

    response = requests.post('https://charting.nseindia.com//Charts/ChartData/', headers=headers, json=json_data)
    
}


