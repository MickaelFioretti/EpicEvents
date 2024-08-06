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


contract = CRUDContract(Contract)
