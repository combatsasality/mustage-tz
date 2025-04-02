from database import engine
from fastapi import FastAPI
from sqlmodel import SQLModel


def on_startup():
    SQLModel.metadata.create_all(engine)


app = FastAPI(on_startup=[on_startup])
