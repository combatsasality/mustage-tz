from database import User
from dependencies import SessionDep
from fastapi import APIRouter
from sqlmodel import select

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def read_users(session: SessionDep):
    users = session.exec(select(User)).all()
    return users


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        return {"message": "User not found", "status": False}
    return user


@router.post("/add")
async def add_user(user: User, session: SessionDep):
    if session.get(User, user.id):
        return {"message": "User already exists", "status": False}

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User successfully added", "status": True}
