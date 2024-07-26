from sqlmodel import create_engine
from app.session import get_db
from app.models.user import UserCreate, DepartmentEnum
from app.crud import user as crud_user

DATABASE_URL = (
    "postgresql://postgres:password@db/epic_events"  # Assurez-vous que l'URL est correcte
)
engine = create_engine(DATABASE_URL, echo=True)


def test_db():
    with get_db() as db:
        # Essayer d'insérer un nouvel utilisateur (comme test)
        new_user = UserCreate(
            email="admin@admin.com",
            full_name="Admin",
            hashed_password="changethis",
            department=DepartmentEnum.gestion,
            is_active=True,
        )

        crud_user.create(db, obj_in=new_user)

        try:
            print("Utilisateur inséré avec succès.")
        except Exception as e:
            db.rollback()
            print(f"Erreur lors de l'insertion : {e}")

        # Récupérer tous les utilisateurs et les afficher
        users = crud_user.get_all(db)
        print("Liste des utilisateurs :", users)


if __name__ == "__main__":
    test_db()
