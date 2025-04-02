from database import engine
from dependencies import get_secret_header
from fastapi import Depends, FastAPI
from routers import expenses_router, users_router
from sqlmodel import SQLModel


def on_startup():
    SQLModel.metadata.create_all(engine)


app = FastAPI(on_startup=[on_startup], dependencies=[Depends(get_secret_header)])


app.include_router(users_router)
app.include_router(expenses_router)
