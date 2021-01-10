from sqlalchemy import create_engine
import urllib
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv


load_dotenv()

SQLALCHEMY_DATABASE_URL = "postgres://{}:{}@localhost:5432/fastapitutorial".format(os.getenv("DATABASE_USERNAME"), urllib.parse.quote_plus(os.getenv("DATABASE_PASSWORD")))

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
