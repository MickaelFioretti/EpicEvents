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

    clients: list["Client"] = Relationship(back_populates="events")
    contracts: list["Contract"] = Relationship(back_populates="events")


class EventCreate(EventBase):
    event_date_start: datetime
    event_date_end: datetime
    location: str
    attendees: int
    notes: str
    contract: int
    client: int


class EventUpdate(EventBase):
    event_date_start: datetime | None
    event_date_end: datetime | None
    location: str | None
    attendees: int | None
    notes: str | None
    contract: int | None
    client: int | None


class EventRead(EventBase):
    id: int
