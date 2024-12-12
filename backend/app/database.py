# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings

# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base: DeclarativeMeta = declarative_base()
# database.py
from sqlalchemy import create_engine, MetaData, select, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from datetime import date, timedelta
import pandas as pd
from .models import Base, ScripCode, ETFList, EQList

from .utils import get_scrip_data, get_etflist_data, \
    get_eqlist_data, get_indices_list, get_indices_hist_data,\
    get_nse_indices_mapping, get_trading_index_name

from .config import get_logger, get_relevant_nse_indices

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

def check_table_exists(engine, table_name):
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def append_if_needed(table_name, df, date_col, engine):
    if check_table_exists(engine, table_name):
        # Read existing data
        existing_df = pd.read_sql_table(table_name, con=engine)
        if not existing_df.empty:
            last_date = pd.to_datetime(existing_df[date_col]).max()
            today = pd.to_datetime(date.today())
            if last_date >= today:
                logger.info(f"Table '{table_name}' is up to date.")
                return
    else:
        logger.info(f"Table '{table_name}' does not exist. Creating it.")
    df.to_sql(table_name, engine, if_exists="append", index=False)

def init_tables(db = get_db())  ->  None:
    """
    Populate the tables with data
    """
    logger.info("Populating DB with initial data...")
    logger.info("Caching scripcodes...")
    if check_table_exists(engine, "scripcodes") == None:
        df = get_scrip_data()
        df.columns = [ "scrip_code",     "symbol",               "description",  "instrument_type"]
        df.to_sql("scripcodes", engine, if_exists="replace", index=False)
    logger.info("Table scripcodes already exists!")
  
    logger.info("Caching etflist...")
    df = get_etflist_data()
    df.columns = [ "symbol","description","securtiy_name","date_of_listing","market_lot","isin","face_value"]
    df.to_sql("etflist", engine, if_exists="replace",index=False)

    
    logger.info("Caching equity list...")
    df = get_eqlist_data()  
    df.columns = [ "symbol","description",  "series", "date_of_listing","paid_up_value","market_lot", "isin","face_value"]
    df.to_sql("equitylist", engine, if_exists="replace",index=False)
    
    logger.info("Caching Indices...")
    indices = get_relevant_nse_indices()
    # indices_mapping = get_nse_indices_mapping()
    # print(indices.keys())
    
    for index in indices:
        logger.info(f"Caching {index}...")
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        # index = get_trading_index_name(index)
        df = get_indices_hist_data(index,start_date.strftime("%d-%m-%Y"),end_date.strftime("%d-%m-%Y"))
        # print("db ", df)
        # df = df.drop(columns=['index_name'], axis=1, inplace=True)
        # df.to_sql(index.replace(" ","_"),engine, if_exists="replace", index=False)
        append_if_needed(index.replace(" ", "_"), df, "ts", engine)
        
        
        
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
