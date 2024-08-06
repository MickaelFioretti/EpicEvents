from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .event import Event
    from .client import Client


class StatusContractEnum(str, enum.Enum):
    signe = "signe"
    en_cours = "en_cours"
    termine = "termine"
    annule = "annule"


class ContractBase(SQLModel):
    total_amount: float
    remaining_amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: StatusContractEnum = Field(default="en_cours")
    client_id: int = Field(default=None, foreign_key="client.id")
    user_id: int = Field(default=None, foreign_key="user.id")


class Contract(ContractBase, table=True):
    id: int = Field(default=None, primary_key=True, index=True)

    user: "User" = Relationship(back_populates="contract")
    client: "Client" = Relationship(back_populates="contract")
    event: list["Event"] = Relationship(back_populates="contract")


class ContractCreate(ContractBase):
    total_amount: float
    remaining_amount: float
    status: StatusContractEnum = StatusContractEnum.en_cours
    user_id: int | None = None


class ContractUpdate(ContractBase):
    total_amount: float | None
    remaining_amount: float | None
    status: StatusContractEnum | None = None
    client_id: int | None = None
    user_id: int | None = None


class ContractRead(ContractBase):
    id: int
    client: "Client"
    user: "User"
