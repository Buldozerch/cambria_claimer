from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .models import Base

# class DataBase
class DB:
    def __init__(self):
        self.engine = create_engine("sqlite:///files/accounts.db")
        self.session = Session(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)
