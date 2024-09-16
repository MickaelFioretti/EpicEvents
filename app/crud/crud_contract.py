import sentry_sdk
from app.models.contract import Contract, ContractCreate, ContractUpdate
from app.crud.base import CRUDBase
from sqlmodel import select
from sqlalchemy.orm import Session
from app.models import Client, User


class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):
    def get_all(self, db: Session) -> list[Contract]:
        statement = (
            select(Contract, Client, User)
            .join(Client, Contract.client_id == Client.id)
            .join(User, Contract.user_id == User.id)
        )
        results = db.execute(statement).scalars().all()
        return results

    def create(self, db: Session, *, obj_in: ContractCreate) -> Contract:
        sentry_sdk.capture_message("Contract created", level="info")
        return super().create(db, obj_in=obj_in)


contract = CRUDContract(Contract)
