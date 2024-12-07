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
import httpx
import re
import random
import pandas as pd


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
"Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4",
"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
"Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/600.7.12 (KHTML, like Gecko) Version/8.0.7 Safari/600.7.12",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.8.9 (KHTML, like Gecko) Version/7.1.8 Safari/537.85.17",
"Mozilla/5.0 (iPad; CPU OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H143 Safari/600.1.4",
"Mozilla/5.0 (iPad; CPU OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F69 Safari/600.1.4",
"Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
"Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
"Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
"Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0",
]

def generate_headers(user_agent):
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
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://charting.nseindia.com//Charts/GetEQMasters", headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep="|")
    return df

# TODO
def get_etflist_data():
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://nsearchives.nseindia.com/content/equities/eq_etfseclist.csv", headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep=",")
    return df

# TODO
def get_eqlist_data():
    headers  = generate_headers(random.choice(user_agents))
    response = httpx.get("https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv", headers=headers)
    csv_str = StringIO(response.text)
    df = pd.read_csv(csv_str,sep=",")
    return df