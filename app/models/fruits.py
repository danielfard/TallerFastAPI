from config.database import Base
from sqlalchemy import Column, Float, Integer, String


class Fruit(Base):
    __tablename__ = "fruits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    sugar = Column(Float)
