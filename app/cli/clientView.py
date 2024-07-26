from textual.containers import Grid
from textual.widgets import Static, DataTable, Button, Input, Label
from textual.containers import Container
from textual.app import ComposeResult
from app.crud.crud_client import CRUDClient
from app.models.client import Client, ClientCreate
from app.session import get_db
from app.core.security import decode_jwt
from datetime import datetime


class ClientView(Static):
    def __init__(self, user, **kwargs) -> None:
        self.crud_client = CRUDClient(Client)
        self.user = user
        super().__init__(**kwargs)

    TABLE_HEADERS = [
        "ID",
        "Nom complet",
        "Email",
        "Téléphone",
        "Nom de l'entreprise",
        "Créé le",
        "Mis à jour le",
        "Utilisateur",
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
        table.add_columns(*self.TABLE_HEADERS)
        with get_db() as db:
            try:
                clients = self.crud_client.get_multi(db)
                for client in clients:
                    row_data = [
                        client.id,
                        client.full_name,
                        client.email,
                        client.phone,
                        client.company_name,
                        datetime.strftime(client.created_at, "%Y-%m-%d %H:%M:%S"),
                        datetime.strftime(client.updated_at, "%Y-%m-%d %H:%M:%S"),
                        client.full_name,
                    ]
                    table.add_row(*row_data)
            except Exception as e:
                self.log.warning(e)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.name == "add_client":
            self.query(DataTable).remove()
            self.query(Button).remove()
            self.query(Grid).remove()
            self.mount(ClientFormCreate(user=self.user))


class ClientFormCreate(Static):
    def __init__(self, user, **kwargs) -> None:
        self.crud_client = CRUDClient(Client)
        self.user = user
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Nom complet", id="full_name"),
            Input(placeholder="Email", id="email"),
            Input(placeholder="Téléphone", id="phone"),
            Input(placeholder="Nom de l'entreprise", id="company_name"),
            id="form",
        )
        yield Container(
            Button("Annuler", variant="warning", id="cancel"),
            Button("Créer", variant="success", id="create"),
            classes="buttons",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel":
            self.query(Container).remove()
            self.mount(ClientView(user=self.user))
        if event.control.id == "create":
            label = self.query("#invalid-credentials")
            if label:
                label.remove()
            if not all(
                [
                    self.query_one("#full_name", Input).value,
                    self.query_one("#email", Input).value,
                    self.query_one("#phone", Input).value,
                    self.query_one("#company_name", Input).value,
                ]
            ):
                self.mount(
                    Label("Veuillez remplir tous les champs", id="invalid-credentials"),
                    after="#is_active",
                )
                return
            full_name = self.query_one("#full_name", Input).value
            email = self.query_one("#email", Input).value
            phone = self.query_one("#phone", Input).value
            company_name = self.query_one("#company_name", Input).value
            # decode JWT token to get user_id
            user_id = decode_jwt(self.user)["id"]
            with get_db() as db:
                try:
                    client = ClientCreate(
                        email=email,
                        full_name=full_name,
                        phone=phone,
                        company_name=company_name,
                        user_id=user_id,
                    )
                    self.crud_client.create(db, obj_in=client)
                except Exception as e:
                    self.log.warning(e)
            self.query(Container).remove()
            self.mount(ClientView(user=self.user))
