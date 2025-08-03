from fastapi import FastAPI, APIRouter
from app.api.v1.routes import instance, auth
from app.database import Base, engine
from app.schemas import *

app = FastAPI()
app.include_router(instance.router)
app.include_router(auth.router)
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Hello World"}
