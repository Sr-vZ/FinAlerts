# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings

# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base: DeclarativeMeta = declarative_base()
# database.py
from sqlalchemy import create_engine, MetaData, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from datetime import date, timedelta
from .models import Base, ScripCode, ETFList, EQList

from .utils import get_scrip_data, get_etflist_data, get_eqlist_data, get_indices_list, get_indices_hist_data

from .config import get_logger

DATABASE_URL = "sqlite:///./test.db"  # You can use any database here

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base.metadata.create_all(bind=engine)


logger = get_logger()

def init_tables(db = get_db())  ->  None:
    """
    Populate the tables with data
    """
    logger.info("Populating DB with initial data...")
    logger.info("Caching scripcodes...")
    df = get_scrip_data()
    
    df.columns = [ "scrip_code",     "symbol",               "description",  "instrument_type"]
    df.to_sql("scripcodes", engine, if_exists="replace", index=False)
 
  
    logger.info("Caching etflist...")
    df = get_etflist_data()
    df.columns = [ "symbol","description","securtiy_name","date_of_listing","market_lot","isin","face_value"]
    df.to_sql("etflist", engine, if_exists="replace",index=False)

    
    logger.info("Caching equity list...")
    df = get_eqlist_data()  
    df.columns = [ "symbol","description",  "series", "date_of_listing","paid_up_value","market_lot", "isin","face_value"]
    df.to_sql("equitylist", engine, if_exists="replace",index=False)
    
    logger.info("Caching Indices...")
    indices = get_indices_list()
    # print(indices.keys())
    for key in indices.keys():
        for index in indices[key]:
            print(key, index)
            end_date = date.today()
            start_date = end_date - timedelta(days=365)
            df = get_indices_hist_data(index,start_date.strftime("%d-%m-%Y"),end_date.strftime("%d-%m-%Y"))
            print(df)
        
        
        
    # indices = indices.values()
    

init_tables()

# def get_scrip_code(symbol:str):
#     db = get_db()
#     scripcode_table = ScripCode.__table__
#     query = select([scripcode_table]).where(scripcode_table.symbol.like(f"%{symbol}%"))
#     result = db.execute(query).fetchone()

#     if result:
#         return ScripCode(**result)  # Unpack row data into a ScripCode object
#     else:
#         return None
