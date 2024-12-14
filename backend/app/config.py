from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "FastAPI App"
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

settings = Settings()

import logging

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

def get_logger():
    return logger

# TODO: add scripcodes as well
def get_relevant_nse_indices() -> list:
    relevant_indices = [
        "NIFTY 50",
        "NIFTY NEXT 50",
        "NIFTY MIDCAP 50",
        "NIFTY MIDCAP 100",
        "NIFTY MIDCAP 150",
        "NIFTY SMALLCAP 50",
        "NIFTY SMALLCAP 100",
        "NIFTY SMALLCAP 250",
        "NIFTY MIDSMALLCAP 400",
        "NIFTY 100",
        "NIFTY 200",
        "NIFTY500 MULTICAP 50:25:25",
        "NIFTY LARGEMIDCAP 250",
        "NIFTY MIDCAP SELECT",
        "NIFTY TOTAL MARKET",
        "NIFTY MICROCAP 250",
        "NIFTY 500",
        "NIFTY AUTO",
        "NIFTY BANK",
        "NIFTY ENERGY",
        "NIFTY FINANCIAL SERVICES",
        "NIFTY FINANCIAL SERVICES 25/50",
        "NIFTY FMCG",
        "NIFTY IT",
        "NIFTY MEDIA",
        "NIFTY METAL",
        "NIFTY PHARMA",
        "NIFTY PSU BANK",
        "NIFTY REALTY",
        "NIFTY PRIVATE BANK",
        "NIFTY HEALTHCARE INDEX",
        "NIFTY CONSUMER DURABLES",
        "NIFTY OIL & GAS",
        "NIFTY MIDSMALL HEALTHCARE",
        "NIFTY COMMODITIES",
        "NIFTY INDIA CONSUMPTION",
        "NIFTY CPSE",
        "NIFTY INFRASTRUCTURE",
        "NIFTY MNC",
        "NIFTY GROWTH SECTORS 15",
        "NIFTY PSE",
        "NIFTY SERVICES SECTOR",
        "NIFTY100 LIQUID 15",
        "NIFTY MIDCAP LIQUID 15",
        "NIFTY INDIA DIGITAL",
        "NIFTY100 ESG",
        "NIFTY INDIA MANUFACTURING",
        "NIFTY INDIA CORPORATE GROUP INDEX - TATA GROUP 25% CAP",
        "NIFTY500 MULTICAP INDIA MANUFACTURING 50:30:20",
        "NIFTY500 MULTICAP INFRASTRUCTURE 50:30:20",
        "NIFTY INDIA DEFENCE",
        "NIFTY INDIA TOURISM",
        "NIFTY CAPITAL MARKETS",
        "NIFTY DIVIDEND OPPORTUNITIES 50",
        "NIFTY50 VALUE 20",
        "NIFTY100 QUALITY 30",
        "NIFTY50 EQUAL WEIGHT",
        "NIFTY100 EQUAL WEIGHT",
        "NIFTY100 LOW VOLATILITY 30",
        "NIFTY ALPHA 50",
        "NIFTY200 QUALITY 30",
        "NIFTY ALPHA LOW-VOLATILITY 30",
        "NIFTY200 MOMENTUM 30",
        "NIFTY MIDCAP150 QUALITY 50",
        "NIFTY200 ALPHA 30",
        "NIFTY MIDCAP150 MOMENTUM 50",
        "NIFTY500 MOMENTUM 50",
        "NIFTY MIDSMALLCAP400 MOMENTUM QUALITY 100",
        "NIFTY SMALLCAP250 MOMENTUM QUALITY 100",
        "NIFTY TOP 10 EQUAL WEIGHT"
    ]
    return relevant_indices

def search_metadata(data, search_term):
    """
    Search for a term in the 'symbol' or 'name' keys of JSON data.

    Args:
        data (list): List of dictionaries containing market data.
        search_term (str): The term to search for.

    Returns:
        list: A list of matching JSON objects.
    """
    # Convert search_term to lowercase for case-insensitive matching
    search_term_lower = search_term.lower()
    return [
        entry for entry in data
        if search_term_lower in entry["symbol"].lower() or 
        search_term_lower in entry["name"].lower() or 
        search_term_lower in entry["geography"].lower()
    ]


def get_global_indices_metadata(search_term: str|None = None):
    data = [
        {
            "symbol": "de;qx",
            "name": "DAX",
            "geography": "EU",
        },
        {
            "symbol": "gb;FTSE",
            "name": "FTSE",
            "geography": "EU",
        },
        {
            "symbol": "fr;CAC",
            "name": "CAC",
            "geography": "EU",
        },
        {
            "symbol": "in;gsx",
            "name": "GIFT NIFTY",
            "geography": "ASIA",
        },        
        {
            "symbol": "JP;N225",
            "name": "NIKKEI 225",
            "geography": "ASIA",
        },
        {
            "symbol": "sg;STII",
            "name": "Straits Times",
            "geography": "ASIA",
        },
        {
            "symbol": "cn;hsi",
            "name": "Hang Seng",
            "geography": "ASIA",
        },
        {
            "symbol": "tw;IXTA",
            "name": "Taiwan Weighted",
            "geography": "ASIA",
        },
        {
            "symbol": "kr;KSPI",
            "name": "KOSPI",
            "geography": "ASIA",
        },       
        {
            "symbol": "th;SETI",
            "name": "SET Composite",
            "geography": "ASIA",
        }, 
        {
            "symbol": "id;JSC",
            "name": "Jakarta Composite",
            "geography": "ASIA",
        },        
        {
            "symbol": "cn;shi",
            "name": "Shanghai Composite",
            "geography": "ASIA",
        },         
        {
            "symbol": "INDU:IND",
            "name": "Dow Jones",
            "geography": "US",
        }, 
        {
            "symbol": "SPX:IND",
            "name": "S&P 500",
            "geography": "US",
        },
        {
            "symbol": "CCMP:IND",
            "name": "Nasdaq",
            "geography": "US",
        },          
    ]
    if search_term:
        return search_metadata(data, search_term)
    else:
        return data