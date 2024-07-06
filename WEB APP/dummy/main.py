from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel
from typing import List
from databases import Database
from passlib.context import CryptContext
import uuid
import logging
import os
from fastapi.middleware.cors import CORSMiddleware
#from starlette.middleware.base import BaseHTTPMiddleware
import subprocess

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

# Database connection URL (read from environment variable)
DATABASE_URL = "postgresql://neondb_owner:VhFlv4Nn6ZwQ@ep-noisy-water-a7lnl2wu-pooler.ap-southeast-2.aws.neon.tech/dummy_data?sslmode=require"
# Database connection URL (replace with your actual connection string)
#DATABASE_URL = "postgresql://neondb_owner:VhFlv4Nn6ZwQ@ep-noisy-water-a7lnl2wu-pooler.ap-southeast-2.aws.neon.tech/dummy%20Docker?sslmode=require"

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware if you're testing the frontend locally
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    #allow_headers=["*"],
)
# Add custom middleware to handle large headers
# class LargeHeaderMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         response = await call_next(request)
#         response.headers['X-Large-Header'] = 'value' * 100  # Example large header
#         return response

#app.add_middleware(LargeHeaderMiddleware)


# Initialize database connection
# Initialize database connection
database = Database(DATABASE_URL)
engine = create_engine(DATABASE_URL, echo=True)

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Define the User model
class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(index=True)
    hashed_password: str

# Define the UserCreate model
class UserCreate(BaseModel):
    username: str
    password: str

# Define the Article model
class Article(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    content: str
    pdf: bytes

# Define the ArticleCreate model
class ArticleCreate(BaseModel):
    title: str
    content: str

@app.on_event("startup")
async def startup():
    await database.connect()
    SQLModel.metadata.create_all(engine)

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Helper function to get a user by username
def get_user(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        results = session.exec(statement)
        return results.first()

# Helper function to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Helper function to hash password
def get_password_hash(password):
    return pwd_context.hash(password)

# Endpoint to create a new user
@app.post("/users/", response_model=UserCreate, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    db_user = get_user(user.username)
    if db_user:
        logging.error("Username already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    user_obj = User(username=user.username, hashed_password=hashed_password)
    try:
        with Session(engine) as session:
            session.add(user_obj)
            session.commit()
            session.refresh(user_obj)
            logging.info(f"User created successfully: {user_obj}")
    except Exception as e:
        logging.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create account")
    
    return user

# Endpoint for user login
@app.post("/login/")
async def login(user: UserCreate):
    db_user = get_user(user.username)
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return {"message": "Login successful"}

# Endpoint to fetch all articles
@app.get("/articles/", response_model=List[Article])
async def get_articles():
    with Session(engine) as session:
        statement = select(Article)
        results = session.exec(statement).all()
        return results

# Endpoint to upload a PDF article
@app.post("/articles/upload/")
async def upload_article(title: str = Form(...), content: str = Form(...), pdf: UploadFile = File(...)):
    pdf_data = await pdf.read()
    article = Article(title=title, content=content, pdf=pdf_data)
    try:
        with Session(engine) as session:
            session.add(article)
            session.commit()
            session.refresh(article)
            logging.info(f"Article uploaded successfully: {article}")
    except Exception as e:
        logging.error(f"Error uploading article: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload article")
    return {"message": "Article uploaded successfully"}

# @app.get("/hello/")
# def display():
#     return("hello")
# @app.get("/display/")
# def display():
#     # Start the Streamlit application
#     subprocess.Popen(["streamlit", "run", "app.py"])
#     return {"message": "Streamlit app is running"}