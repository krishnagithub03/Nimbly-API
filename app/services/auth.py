import hashlib
import os
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta, timezone
from cryptography.fernet import Fernet
from sqlalchemy.orm import Session

from app.deps import get_db
from app.schemas.auth_request import AWS_User


SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
FERNET_KEY = os.getenv("FERNET_SECRET_KEY")

fernet = Fernet(FERNET_KEY)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/register")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    )
    to_encode.update({"exp": expire, "sub": data.get("sub")})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire, "sub": data.get("sub")})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")
    except PyJWTError:
        raise ValueError("Invalid token")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(AWS_User).filter(AWS_User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def encrypt_aws_creds(access_key: str, access_secret: str):
    return (
        fernet.encrypt(access_key.encode()).decode(),
        fernet.encrypt(access_secret.encode()).decode(),
    )


def decrypt_aws_creds(enc_key: str, enc_secret: str):
    return (
        fernet.decrypt(enc_key.encode()).decode(),
        fernet.decrypt(enc_secret.encode()).decode(),
    )


def get_aws_fingerprint(access_key: str, access_secret: str):
    return hashlib.sha256(f"{access_key}:{access_secret}".encode()).hexdigest()
