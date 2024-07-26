from app.models.event import Event, EventCreate, EventUpdate
from app.crud.base import CRUDBase
from sqlmodel import select
from sqlalchemy.orm import Session


class CRUDEvent(CRUDBase[Event, EventCreate, EventUpdate]):
    def get_all(self, db: Session):
        return db.execute(select(Event)).all()


event = CRUDEvent(Event)
