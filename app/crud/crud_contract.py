from app.models.contract import Contract, ContractCreate, ContractUpdate
from app.crud.base import CRUDBase
from sqlmodel import select
from sqlalchemy.orm import Session


class CRUDContract(CRUDBase[Contract, ContractCreate, ContractUpdate]):
    def get_all(self, db: Session):
        return db.execute(select(Contract)).all()


contract = CRUDContract(Contract)
