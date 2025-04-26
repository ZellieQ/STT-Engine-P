import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our models and database setup
from api.db.database import Base, engine
from api.models.user import User
from api.models.transcription import Transcription, CustomVocabulary

# Create password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Check if we already have users
        user_count = db.query(User).count()
        if user_count == 0:
            print("Creating test user...")
            # Create a test user
            test_user = User(
                email="test@example.com",
                username="testuser",
                hashed_password=get_password_hash("password123"),
                full_name="Test User",
                is_active=True,
                is_superuser=True,
                created_at=datetime.now()
            )
            db.add(test_user)
            db.commit()
            print("Test user created successfully.")
            print("Username: testuser")
            print("Password: password123")
        else:
            print(f"Database already has {user_count} users. Skipping user creation.")
        
        # Create a test custom vocabulary if none exists
        vocab_count = db.query(CustomVocabulary).count()
        if vocab_count == 0 and user_count > 0:
            print("Creating test custom vocabulary...")
            # Get the first user
            user = db.query(User).first()
            
            # Create a test custom vocabulary for technical terms
            tech_vocab = CustomVocabulary(
                user_id=user.id,
                name="Technical Terms",
                description="Common technical terms and acronyms",
                language_code="en-US",
                terms='''
                {
                    "API": "Application Programming Interface",
                    "REST": "Representational State Transfer",
                    "JSON": "JavaScript Object Notation",
                    "HTML": "HyperText Markup Language",
                    "CSS": "Cascading Style Sheets",
                    "SQL": "Structured Query Language",
                    "NoSQL": "Not Only SQL",
                    "HTTP": "HyperText Transfer Protocol",
                    "HTTPS": "HyperText Transfer Protocol Secure",
                    "JWT": "JSON Web Token",
                    "OAuth": "Open Authorization",
                    "DNS": "Domain Name System",
                    "TCP": "Transmission Control Protocol",
                    "IP": "Internet Protocol",
                    "GPU": "Graphics Processing Unit",
                    "CPU": "Central Processing Unit",
                    "RAM": "Random Access Memory",
                    "SSD": "Solid State Drive",
                    "HDD": "Hard Disk Drive"
                }
                '''
            )
            db.add(tech_vocab)
            db.commit()
            print("Test custom vocabulary created successfully.")
        else:
            print(f"Database already has {vocab_count} custom vocabularies. Skipping vocabulary creation.")
            
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialization completed.")
