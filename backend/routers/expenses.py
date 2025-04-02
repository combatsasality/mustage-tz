from datetime import datetime
from uuid import UUID

from database import Expenses, User
from dependencies import SessionDep
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlmodel import SQLModel, select
from utils import RedisBroker


class ExpensesAdd(SQLModel):
    name: str
    amount_uah: float
    user_id: int

    created_at: datetime


class ExpensesUpdate(SQLModel):
    name: str
    amount_uah: float

    created_at: datetime


class ExpensesGet(SQLModel):
    name: str
    amount_uah: float
    amount_usd: float
    created_at: datetime


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/{user_id}", response_model=list[ExpensesGet])
async def get_expenses(user_id: int, session: SessionDep):
    expenses = session.exec(select(Expenses).where(Expenses.user_id == user_id)).all()
    return expenses


@router.get("/{user_id}/{from_range}/{to_range}", response_model=list[ExpensesGet])
async def get_expenses_range(
    user_id: int, from_range: str, to_range: str, session: SessionDep
):
    try:
        from_time = datetime.strptime(from_range, "%d.%m.%Y")
        to_time = datetime.strptime(to_range, "%d.%m.%Y")
    except Exception as e:
        return JSONResponse(
            {
                "message": str(e),
                "status": False,
            },
            400,
        )
    statement = select(Expenses).where(
        Expenses.user_id == user_id, Expenses.created_at.between(from_time, to_time)
    )
    expenses = session.exec(statement).all()

    return expenses


@router.post("/add")
async def add_expenses(expenses: ExpensesAdd, session: SessionDep):
    if not session.get(User, expenses.user_id):
        return {"message": "User doesn't exists", "status": False}

    session.add(
        Expenses(
            name=expenses.name,
            amount_uah=expenses.amount_uah,
            user_id=expenses.user_id,
            amount_usd=RedisBroker().get_rate() * expenses.amount_uah,
            created_at=expenses.created_at,
        )
    )
    session.commit()
    return {"message": "Expenses successfully added", "status": True}


@router.delete("/{expenses_id}")
async def delete_expenses(expenses_id: UUID, session: SessionDep):
    expenses = session.get(Expenses, expenses_id)
    if not expenses:
        return {"message": "Expenses doesn't exists", "status": False}

    session.delete(expenses)
    session.commit()
    return {"message": "Expenses successfully deleted", "status": True}


@router.patch("/{expenses_id}")
async def update_expense(
    expenses_id: UUID, expenses: ExpensesUpdate, session: SessionDep
):
    expenses_db = session.get(Expenses, expenses_id)
    if not expenses_db:
        return {"message": "Expenses doesn't exists", "status": False}

    expenses_data = expenses.model_dump(exclude_unset=True)
    expenses_db.sqlmodel_update(expenses_data)
    expenses_db.amount_usd = expenses.amount_uah * RedisBroker().get_rate()
    session.add(expenses_db)
    session.commit()
    session.refresh(expenses_db)
    return {"message": "Expenses successfully changed", "status": True}
