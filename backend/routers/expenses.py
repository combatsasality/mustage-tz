from datetime import date, datetime
from uuid import UUID

from database import Expenses, User
from dependencies import SessionDep
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import field_serializer
from sqlmodel import SQLModel, delete, select
from utils import RedisBroker


class ExpensesAdd(SQLModel):
    name: str
    amount_uah: float
    user_id: int

    created_at: date


class ExpensesUpdate(SQLModel):
    name: str
    amount_uah: float


class ExpensesGet(SQLModel):
    name: str
    amount_uah: float
    amount_usd: float
    created_at: date

    id: UUID

    @field_serializer("created_at")
    def serialize_created_at(self, created_at: date) -> str:
        return created_at.strftime("%d.%m.%Y")


router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.get("/{user_id}", response_model=list[ExpensesGet])
async def get_expenses(user_id: int, session: SessionDep):
    expenses = session.exec(
        select(Expenses)
        .order_by(Expenses.created_at)
        .where(Expenses.user_id == user_id)
    ).all()
    return expenses


@router.get("/get/{expenses_id}", response_model=ExpensesGet)
async def get_expenses_by_id(expenses_id: UUID, session: SessionDep):
    expenses = session.get(Expenses, expenses_id)
    if not expenses:
        return JSONResponse({"status": False})
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
    statement = (
        select(Expenses)
        .order_by(Expenses.created_at)
        .where(
            Expenses.user_id == user_id, Expenses.created_at.between(from_time, to_time)
        )
    )
    expenses = session.exec(statement).all()

    return expenses


@router.post("/add")
async def add_expenses(expenses: ExpensesAdd, session: SessionDep):
    if not session.get(User, expenses.user_id):
        return {"message": "User doesn't exists", "status": False}
    expenses = Expenses(
        name=expenses.name,
        amount_uah=expenses.amount_uah,
        user_id=expenses.user_id,
        amount_usd=RedisBroker().get_rate() * expenses.amount_uah,
        created_at=expenses.created_at,
    )
    session.add(expenses)
    session.commit()
    session.refresh(expenses)
    return {"message": expenses, "status": True}


@router.delete("/{expenses_id}")
async def delete_expenses(expenses_id: UUID, session: SessionDep):
    expenses = session.get(Expenses, expenses_id)
    if not expenses:
        return {"message": "Expenses doesn't exists", "status": False}

    session.delete(expenses)
    session.commit()
    return {"message": "Expenses successfully deleted", "status": True}


@router.delete("/")
async def delete_expenses_ids(expenses_ids: list[UUID], session: SessionDep):
    statement = delete(Expenses).where(Expenses.id.in_(expenses_ids))

    session.exec(statement)

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
    return {"message": expenses_db, "status": True}
