from typing import Annotated
from fastapi.security import OAuth2PasswordBearer
import jwt
from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()