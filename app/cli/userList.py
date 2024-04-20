from textual.widgets import Static, DataTable, Button
from textual.app import ComposeResult
from app.crud.crud_user import CRUDUser
from app.models.user import User
from app.session import get_db
from textual.containers import Grid


class UserList(Static):
    def __init__(self, **kwargs) -> None:
        self.crud_user = CRUDUser(User)
        super().__init__(**kwargs)

    TABLE_DATA = [("id", "full_name", "email", "department", "is_active")]

    def compose(self) -> ComposeResult:
        with Grid():
            yield Button(
                "Ajouter un utilisateur", variant="success", name="add_user", classes="box"
            )
            yield DataTable(classes="box")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns(*self.TABLE_DATA[0])
        with get_db() as db:
            try:
                users = self.crud_user.get_multi(db)
                for user in users:
                    table.add_row(*[getattr(user, column) for column in self.TABLE_DATA[0]])
            except Exception as e:
                self.log.warning(e)
