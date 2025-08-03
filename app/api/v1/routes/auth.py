import os
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.deps import get_db
from app.models.auth_model import AuthRequest
from app.schemas.auth_request import AWS_User
from app.services.auth import *


router = APIRouter(prefix="/auth")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


@router.post("/register")
def register_user(data: AuthRequest, db: Session = Depends(get_db)):
    fp = get_aws_fingerprint(data.aws_access_key_id, data.aws_secret_access_key)

    user = db.query(AWS_User).filter_by(aws_fp=fp).first()

    if not user:
        enc_key, enc_secret = encrypt_aws_creds(
            data.aws_access_key_id, data.aws_secret_access_key
        )

        user = AWS_User(
            access_key=enc_key, access_secret=enc_secret, region=data.region, aws_fp=fp
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = create_access_token({"sub": str(user.id)})

    refresh_token = create_refresh_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS)),
    )

    response = JSONResponse({"token": access_token}, status_code=200)

    response.set_cookie(key="refresh_token", value=refresh_token, secure=True)

    return response
