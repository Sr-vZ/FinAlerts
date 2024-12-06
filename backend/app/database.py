# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
# from sqlalchemy.orm import sessionmaker
# from app.config import settings

# SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base: DeclarativeMeta = declarative_base()
# database.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from .models import Base, ScripCode, ETFList, EQList

from .utils import get_scrip_data
import pandas as pd

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


def init_tables(db: get_db)  ->  None:
    """
    Populate the tables with data
    """
    df = get_scrip_data
    for row in df:
        scriprow = ScripCode(scrip_code=row.ScripCode, 
                             symbol=row.TradingSymbol, 
                             description=row.Description, 
                             instrument_type=row.InstrumentType)
        db.add(scriprow)
        db.commit()
        db.refresh(scriprow)
    
