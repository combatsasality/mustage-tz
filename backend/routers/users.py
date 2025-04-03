from database import User
from dependencies import SessionDep
from fastapi import APIRouter
from fastapi.responses import JSONResponse
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
        return JSONResponse({"message": "User not found", "status": False})
    return user


@router.post("/add")
async def add_user(user: User, session: SessionDep):
    user_db = session.get(User, user.id)
    if user_db:
        user_data = user.model_dump(exclude_unset=True)
        user_db.sqlmodel_update(user_data)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
    else:
        session.add(user)
        session.commit()
        session.refresh(user)
    return {"message": "User successfully added", "status": True}
