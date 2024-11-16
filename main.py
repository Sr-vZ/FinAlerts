import re
from typing import Union

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import requests
import json
import os
from datetime import datetime as datetime
from datetime import timedelta as timedelta
from io import StringIO
import pandas as pd
import uvicorn
import sqlite3
import logging
import httpx

def create_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    term_handler = logging.StreamHandler()
    term_handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(term_handler)
    return logger 

logger = create_logger('finalerts', 'finalerts.log', logging.DEBUG)

app = FastAPI()

templates = Jinja2Templates(directory="ui")

db_name = "nse_local_cache.db"

@app.get("/")
def dashboard(request: Request):
    # return {"Hello": "World"}
    return templates.TemplateResponse("dashboard.html",{"request":request})


@app.get("/api/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/api/nse_data/")
async def get_nse_data(symbol: str, startdate: str=None, enddate: str=None, interval: int=5):
    if symbol == None:
        symbol = "TCS-EQ"
    return fetch_hist_nse_data(symbol,startdate,enddate,interval)
    

@app.get("/api/scripcodes/")
def scripCode(symbol: str=None):
    return get_scrip_code(symbol)


@app.get("/api/test/")
def nse_indices():
    # return fetch_nse_indices_stocklist()
    return init_nifty50_data()


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
    logging.info(f"Intraday response for {symbol} {response.json()}")

    return response.json()

def get_scrip_code(symbol=None) -> json:
    # csv_filepath = './temp/scripcode.csv'
    nse_local_cache = "./nse_local_cache.db"
    conn = sqlite3.connect(nse_local_cache)
    if os.path.exists(nse_local_cache):
        # df = pd.read_csv(csv_filepath,sep=",")  
        df = pd.read_sql_query("SELECT * from eq_scrip_codes", conn)
    else:
        # response = requests.get('https://charting.nseindia.com//Charts/GetEQMasters', headers=headers)

        # csv_str = StringIO(response.text)
        # df = pd.read_csv(csv_str,sep="|")
    
        # df.to_csv(csv_filepath, index=False)
        logger.warning(f"{nse_local_cache} missing! rebuilding local cache...")
        init_local_cache()  
        df = pd.read_sql_query("SELECT * from eq_scrip_codes", conn)
    
    if symbol in df.values:
        df = df[df['TradingSymbol']==symbol]
    
    return json.loads(df.to_json(orient='records'))

def fetch_hist_nse_data(symbol, startdate, enddate, interval: int=5, period ="D")-> json:
    """
    Args:
        period = "I" for intra "D" for daily "W" for weekly "M" for monthly
        interval = "1,3,5,10,15,30,60" for intra
        interval = "1" for period=["D","W","M"]
        startdate = "dd-mm-yyyy"
        enddate = "dd-mm-yyyy"
    Returns:
        json
    
    """
   
    if symbol == None:
        symbol = "TCS-EQ"
    
    if startdate == None:
        startdate = datetime.now() - timedelta(days=7)
        startdate = startdate.strftime('%d-%m-%Y')
    if enddate == None:
        enddate = datetime.now().strftime('%d-%m-%Y')
   
    startdate = datetime.strptime(startdate,'%d-%m-%Y').timestamp()
    enddate = datetime.strptime(enddate,'%d-%m-%Y').timestamp()
    
    scrip_code = get_scrip_code(symbol)[0]['ScripCode']

    data = {
        'exch': 'N',
        'instrType': 'C',
        # 'tradingSymbol': symbol,
        'fromDate': int(startdate),
        'toDate': int(enddate),
        'timeInterval': interval,
        'chartPeriod': period,
        'chartStart': 0,      
        'scripCode': scrip_code,
        'ulToken': scrip_code,
    }

    response = requests.post('https://charting.nseindia.com//Charts/symbolhistoricaldata/', headers=headers, json=data)

    return response.json()



def create_stock_table(conn, symbol):
    """Creates a table for the given symbol with appropriate columns."""
    cursor = conn.cursor()
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {symbol} (
        ts INTEGER PRIMARY KEY,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER
    )""")
    logger.info(f"{symbol} Table created")
    conn.commit()

def insert_stock_data(conn, symbol, data):
    """Inserts data into the specified table."""
    cursor = conn.cursor()
    for row in data:
        ts, open_price, high_price, low_price, close_price, volume = row
        cursor.execute(f"""
            INSERT OR REPLACE INTO {symbol} (ts, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (ts, open_price, high_price, low_price, close_price, volume))
    logger.info(f"Data {data} inserted to {symbol} Table")
    conn.commit()


def init_nifty50_data():
    nifty50list = "https://nsearchives.nseindia.com/content/indices/ind_nifty50list.csv"
    temp_filepath = "./temp/ind_nifty50list.csv"
    res = httpx.get(nifty50list, timeout=20, headers=headers)
    with open(temp_filepath, "wb") as f:
        f.write(res.content)
    
    df = pd.read_csv(temp_filepath)
    nifty_50_data =[]
    st_date = datetime.now()- timedelta(days=30)
    end_date = datetime.now()
    st_date = st_date.strftime('%d-%m-%Y')
    end_date = end_date.strftime('%d-%m-%Y')
    for symbol in df["Symbol"]:
        symbol = re.sub(r'[\W_]+','_',symbol)
        nifty_50_data.append({
            symbol:fetch_hist_nse_data(symbol=f"{symbol}-EQ", startdate=st_date, enddate=end_date, interval=1, period="D")
        })
        
    # return json.loads(df["Symbol"].to_json())
    conn = sqlite3.connect(db_name)
    # for symbol, stock_data in nifty_50_data.items():
    for item in nifty_50_data:
        for symbol, stock_data in item.items():
            create_stock_table(conn, symbol)
            timestamp_data = stock_data['t']
            open_data = stock_data['o']
            high_data = stock_data['h']
            low_data = stock_data['l']
            close_data = stock_data['c']
            volume_data = stock_data['v']

            data_to_insert = zip(timestamp_data, open_data, high_data, low_data, close_data, volume_data)
            insert_stock_data(conn, symbol, data_to_insert)

    conn.close()
    
    return nifty_50_data


def fetch_nse_indices_stocklist(index='NIFTY 50'):
    indices = ["NIFTY 50", "NIFTY NEXT 50", "NIFTY 100", "NIFTY 200", "NIFTY MIDCAP 50"]
    if not index in indices:
        logging.error(f"{index} is not valid index. Select among {indices}")
        return None
    params = {
    'index': index,
    }

    headers['origin'] = "https://www.nseindia.com/"
    response = requests.get('https://www.nseindia.com/api/equity-stockIndices', params=params, headers=headers)
    logger.info(response)
    # df = pd.read_json(response.json())
    return json.loads(response.json())
    
    

def initialize_db(db_name, table_name, columns, values):
    """
    Initializes a local SQLite database and populates a table with the given values.

    Args:
        db_name (str): The name of the database file.
        table_name (str): The name of the table to create.
        columns (list): A list of column names.
        values (list): A list of tuples, each representing a row of values.

    Returns:
        None
    """

    if os.path.exists(db_name):
        logging.info(f"Database '{db_name}' already exists. Using existing database.")
        conn = sqlite3.connect(db_name)
    else:
        logging.info(f"Creating new database '{db_name}'")
        conn = sqlite3.connect(db_name)

        # Create the table if it doesn't exist
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(f'{col} TEXT' for col in columns)}
            )
        """)

        # Insert values into the table
        cursor.executemany(f"""
            INSERT INTO {table_name} VALUES ({', '.join(['?'] * len(columns))})
        """, values)

        conn.commit()
    conn.close()

def init_local_cache():
    db_name = "nse_local_cache.db"
    table_name = "eq_scrip_codes"
    # columns = ["ts","open","high","low","close"]
    columns = ["ScripCode","TradingSymbol","Description","InstrumentType"]
    
    response = requests.get('https://charting.nseindia.com//Charts/GetEQMasters', headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep="|")
    values = df.values
    initialize_db(db_name, table_name, columns, values)
    table_name = "nifty_50_daily"
    columns = ["TS","TradingSymbol","Open","High","Low","Close"]


app_ui = FastAPI(title="FinAlerts UI")

# app.mount("/api", api_app)
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")

if __name__ == "__main__":
    init_local_cache()
    uvicorn.run(app, host="0.0.0.0", port=8000)
    