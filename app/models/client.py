from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .user import User
    from .event import Event


class ClientBase(SQLModel):
    full_name: str = Field(max_length=255)
    email: str = Field(max_length=255)
    phone: str = Field(max_length=255)
    company_name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id")


class Client(ClientBase, table=True):
    id: int = Field(primary_key=True, index=True)

    user: "User" = Relationship(back_populates="clients")
    events: list["Event"] = Relationship(back_populates="clients")


class ClientCreate(ClientBase):
    full_name: str
    email: str
    phone: str
    company_name: str
    user_id: int


class ClientUpdate(ClientBase):
    full_name: str | None
    email: str | None
    phone: str | None
    company_name: str | None
    user_id: int | None


class ClientRead(ClientBase):
    id: int
