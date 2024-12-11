# from sqlalchemy import Column, Integer, String
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)

#     is_active = Column(Integer, default=True)

# models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

# ScripCode,TradingSymbol,Description,InstrumentType
class ScripCode(Base):
    __tablename__ = "scripcodes"
    scrip_code = Column(Integer, primary_key=True, unique=True, index=True)
    symbol = Column(String, unique=True, index=True)
    description = Column(String)
    instrument_type = Column(String)

# Symbol	Underlying	SecurityName	DateofListing	MarketLot	ISINNumber	FaceValue
class ETFList(Base):
    __tablename__ = "etflist"
    isin = Column(Integer, primary_key=True, unique=True, index=True)
    symbol = Column(String, unique=True, index=True)
    description = Column(String)
    security_name = Column(String)
    date_of_listing = Column(DateTime)
    face_value = Column(Integer)
    market_lot = Column(String)    

# SYMBOL	NAME OF COMPANY	 SERIES	 DATE OF LISTING	 PAID UP VALUE	 MARKET LOT	 ISIN NUMBER	 FACE VALUE
class EQList(Base):
    __tablename__ = "equitylist"
    isin = Column(Integer, primary_key=True, unique=True, index=True)
    symbol = Column(String, unique=True, index=True)
    description = Column(String)
    date_of_listing = Column(DateTime)
    face_value = Column(Integer)
    market_lot = Column(Integer)
    paid_up_value = Column(Integer)
    series = Column(String)