from pydantic import BaseModel


class AuthRequest(BaseModel):
    aws_access_key_id: str
    aws_secret_access_key: str
    region: str
