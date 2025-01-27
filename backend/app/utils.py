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
from .config import get_logger, get_relevant_nse_indices, get_global_indices_metadata
import requests
# from nsepython import indices
import difflib
import jwt
from bs4 import BeautifulSoup

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
    # TODO: add user_agents in function and make origin as argument
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
    response = httpx.get("https://charting.nseindia.com//Charts/GetEQMasters", 
                         headers=headers, verify=False)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep="|")
    return df


def get_etflist_data():
    """
    Fetch ETF List from NSE
    """
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv", 
                         headers=headers, verify=False)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep=",")
    return df


def get_eqlist_data():
    """
    Fetch Equity List from NSE
    """
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv", 
                         headers=headers, verify=False)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep=",")
    return df


def get_nse_indices_mapping():
    """
    This is to map NSE's weird internal naming of indices 
    which is needed to fetch OHLCV data
    """
    headers = generate_headers(random.choice(user_agents))
    response  = httpx.get("https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json", 
                          headers=headers, verify=False)
    return response.json()

def get_trading_index_name(index_long_name):
    """Gets the trading index name based on the index long name.

    Args:
    index_long_name: The long name of the index.
    data: The list of indices, each with a `Trading_Index_Name` and `Index_long_name`.

    Returns:
    The trading index name, or None if not found.
    """
    headers = generate_headers(random.choice(user_agents))
    response  = httpx.get("https://iislliveblob.niftyindices.com/assets/json/IndexMapping.json", 
                          headers=headers, verify=False)

    for index_data in response.json():
        if index_data['Index_long_name'].upper() == index_long_name.upper():
            return index_data['Trading_Index_Name']
    return None

def get_indices_list():
    """
    fetches NSE indices categories and sectoral indices
    
    """
    headers = generate_headers(random.choice(user_agents))
    response  = httpx.get("https://www.nseindia.com/api/equity-master", 
                          headers=headers, verify=False)
    return response.json()

def get_scrip_code(symbol=None):
    df = get_scrip_data()
    # df.replace('\s+', '_',regex=True,inplace=True)
    df['TradingSymbol'] = df['TradingSymbol'].str.upper()
    df['Description'] = df['Description'].str.upper()
    # print(symbol)
    # print("test: ")
    # print(df[df['TradingSymbol'].str.match("NIFTY 50")])
    # print(df[df['TradingSymbol'] == "NIFTY 50"])
    # print(df[df['TradingSymbol'] == symbol]['ScripCode'])
    symbol = symbol.upper()
    print(symbol)
    # print(df)
    print(difflib.get_close_matches(symbol,df['Description'],n=1))
    closest_match = difflib.get_close_matches(symbol,df['Description'],n=1, cutoff=0.60)[0]
    # print(symbol, closest_match)
    # if df[df['TradingSymbol'] == symbol]['ScripCode'].item() == None:
    #     if len(closest_match) > 0:
    #         closest_match = difflib.get_close_matches(symbol,df['Description'],n=1)[0]
    #     else:
    #         return None
    #     return df[df['Description'] == closest_match]['ScripCode'].item()
    return df[(df['TradingSymbol'] == symbol)|(df['Description'] == symbol)|(df['Description'] == closest_match)]['ScripCode'].item() 

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
    # print(scrip_code)

    headers = generate_headers(random.choice(user_agents))
    response = httpx.post('https://charting.nseindia.com//Charts/symbolhistoricaldata/', 
                          headers=headers,  json=data, verify=False)

    # print(response.text)
    return response.json()


def get_indices_hist_data(index:str, startdate:str, enddate:str):
    
    relevant_indices = get_relevant_nse_indices()
    
    temp = get_indices_list()
    valid_indices = [j for i in list(temp.values()) for j in i]
    if index not in relevant_indices:
        logger.error(f"{index} is not a relevant Index")
        return None
    
    # Validate date format
    try:
        start_date_obj = datetime.strptime(startdate, "%d-%m-%Y")
        end_date_obj = datetime.strptime(enddate, "%d-%m-%Y")
    except ValueError:
        logger.error("Dates should be in dd-mm-yyyy format.")
        return None

    # Validate date range
    # if (end_date_obj - start_date_obj).days > 365:
    #     logger.error("Error: The difference between startdate and enddate should not exceed 365 days.")
    #     return None
    
    if (end_date_obj - start_date_obj).days < 0:
        logger.error("enddate must be later than or equal to startdate.")
        return None

    result =  fetch_hist_nse_data(symbol=get_trading_index_name(index),
                               startdate=startdate,
                               enddate=enddate, 
                               interval=1, period="D")

    result['s'] = index
    df = pd.DataFrame.from_dict(result)
    df.columns = ["index_name","ts","open","high","low","close","volume"]
    # print(df)
    return df
    # headers = generate_headers(random.choice(user_agents))
    # headers['referer'] = 'https://www.nseindia.com/reports-indices-historical-index-data'

    
    # index = index.replace(" ","%20")
    # index_url = "https://www.nseindia.com/api/historical/indicesHistory?indexType=NIFTY%20NEXT%2050&from=01-01-2023&to=31-12-2023"
    # index_url = f"https://www.nseindia.com/api/historical/indicesHistory?indexType={index}&from={startdate}&to={enddate}"
    # # print(index_url)
    # response = httpx.get(index_url, headers=headers)
    # # print(response.text)
    # return response.json()
    

    
# get_indices_hist_data('NIFTY 50', '01-12-2024', '08-12-2024')
# print(indices)

def format_json_data(json_data):
    # Parse JSON data
    # data = json.loads(json_data)
    data = json_data
    headers = [header["name"] for header in data["header"]]
    formatted_output = {}

    for market in data["dataList"]:
        market_name = market["heading"]
        formatted_output[market_name] = []

        # Map each entry in 'data' to the headers
        for row in market["data"]:
            market_entry = {header: value for header, value in zip(headers, row)}
            formatted_output[market_name].append(market_entry)

    return formatted_output

def get_global_indices():
    headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'origin': 'https://www.moneycontrol.com',
    'priority': 'u=1, i',
    'referer': 'https://www.moneycontrol.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.178 Safari/537.36',
    'user-agent': random.choice(user_agents)
    }

    params = {
        'view': 'overview',
        'deviceType': 'W',
    }
    mcgi_url = 'https://priceapi.moneycontrol.com/technicalCompanyData/globalMarket/getGlobalIndicesListingData'
    response = httpx.get(mcgi_url, params=params, headers=headers, verify=False)
    # print(response.json())
    
    return format_json_data(response.json())


def get_global_hist_indices(symbol:str, startdate:str, enddate:str):
    headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'origin': 'https://www.moneycontrol.com',
        'priority': 'u=1, i',
        'referer': 'https://www.moneycontrol.com/',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        # 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.178 Safari/537.36',
        'user-agent': random.choice(user_agents)
    }
    
    try:
        start_date_obj = datetime.strptime(startdate, "%d-%m-%Y")
        end_date_obj = datetime.strptime(enddate, "%d-%m-%Y")
    except ValueError:
        logger.error("Dates should be in dd-mm-yyyy format.")
        return None
    
    if (end_date_obj - start_date_obj).days < 0:
        logger.error("enddate must be later than or equal to startdate.")
        return None
    
    metadata = get_global_indices_metadata(symbol)
    print(metadata, metadata[0])
    if metadata == None:
        logger.error(f"Invalid symbol {symbol}")
        return None
    
    params = {
        'symbol': metadata[0]['symbol'],
        'resolution': '1D',
        'from': int(start_date_obj.timestamp()),
        'to': int(end_date_obj.timestamp()),
        'countback': (end_date_obj - start_date_obj).days,
        'currencyCode': 'USD',
    }
    print(params)
    mcgi_url = 'https://priceapi.moneycontrol.com/globaltechCharts/globalMarket/index/history'
    if metadata[0]['geography'] == "US":
        mcgi_url = 'https://priceapi.moneycontrol.com/globaltechCharts/usMarket/index/history'
    
    
    response = httpx.get(mcgi_url, params=params, headers=headers, verify=False)
    # print(response.text)
    return response.json()

def get_nse_cookies():
    cookie_path = "../../temp/cookie.json"
    with open(cookie_path, 'r') as f:
        cookie = json.load(f)
    temp = jwt.decode(jwt=cookie['nseappid'], key=None, algorithms=['HS256'], options={"verify_signature":False})
    
    

# def get_nse_indices():
#     # headers = generate_headers(random.choice(user_agents))
#     # headers['referer'] = 'https://www.nseindia.com/market-data/live-market-indices'
#     # headers.pop('origin', None)
#     cookies = {
#     'defaultLang': 'en',
#     'nsit': 'hJ0HH5iOKS52RjxAKrHWBBnw',
#     'AKA_A2': 'A',
#     'nseappid': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTczNTkzMzMyNSwiZXhwIjoxNzM1OTQwNTI1fQ.Y2hqAEe3pLhHcj-wjhtmjvJTdRyVIl5MdfTJeqhIB_4',
#     'bm_mi': 'AFDFDCD8F88E17BEB603BE00A0E1A837~YAAQFf7UF1rYhtGTAQAAMnGwLRpKvQA+p/M2wzz5cF/u//5z+AiKOGooDQQQnDqXxEAxCrwqN7r7ZHg+H6g/GqHEt3wGyPwDgEo/3sTv5ZbMwSWb9Wu7bG2cVm9r4PnJhEmM0Yplci9Vi98dlnU77vVWxxIATUr2Uqk9v+7Dic5dDqPSfrPLx1Ob5krcQ0Mqt0Qf4p5f+50mnpaxu9Bf1B2HEiCpEMXdXGEIbn07/ybEuo39SLIHEWCnpjJ+vkgRH/JaJxAU4NcsMjDLHgGRBg2804v79a01O4/SIwU8U3QWUMiCa2KNaFuEwHijEgoDwW1GWP96RLZP010WM9dTP6/uivEMcg1ARfr3nptZtA==~1',
#     'bm_sz': '5A487D87FDDAD99E426686269A54E1A5~YAAQFf7UF1zYhtGTAQAAMnGwLRpkJr+zjEYqP6hLIQsOja6wR1O92rsmQ4IHJBSAoNAQFO15RaxGuwo/X6jc3C8uYWHzxQWSxUIkxqWsB4DQ1ElMznUXpp0EsrYhHs7KvoZ7tjQuu8T+1sPwRE0Q6gD0jg8wy/Vl8bsrLeYojezJbkkOPgVhDUJpmNn6JZo/VsWXLkC7EjC3wyj2sxpm+9oR0xYUSPevVz6a3vZxGwiITYWxk3nSj2cpAALxJkC3Fxzd7+uFb0uBtj9WGFfuZSwmK/LcZbBATLTm5zOmyF5ZYX7N5xSkP0rt2yefk70TqjAf3lmc+FcIhmYQiZhLWtActTpTMGPDNHhC0dK9sjZ3b+TyxphmM1yky+a6L7GWmZgf9dUQt/8xkInsWy5D1ih1jRE=~4535605~4338738',
#     '_abck': '07B1F1F995ACFC756B5CE515B94E43DF~0~YAAQFf7UF+zYhtGTAQAA9YKwLQ3k942YUr6S14R+dCXdA5dormCivz5sfecVA7mD7JJ/MxyONUOjQUgSb6vBqfkv0QWYCf2barybjRt3DJTWBlj94+/UD4nclZp6z7ssJyIxYVDJ5S04TM07h9x/k03Hm2E9LDoEvdYYAmtRwjW0AiIWO4E51JCCENPd3qOvhqxQu3IE7mfsmn/P5En3rK4S8AJaKJNURa5m1sSHy+mCwV1YwdUENBOmZ/1HXrw2aM58uxkVFQaYD7rY9vt98XzaNfCdEMbetTQpEzafL1FLOFQRC01ScWPqtPGrTg0LcJggpyErg4mo7Oqatc/Xt9If3fI4bZ6J0pDtLAZ8HF9Kb+d18hXa2Rigrtt7yPjCVkTek2U/8wJjp67X1sv8RnYIqC9WcfUaDlOmlaQlh4SI+QwNUomM1eIZuJP1Z9pN7ZitHyl85RIe6M8mtFbAAGle1KerDysJHAFsLVQZmcV+b7cxahczZsiZF3vlgMAT6w==~-1~||0||~-1',
#     'bm_sv': 'B87BFA33D08467F49BC911B882C0BB93~YAAQL3LBF3ZTZumTAQAAIKiwLRpm8EsOGqx0PE6TAwoAzmgXVns6crDpZZkQa/vnb+2TUXbaQ52pgN4Fw5KRQcTZcRt4cb6xHR2Gd5UyUXvBCSwFc+/JBAqRStJPmcFRdSUYMCLfnb/rG7JUJNbi4Ku0kepq7BOz6/yyMOxam19G0DZReit4sGKQHOL3hhGM83odNb2VP90Z7oSFJCETShrgLW6p1bzWMCtfCiVC1xEo8oC27Yh4KzGnPZsc+OLpm8sl~1',
#     'ak_bmsc': 'FBEBC972FE720F65011D243F87D79872~000000000000000000000000000000~YAAQFf7UFxjahtGTAQAAhbGwLRpQUwfEaOyY0Gq3K3LNx6Y6E/YVLl1jFxwNgcu4phhSLTJfaatZsavLFUMu8shYHI2d5V4l2+AyMCw1ZmrlqeGFIOi+GxGBSgKbay0R2Awk/0Y7d3xTsrdFVcXYiFsVi/1mJ1AAPABhaeULM4Nop4hW62kEQxmsH7kMrvtFtPAtWWkk2d+h3IXX+BXef2PDtSWtOMfmXqWbox/Oh0ux5ELcfQfsaP+ps+3jYZzCATpHG+EUQ+aT9JUeC4F5C3+40GfBXqn1UiLw1o2+GtwD6+ge9lVWp/aGq6RxFtNv6Hx/Fu3ztbWAvqgyyNrEmwlhxdm/dxFtuLfIyMTIZhBpnpogGryQkw7CUud70I+9FH3TQTdY7n73IYZ6qsL9/C9FNyHnP4wTZeowbyQsTeQfDszInZHR6G0SLFvBogVKHMZDrLW65pfIrveC5nJo',
#     }
#     headers = {
#     'accept': '*/*',
#     'accept-language': 'en-US,en;q=0.9',
#     # 'cookie': 'defaultLang=en; nsit=hJ0HH5iOKS52RjxAKrHWBBnw; AKA_A2=A; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTczNTkzMzMyNSwiZXhwIjoxNzM1OTQwNTI1fQ.Y2hqAEe3pLhHcj-wjhtmjvJTdRyVIl5MdfTJeqhIB_4; bm_mi=AFDFDCD8F88E17BEB603BE00A0E1A837~YAAQFf7UF1rYhtGTAQAAMnGwLRpKvQA+p/M2wzz5cF/u//5z+AiKOGooDQQQnDqXxEAxCrwqN7r7ZHg+H6g/GqHEt3wGyPwDgEo/3sTv5ZbMwSWb9Wu7bG2cVm9r4PnJhEmM0Yplci9Vi98dlnU77vVWxxIATUr2Uqk9v+7Dic5dDqPSfrPLx1Ob5krcQ0Mqt0Qf4p5f+50mnpaxu9Bf1B2HEiCpEMXdXGEIbn07/ybEuo39SLIHEWCnpjJ+vkgRH/JaJxAU4NcsMjDLHgGRBg2804v79a01O4/SIwU8U3QWUMiCa2KNaFuEwHijEgoDwW1GWP96RLZP010WM9dTP6/uivEMcg1ARfr3nptZtA==~1; bm_sz=5A487D87FDDAD99E426686269A54E1A5~YAAQFf7UF1zYhtGTAQAAMnGwLRpkJr+zjEYqP6hLIQsOja6wR1O92rsmQ4IHJBSAoNAQFO15RaxGuwo/X6jc3C8uYWHzxQWSxUIkxqWsB4DQ1ElMznUXpp0EsrYhHs7KvoZ7tjQuu8T+1sPwRE0Q6gD0jg8wy/Vl8bsrLeYojezJbkkOPgVhDUJpmNn6JZo/VsWXLkC7EjC3wyj2sxpm+9oR0xYUSPevVz6a3vZxGwiITYWxk3nSj2cpAALxJkC3Fxzd7+uFb0uBtj9WGFfuZSwmK/LcZbBATLTm5zOmyF5ZYX7N5xSkP0rt2yefk70TqjAf3lmc+FcIhmYQiZhLWtActTpTMGPDNHhC0dK9sjZ3b+TyxphmM1yky+a6L7GWmZgf9dUQt/8xkInsWy5D1ih1jRE=~4535605~4338738; _abck=07B1F1F995ACFC756B5CE515B94E43DF~0~YAAQFf7UF+zYhtGTAQAA9YKwLQ3k942YUr6S14R+dCXdA5dormCivz5sfecVA7mD7JJ/MxyONUOjQUgSb6vBqfkv0QWYCf2barybjRt3DJTWBlj94+/UD4nclZp6z7ssJyIxYVDJ5S04TM07h9x/k03Hm2E9LDoEvdYYAmtRwjW0AiIWO4E51JCCENPd3qOvhqxQu3IE7mfsmn/P5En3rK4S8AJaKJNURa5m1sSHy+mCwV1YwdUENBOmZ/1HXrw2aM58uxkVFQaYD7rY9vt98XzaNfCdEMbetTQpEzafL1FLOFQRC01ScWPqtPGrTg0LcJggpyErg4mo7Oqatc/Xt9If3fI4bZ6J0pDtLAZ8HF9Kb+d18hXa2Rigrtt7yPjCVkTek2U/8wJjp67X1sv8RnYIqC9WcfUaDlOmlaQlh4SI+QwNUomM1eIZuJP1Z9pN7ZitHyl85RIe6M8mtFbAAGle1KerDysJHAFsLVQZmcV+b7cxahczZsiZF3vlgMAT6w==~-1~||0||~-1; bm_sv=B87BFA33D08467F49BC911B882C0BB93~YAAQL3LBF3ZTZumTAQAAIKiwLRpm8EsOGqx0PE6TAwoAzmgXVns6crDpZZkQa/vnb+2TUXbaQ52pgN4Fw5KRQcTZcRt4cb6xHR2Gd5UyUXvBCSwFc+/JBAqRStJPmcFRdSUYMCLfnb/rG7JUJNbi4Ku0kepq7BOz6/yyMOxam19G0DZReit4sGKQHOL3hhGM83odNb2VP90Z7oSFJCETShrgLW6p1bzWMCtfCiVC1xEo8oC27Yh4KzGnPZsc+OLpm8sl~1; ak_bmsc=FBEBC972FE720F65011D243F87D79872~000000000000000000000000000000~YAAQFf7UFxjahtGTAQAAhbGwLRpQUwfEaOyY0Gq3K3LNx6Y6E/YVLl1jFxwNgcu4phhSLTJfaatZsavLFUMu8shYHI2d5V4l2+AyMCw1ZmrlqeGFIOi+GxGBSgKbay0R2Awk/0Y7d3xTsrdFVcXYiFsVi/1mJ1AAPABhaeULM4Nop4hW62kEQxmsH7kMrvtFtPAtWWkk2d+h3IXX+BXef2PDtSWtOMfmXqWbox/Oh0ux5ELcfQfsaP+ps+3jYZzCATpHG+EUQ+aT9JUeC4F5C3+40GfBXqn1UiLw1o2+GtwD6+ge9lVWp/aGq6RxFtNv6Hx/Fu3ztbWAvqgyyNrEmwlhxdm/dxFtuLfIyMTIZhBpnpogGryQkw7CUud70I+9FH3TQTdY7n73IYZ6qsL9/C9FNyHnP4wTZeowbyQsTeQfDszInZHR6G0SLFvBogVKHMZDrLW65pfIrveC5nJo',
#     'priority': 'u=1, i',
#     'referer': 'https://www.nseindia.com/market-data/live-market-indices',
#     'sec-ch-ua': '"Chromium";v="130", "Opera GX";v="115", "Not?A_Brand";v="99"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'empty',
#     'sec-fetch-mode': 'cors',
#     'sec-fetch-site': 'same-origin',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 OPR/115.0.0.0',
#     }
#     response = httpx.get('https://www.nseindia.com/api/allIndices', headers=headers, cookies=cookies, verify=False)
#     print(response.text)
#     return response.json()

def get_nse_indices():
    # headers = generate_headers(random.choices(user_agents))
    # headers['accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
    # headers['origin'] = 'https://www.moneycontrol.com/'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Chromium";v="130", "Opera GX";v="115", "Not?A_Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.6723.170 Safari/537.36',
    }
    params = {
        'deviceType': 'web',
        'exName': 'N',
        'indicesID': '23',
        'selTab': 'o',
        'subTabOT': 'o',
        'subTabOPL': 'cl',
    }
    # print(headers)
    
    
    response = httpx.get(
        'https://www.moneycontrol.com/markets/indian-indices/changeTableData',params=params,
        headers=headers,verify=False
    )
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "tbl_indices"})
    if table:
        # Extract table headers
        headers = [th.text.strip() for th in table.find("thead").find_all("th")]
        data = []
        # Extract table rows
        for index_type in ["Key Indices", "Sectoral Indices", "Other Indices"]:
            rows = table.find("tbody").find_all("tr", {"data-type": index_type})
            

            for row in rows:
                cells = row.find_all("td")
                row_data = {headers[i]: cells[i].text.strip() for i in range(len(cells))}
                data.append(row_data)

        # Convert the extracted data to JSON
        # json_data = json.dumps(data, indent=4)
    return data