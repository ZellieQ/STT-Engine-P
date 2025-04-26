from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis

from api.core.config import settings

# PostgreSQL connection
SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# MongoDB connection
mongo_client = MongoClient(settings.MONGODB_URL)
mongo_db = mongo_client[settings.MONGODB_DB]

# Redis connection
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get MongoDB connection
def get_mongo_db():
    return mongo_db

# Dependency to get Redis connection
def get_redis_client():
    return redis_client
