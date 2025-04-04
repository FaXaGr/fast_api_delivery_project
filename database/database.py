from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base



engine = create_engine("postgresql://postgres:faxa@localhost/delivery_db",echo=True)

Base = declarative_base()
session = sessionmaker()