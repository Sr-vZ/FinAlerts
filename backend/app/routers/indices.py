from fastapi import APIRouter

from ..utils import get_global_indices, get_global_hist_indices
from ..config import get_logger, get_relevant_nse_indices

router = APIRouter()






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
    
    if realtime:
        if symbol.lower() == "all":
            return get_global_indices()
    else:
        return get_global_hist_indices(symbol, startdate, enddate)
        