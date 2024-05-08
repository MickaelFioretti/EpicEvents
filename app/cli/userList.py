from textual.widgets import Static, DataTable, Button, Input
from textual.app import ComposeResult
from textual.containers import Container
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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.name == "add_user":
            self.query(DataTable).remove()
            self.query(Button).remove()
            self.query(Grid).remove()
            self.mount(UserForm())


class UserForm(Static):
    def compose(self) -> ComposeResult:
        yield Input(placeholder="Nom complet", id="full_name")
        yield Input(placeholder="Email", id="email")
        yield Input(placeholder="Mot de passe", id="password")
        yield Input(placeholder="Département", id="department")
        yield Input(placeholder="Actif", id="is_active")
        yield Container(
            Button("Annuler", variant="warning", id="cancel_user"),
            Button("Créer", variant="success", id="create_user"),
        )
