import uuid
from datetime import date, datetime

from sqlmodel import BigInteger, Column, Field, ForeignKey, SQLModel


class Expenses(SQLModel, table=True):
    id: uuid.UUID = Field(primary_key=True, default_factory=uuid.uuid4)
    name: str = Field(index=True, max_length=128, nullable=False)
    amount_uah: float = Field(nullable=False)
    amount_usd: float = Field(nullable=False)
    created_at: date = Field(default_factory=datetime.now, nullable=False)

    user_id: int | None = Field(
        sa_column=Column(
            BigInteger(), foreign_key=ForeignKey("user.id"), nullable=False
        )
    )
