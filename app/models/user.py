from datetime import datetime
from typing import TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
import enum

if TYPE_CHECKING:
    from .client import Client
    from .contract import Contract


class DepartmentEnum(str, enum.Enum):
    commercial = "commercial"
    support = "support"
    gestion = "gestion"
    guest = "guest"


class UserBase(SQLModel):
    email: str = Field(max_length=255, unique=True, index=True)
    full_name: str = Field(max_length=255)
    hashed_password: str = Field(max_length=255)
    is_active: bool = Field(default=True)
    department: DepartmentEnum
    created_at: datetime = Field(default_factory=datetime.utcnow)


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True, index=True)

    clients: list["Client"] = Relationship(back_populates="user")
    contracts: list["Contract"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    email: str
    full_name: str
    hashed_password: str
    is_active: bool
    department: DepartmentEnum


class UserUpdate(UserBase):
    email: str | None
    full_name: str | None
    hashed_password: str | None
    is_active: bool | None
    department: DepartmentEnum | None


class UserRead(UserBase):
    id: int
