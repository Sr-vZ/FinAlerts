# from passlib.context import CryptContext
# # from jose import jwt
# import jwt
# from datetime import datetime, timedelta
# from app.config import settings

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def hash_password(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def create_access_token(data: dict) -> str:
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

from io import StringIO
import json
import httpx
import re
import random
import pandas as pd
from datetime import datetime
from .config import get_logger
import requests


logger = get_logger()


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

user_agents = [
"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/8.0.8 Safari/600.8.9",
# "Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
"Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
# "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
# "Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
# "Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
"Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
# "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
# "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
# "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
# "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0",
]

def generate_headers(user_agent):
    """
    To rotate the user agent to prevent getting IP banned
    """
    # Define a function to parse the sec-ch-ua from the user-agent
    def parse_sec_ch_ua(user_agent):
        # Extract browser info (simplified for common browsers)
        browsers = [
            ("Opera", "Opera"),
            ("OPR", "Opera"),
            ("Chrome", "Chromium"),
            ("Safari", "Safari"),
            ("Firefox", "Firefox"),
            ("Trident", "Internet Explorer"),
            ("Edge", "Edge")
        ]
        sec_ch_ua = []
        for identifier, name in browsers:
            if identifier in user_agent:
                version_match = re.search(rf"{identifier}/([\d.]+)", user_agent)
                version = version_match.group(1).split('.')[0] if version_match else "0"
                sec_ch_ua.append(f'"{name}";v="{version}"')
        
        # Add "Not:A-Brand" to mimic realistic headers
        sec_ch_ua.append('"Not:A-Brand";v="99"')
        return ', '.join(sec_ch_ua)

    # Check if the user agent is mobile
    def is_mobile(user_agent):
        return "Mobile" in user_agent or "iPad" in user_agent or "CPU OS" in user_agent

    # Generate dynamic headers
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json; charset=utf-8',
        'origin': 'https://charting.nseindia.com',
        'sec-ch-ua': parse_sec_ch_ua(user_agent),
        'sec-ch-ua-mobile': '?1' if is_mobile(user_agent) else '?0',
        'sec-ch-ua-platform': '"Windows"' if 'Windows' in user_agent else '"Mac OS X"' if 'Macintosh' in user_agent else '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': user_agent,
    }
    return headers


def get_scrip_data():
    """
    Fetch scripcodes from NSE
    """
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://charting.nseindia.com//Charts/GetEQMasters", headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep="|")
    return df


def get_etflist_data():
    """
    Fetch ETF List from NSE
    """
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv", headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep=",")
    return df


def get_eqlist_data():
    """
    Fetch Equity List from NSE
    """
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv", 
                         headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep=",")
    return df

# TODO
def get_indices_list():
    """
    fetches NSE indices categories and sectoral indices
    """
    headers = generate_headers(random.choice(user_agents))
    response  = httpx.get("https://www.nseindia.com/api/equity-master", headers=headers)
    return response.json()

def get_scrip_code(symbol=None):
    df = get_scrip_data()
    # df.replace('\s+', '_',regex=True,inplace=True)
    df['TradingSymbol'] = df['TradingSymbol'].str.upper()
    # print(symbol)
    # print("test: ")
    # print(df[df['TradingSymbol'].str.match("NIFTY 50")])
    # print(df[df['TradingSymbol'] == "NIFTY 50"])
    # print(df[df['TradingSymbol'] == symbol]['ScripCode'])
    return df[df['TradingSymbol'] == symbol]['ScripCode'].item() 

def fetch_hist_nse_data(symbol, startdate, enddate, interval: int=5, period ="D"):
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
        # startdate = datetime.now() - timedelta(days=7)
        startdate = startdate.strftime('%d-%m-%Y')
    if enddate == None:
        enddate = datetime.now().strftime('%d-%m-%Y')
   
    startdate = datetime.strptime(startdate,'%d-%m-%Y').timestamp()
    enddate = datetime.strptime(enddate,'%d-%m-%Y').timestamp()
    
    scrip_code = get_scrip_code(symbol)

    data = {
        'exch': 'N',
        'instrType': 'C',
        'fromDate': int(startdate),
        'toDate': int(enddate),
        'timeInterval': interval,
        'chartPeriod': period,
        'chartStart': 0,      
        'scripCode': scrip_code,
        'ulToken': scrip_code,
    }
    print(scrip_code)

    headers = generate_headers(random.choice(user_agents))
    response = requests.post('https://charting.nseindia.com//Charts/symbolhistoricaldata/', 
                          headers=headers,  json=data)

    # print(response.text)
    return response.json()


def get_indices_hist_data(index:str, startdate:str, enddate:str):
    # Validate date format
    try:
        start_date_obj = datetime.strptime(startdate, "%d-%m-%Y")
        end_date_obj = datetime.strptime(enddate, "%d-%m-%Y")
    except ValueError:
        logger.error("Error: Dates should be in dd-mm-yyyy format.")
        return None

    # Validate date range
    # if (end_date_obj - start_date_obj).days > 365:
    #     logger.error("Error: The difference between startdate and enddate should not exceed 365 days.")
    #     return None

    if (end_date_obj - start_date_obj).days < 0:
        logger.error("enddate must be later than or equal to startdate.")
        return None

    result =  fetch_hist_nse_data(symbol=index,
                               startdate=startdate,
                               enddate=enddate, 
                               interval=1, period="D")

    result['s'] = index
    df = pd.DataFrame.from_dict(result)
    df.columns = ["index","ts","open","high","low","close","volume"]
    # print(df)
    return df
    # headers = generate_headers(random.choice(user_agents))
    # headers['referer'] = 'https://www.nseindia.com/reports-indices-historical-index-data'
    # temp = get_indices_list()
    # valid_indices = [j for i in list(temp.values()) for j in i]
    # if index not in valid_indices:
    #     logger.error(f"{index} is not a valid Index")
    #     return None
    
    # index = index.replace(" ","%20")
    # index_url = "https://www.nseindia.com/api/historical/indicesHistory?indexType=NIFTY%20NEXT%2050&from=01-01-2023&to=31-12-2023"
    # index_url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index}&from={startdate}&to={enddate}"
    # # print(index_url)
    # response = httpx.get(index_url, headers=headers)
    # # print(response.text)
    # return response.json()
    

    
get_indices_hist_data('NIFTY 50', '01-12-2024', '08-12-2024')
