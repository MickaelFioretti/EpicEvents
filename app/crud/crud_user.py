from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User, UserCreate, UserUpdate, UserAuthenticate
from app.core.security import get_password_hash, verify_password, create_access_token
from typing import Optional, Dict
from sqlmodel import select
from app.settings import settings
from datetime import timedelta


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.execute(select(User).where(User.email == email)).scalar_one_or_none()

    def get_all(self, db: Session):
        return db.execute(select(User)).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.hashed_password),
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            department=obj_in.department,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserUpdate) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(self, db: Session, *, obj_in: UserAuthenticate) -> Optional[Dict[str, str]]:
        user = self.get_by_email(db, email=obj_in.email)
        if user and verify_password(obj_in.password, user.hashed_password):
            access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user.email, "id": user.id, "department": user.department},
                expires_delta=access_token_expires,
            )
            # TODO: Add refresh token
            return {
                "access_token": access_token,
                "token_type": "bearer",
            }
        return None


user = CRUDUser(User)
