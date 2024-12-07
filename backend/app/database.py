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
from .models import Base, ScripCode, ETFList, EQList

from .utils import get_scrip_data, get_etflist_data, get_eqlist_data

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
     
       
    # for index, row in df.iterrows():
    #     scriprow = ScripCode(scrip_code=row["ScripCode"], 
    #                          symbol=row.TradingSymbol, 
    #                          description=row.Description, 
    #                          instrument_type=row.InstrumentType)
    #     db.add(scriprow)
    #     db.commit()
    
    logger.info("Caching etflist...")
    df = get_etflist_data()
    df.columns = [ "symbol","description","securtiy_name","date_of_listing","market_lot","isin","face_value"]
    df.to_sql("etflist", engine, if_exists="replace",index=False)
    # for index, row in df.iterrows():
    #     etfrow = ETFList(isin = row.ISINNumber,
    #                      symbol = row.Symbol,
    #                      description = row.Underlying,
    #                      securtiy_name = row.SecurityName,
    #                      date_of_listing = row.DateofListing,
    #                      face_value = row.FaceValue
    #                      )
    #     db.add(etfrow)
    #     db.commit()
    
    logger.info("Caching equity list...")
    df = get_eqlist_data()  
    df.columns = [ "symbol","description",  "series", "date_of_listing","paid_up_value","market_lot", "isin","face_value"]
    df.to_sql("equitylist", engine, if_exists="replace",index=False)
    # for index, row in df.iterrows():
    #     eqrow = EQList(isin = row["ISIN NUMBER"],
    #                     symbol = row["SYMBOL"],
    #                     description = row["NAME OF COMPANY"],
    #                     series = row["SERIES"],
    #                     date_of_listing = row["DATE OF LISTING"],
    #                     face_value = row["FACE VALUE"],
    #                     paid_up_value = row["PAID UP VALUE"],
    #                     market_lot = row["MARKET LOT"]
    #                     )
    #     db.add(eqrow)
    #     db.commit()
    #     db.refresh(eqrow)
    
init_tables()