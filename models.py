import os

import dotenv
from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text, create_engine, func)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

dotenv.load_dotenv()

base = declarative_base()


class User(base):
    __tablename__ = "user"
    id = Column(String, primary_key=True)
    balance = Column(Float, default=0)
    orders = relationship("Order")

class Order(base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True)
    delivered = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=func.now())
    user = Column(String, ForeignKey("user.id"))


engine = create_engine(os.getenv("DB_URL"))
connection = engine.connect()
base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
