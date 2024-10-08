from textual.containers import Grid
from textual.widgets import Static, DataTable, Button, Input, Label
from textual.containers import Container
from textual.app import ComposeResult
from app.crud.crud_client import CRUDClient
from app.models.client import Client, ClientCreate, ClientUpdate
from app.models.user import DepartmentEnum
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
    filter_active = False
    clients = []

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button("Ajouter un client", variant="success", name="add_client", id="add_client"),
                Button("Filtre", variant="default", name="filter"),
                classes="button-container",
            )

            yield Container(
                DataTable(cursor_type="row", id="client_table"),
                classes="table",
            )

    def on_mount(self) -> None:
        self.load_clients()

    def load_clients(self, filter_user_id=None) -> None:
        table = self.query_one("#client_table", DataTable)
        table.clear(columns=True)
        table.add_columns(*self.TABLE_HEADERS)
        with get_db() as db:
            try:
                self.clients = self.crud_client.get_multi(db)
                for client in self.clients:
                    if filter_user_id is None or client.user_id == filter_user_id:
                        row_data = [
                            client.id,
                            client.full_name,
                            client.email,
                            client.phone,
                            client.company_name,
                            datetime.strftime(client.created_at, "%Y-%m-%d"),
                            datetime.strftime(client.updated_at, "%Y-%m-%d"),
                            client.user.full_name,
                        ]
                        table.add_row(*row_data)
            except Exception as e:
                self.log.warning(e)

    def has_permission(self, required_departments):
        user_department = decode_jwt(self.user)["department"]
        # Allow access if required_departments is empty
        if not required_departments:
            return True
        return user_department in required_departments

    def is_client_owned_by_user(self, client_id):
        with get_db() as db:
            client = self.crud_client.get(db, id=client_id)
            if not client:
                return False
            return client.user_id == decode_jwt(self.user)["id"]

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        label = self.query("#invalid-credentials")
        if label:
            label.remove()
        if event.control.name == "add_client":
            if self.has_permission([DepartmentEnum.commercial]):
                self.query(DataTable).remove()
                self.query(Button).remove()
                self.query(Grid).remove()
                self.mount(ClientFormCreate(user=self.user))
        if event.control.name == "update_client":
            if self.has_permission([DepartmentEnum.gestion, DepartmentEnum.commercial]):
                if self.is_client_owned_by_user(self.selected_client):
                    self.query(DataTable).remove()
                    self.query(Button).remove()
                    self.query(Grid).remove()
                    self.mount(ClientFormUpdate(client_id=self.selected_client, user=self.user))
                else:
                    self.mount(
                        Label(
                            "Vous ne pouvez pas modifier un client qui ne vous appartient pas !",
                            id="invalid-credentials",
                        ),
                        before="#client_table",
                    )
        if event.control.name == "delete_client":
            if self.has_permission([DepartmentEnum.gestion]):
                with get_db() as db:
                    try:
                        if self.selected_client:
                            self.crud_client.remove(db, id=self.selected_client)
                    except Exception as e:
                        self.log.warning(e)
        if event.control.name == "filter":
            if self.filter_active:
                self.load_clients()
                self.filter_active = False
            else:
                filter_user_id = decode_jwt(self.user)["id"]
                self.load_clients(filter_user_id)
                self.filter_active = True

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_client = event.data_table.get_row(event.row_key)[0]
        if self.selected_client != 0:
            self.query("#button-update").remove()
            self.query("#button-delete").remove()
            self.mount(
                Button(
                    "Modifier un client",
                    variant="success",
                    name="update_client",
                    id="button-update",
                ),
                after="#add_client",
            )


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


class ClientFormUpdate(Static):
    def __init__(self, client_id, user, **kwargs) -> None:
        self.crud_client = CRUDClient(Client)
        self.client_id = client_id
        self.user = user
        super().__init__(**kwargs)

    client_db: Client

    def on_mount(self) -> None:
        with get_db() as db:
            try:
                client = self.crud_client.get(db, id=self.client_id)
                if client:
                    self.client_db = client
                    self.query_one("#full_name", Input).value = client.full_name
                    self.query_one("#email", Input).value = client.email
                    self.query_one("#phone", Input).value = client.phone
                    self.query_one("#company_name", Input).value = client.company_name
                else:
                    self.mount(ClientView(user=self.user))
            except Exception as e:
                self.log.warning(e)

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
            Button("Mettre à jour", variant="success", id="update"),
            classes="buttons",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel":
            self.query(Container).remove()
            self.mount(ClientView(user=self.user))
        if event.control.id == "update":
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
            with get_db() as db:
                try:
                    client = ClientUpdate(
                        email=email,
                        full_name=full_name,
                        phone=phone,
                        company_name=company_name,
                    )
                    self.crud_client.update(db, db_obj=self.client_db, obj_in=client)
                except Exception as e:
                    self.log.warning(e)
            self.query(Container).remove()
            self.mount(ClientView(user=self.user))
