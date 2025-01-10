from fastapi import APIRouter

from ..utils import get_global_indices, get_global_hist_indices, get_nse_indices
from ..config import get_logger, get_relevant_nse_indices
from ..database import db_get_table_names, db_get_index_data

router = APIRouter()






@router.get("/indices/")
async def get_indices(symbol:str, 
            startdate: str | None = None, 
            enddate: str | None = None, 
            realtime: bool =False,
            # suggestions: bool = False
            ):
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
    tables = db_get_table_names()
    # if suggestions:
    #     return [t.replace("_", " ") for t in tables]
    if realtime:
        if symbol.lower() == "all":
            return get_global_indices()
    else:
        # tables = db_get_table_names()
        formatted_symbol = symbol.upper().replace(" ","_")
        if formatted_symbol in tables:
            return db_get_index_data(formatted_symbol, startdate, enddate)
        return get_global_hist_indices(symbol, startdate, enddate)
        
        
@router.get("/nse_indices")
async def fetch_nse_indices(symbol:str):
    data = get_nse_indices()
    if symbol=="all":
        return data
    matches = []
    for item in data:                
        if item['Name'].lower().replace(" ","") == symbol.lower().replace(" ",""):
            return item
        if ":" in symbol:
            symbols = symbol.split(":")
            for sym in symbols:
                if item['Name'].lower().replace(" ","") == sym.lower().replace(" ",""):
                    matches.append(item)
        return matches

            