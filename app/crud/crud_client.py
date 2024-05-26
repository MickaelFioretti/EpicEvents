from app.models.client import Client, ClientCreate, ClientUpdate
from app.crud.base import CRUDBase
from sqlmodel import select
from sqlalchemy.orm import Session


class CRUDClient(CRUDBase[Client, ClientCreate, ClientUpdate]):
    def get_all(self, db: Session):
        return db.execute(select(Client)).all()


client = CRUDClient(Client)
