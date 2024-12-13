from fastapi import APIRouter
import httpx

from ..config import get_logger, get_relevant_nse_indices

router = APIRouter()


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
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.178 Safari/537.36',
    }

    params = {
        'view': 'overview',
        'deviceType': 'W',
    }
    mc_gi_url = 'https://priceapi.moneycontrol.com/technicalCompanyData/globalMarket/getGlobalIndicesListingData'
    response = httpx(mc_gi_url, params=params, headers=headers)
    
    return response


@router.get("/indices/")
async def get_indices(symbol:str, 
            startdate: str | None = None, 
            enddate: str | None = None, 
            realtime: bool =False ):
    """
    Args:
        symbol: all returns all global indices
                nse returns all nse relevant indices
                NIFTY 50 returns speific index
        startdate: dd-mm-yyyy format for non realtime data
        enddate: dd-mm-yyyy format for non realtime data
        realtime: Boolean True to get the LTP
                 False gets index data within start and end date range
    """
    
    pass