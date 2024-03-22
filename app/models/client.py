from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .user import User
    from .event import Event


class ClientBase(SQLModel):
    full_name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    phone: str = Field(max_length=255, default=None)
    company_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    user_id: int = Field(default=None, foreign_key="user.id")


class Client(ClientBase, table=True):
    id: int = Field(default=None, primary_key=True, index=True)

    user: "User" = Relationship(back_populates="clients")
    events: list["Event"] = Relationship(back_populates="clients")


class ClientCreate(ClientBase):
    name: str
    email: str
    phone: str
    company_name: str
    user_id: str


class ClientUpdate(ClientBase):
    name: str | None
    email: str | None
    phone: str | None
    company_name: str | None
    user_id: str | None


class ClientRead(ClientBase):
    id: int
