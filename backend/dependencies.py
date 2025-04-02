from typing import Annotated

from constants import SECRET
from database import engine
from fastapi import Depends, Header, HTTPException
from sqlmodel import Session


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


async def get_secret_header(secret: Annotated[str, Header()]):
    if secret != SECRET:
        raise HTTPException(status_code=400, detail="Secret token invalid")
