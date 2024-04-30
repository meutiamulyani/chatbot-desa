from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import dotenv_values

# URL_DATABASE = 'postgresql://postgres:meutiaam@localhost:5432/chatbot_ai'

env_vars = dotenv_values(".env")
URL_DATABASE = env_vars.get('DB_URL')

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()