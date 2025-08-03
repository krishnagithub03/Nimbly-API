from sqlalchemy import Column, Integer, String
from app.database import Base


class AWS_User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    access_key = Column(String, nullable=False)
    access_secret = Column(String, nullable=False)
    region = Column(String, default="ap-south-1")
    aws_fp = Column(String, nullable=False, unique=True, index=True)
