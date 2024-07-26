from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from .client import Client
    from .contract import Contract


class EventBase(SQLModel):
    event_date_start: datetime = Field(default_factory=datetime.utcnow)
    event_date_end: datetime = Field(default_factory=datetime.utcnow)
    location: str = Field(max_length=255)
    attendees: int = Field(gt=0)
    notes: str = Field(default=None, max_length=2048)
    contract_id: int = Field(default=None, foreign_key="contract.id")
    client_id: int = Field(default=None, foreign_key="client.id")


class Event(EventBase, table=True):
    id: int = Field(default=None, primary_key=True, index=True)

    contract: "Contract" = Relationship(back_populates="events")
    client: "Client" = Relationship(back_populates="events")


class EventCreate(EventBase):
    location: str
    attendees: int


class EventUpdate(EventBase):
    location: str | None
    attendees: int | None
    contract_id: int | None = None
    client_id: int | None = None


class EventRead(EventBase):
    id: int
