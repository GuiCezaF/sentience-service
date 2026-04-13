from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.settings import envs

DATABASE_URL = envs("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_size=10,         # max persistent connections
    max_overflow=20,      # max extra connections allowed beyond pool_size
    pool_timeout=30,      # seconds to wait for a connection from the pool
    pool_recycle=1800,    # recycle connections after X seconds
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
