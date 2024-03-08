from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


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

    user: "User" = Relationship(back_populates="contracts")


class ContractCreate(ContractBase):
    total_amount: float
    remaining_amount: float
    status: StatusContractEnum
    client: int
    user_id: int


class ContractUpdate(ContractBase):
    total_amount: float | None
    remaining_amount: float | None
    status: StatusContractEnum | None
    client: int | None
    user_id: int | None


class ContractRead(ContractBase):
    id: int
