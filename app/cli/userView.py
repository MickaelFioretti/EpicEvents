from typing import cast
from textual.widgets import Static, DataTable, Button, Input, Checkbox, Select, Label
from textual.app import ComposeResult
from textual.containers import Container
from app.crud.crud_user import CRUDUser
from app.models.user import User, UserCreate, DepartmentEnum
from app.session import get_db
from textual.containers import Grid


LINES = DepartmentEnum.__members__.keys()


class UserView(Static):
    def __init__(self, **kwargs) -> None:
        self.crud_user = CRUDUser(User)
        super().__init__(**kwargs)

    TABLE_DATA = [("id", "full_name", "email", "department", "is_active")]
    selected_user: int = 0

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button("Ajouter un utilisateur", variant="success", name="add_user"),
                classes="button-container",
            )

            yield Container(
                DataTable(cursor_type="row"),
                classes="table",
            )

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
            self.mount(UserFormCreate())
        if event.control.name == "update_user":
            self.query(DataTable).remove()
            self.query(Button).remove()
            self.query(Grid).remove()
            self.mount(UserFormUpdate())
        if event.control.name == "delete_user":
            with get_db() as db:
                try:
                    if self.selected_user:
                        self.crud_user.remove(db, id=self.selected_user)
                except Exception as e:
                    self.log.warning(e)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_user = event.data_table.get_row(event.row_key)[0]
        if self.selected_user != 0:
            self.query("#button-update").remove()
            self.query("#button-delete").remove()
            self.mount(
                Button(
                    "Modifier un utilisateur",
                    variant="success",
                    name="update_user",
                    id="button-update",
                ),
                after="Button",
            )
            self.mount(
                Button(
                    "Supprimer un utilisateur",
                    variant="error",
                    name="delete_user",
                    id="button-delete",
                ),
                after="#button-update",
            )


class UserFormCreate(Static):
    def __init__(self, **kwargs) -> None:
        self.crud_user = CRUDUser(User)
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Nom complet", id="full_name"),
            Input(placeholder="Email", id="email"),
            Input(placeholder="Mot de passe", password=True, id="password"),
            Select.from_values(LINES, prompt="Departement", id="department"),
            Checkbox(label="Actif", value=True, id="is_active"),
            id="form",
        )
        yield Container(
            Button("Annuler", variant="warning", id="cancel_user"),
            Button("Créer", variant="success", id="create_user"),
            classes="buttons",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel_user":
            self.query(Container).remove()
            self.mount(UserView())
        if event.control.id == "create_user":
            label = self.query("#invalid-credentials")
            if label:
                label.remove()
            if not all(
                [
                    self.query_one("#full_name", Input).value,
                    self.query_one("#email", Input).value,
                    self.query_one("#password", Input).value,
                    self.query_one("#department", Select).value != Select.BLANK,
                ]
            ):
                self.mount(
                    Label("Veuillez remplir tous les champs", id="invalid-credentials"),
                    after="#is_active",
                )
                return
            full_name = self.query_one("#full_name", Input).value
            email = self.query_one("#email", Input).value
            password = self.query_one("#password", Input).value
            department = cast(DepartmentEnum, self.query_one("#department", Select).value)
            is_active = self.query_one("#is_active", Checkbox).value
            with get_db() as db:
                try:
                    user = UserCreate(
                        email=email,
                        full_name=full_name,
                        hashed_password=password,
                        department=department,
                        is_active=is_active,
                    )
                    self.crud_user.create(db, obj_in=user)
                except Exception as e:
                    self.log.warning(e)
            self.query(Container).remove()
            self.mount(UserView())


class UserFormUpdate(Static):
    def __init__(self, **kwargs) -> None:
        self.crud_user = CRUDUser(User)
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Nom complet", id="full_name"),
            Input(placeholder="Email", id="email"),
            Select.from_values(LINES, prompt="Departement", id="department"),
            Checkbox(label="Actif", value=True, id="is_active"),
            id="form",
        )
        yield Container(
            Button("Annuler", variant="warning", id="cancel_user"),
            Button("Modifier", variant="success", id="update_user"),
            classes="buttons",
        )
