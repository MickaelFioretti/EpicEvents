from textual.containers import Grid
from textual.widgets import Static, DataTable, Button, Input
from textual.containers import Container
from textual.app import ComposeResult
from app.crud.crud_client import CRUDClient
from app.models.client import Client
from app.session import get_db


class ClientView(Static):
    def __init__(self, **kwargs) -> None:
        self.crud_client = CRUDClient(Client)
        super().__init__(**kwargs)

    TABLE_DATA = [
        ("id", "full_name", "email", "phone", "company_name", "created_at", "updated_at", "user_id")
    ]
    selected_client: int = 0

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button("Ajouter un client", variant="success", name="add_client"),
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
                clients = self.crud_client.get_multi(db)
                for client in clients:
                    table.add_row(*[getattr(client, column) for column in self.TABLE_DATA[0]])
            except Exception as e:
                self.log.warning(e)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.name == "add_client":
            self.query(DataTable).remove()
            self.query(Button).remove()
            self.query(Grid).remove()
            self.mount(ClientFormCreate())


class ClientFormCreate(Static):
    def compose(self) -> ComposeResult:
        yield Container(
            Input("Nom complet", name="full_name"),
            Input("Email", name="email"),
            Input("Téléphone", name="phone"),
            Input("Nom de l'entreprise", name="company_name"),
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
            self.mount(ClientView())
