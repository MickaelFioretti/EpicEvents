from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from .user import User
    from .event import Event
    from .contract import Contract


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

    user: "User" = Relationship(back_populates="client")
    contract: list["Contract"] = Relationship(back_populates="client")
    event: list["Event"] = Relationship(back_populates="client")


class ClientCreate(ClientBase):
    full_name: str
    email: str
    phone: str
    company_name: str
    user_id: int


class ClientUpdate(ClientBase):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    company_name: str | None = None
    user_id: int | None = None


class ClientRead(ClientBase):
    id: int
    user: "User"
    contract: list["Contract"]
