from sqlmodel import BigInteger, Column, Field, SQLModel


class User(SQLModel, table=True):
    id: int = Field(sa_column=Column(BigInteger(), primary_key=True))
    name: str = Field(index=True, max_length=64)
