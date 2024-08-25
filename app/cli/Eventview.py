from textual.widgets import Static
from app.crud.crud_event import CRUDEvent
from app.crud.crud_client import CRUDClient
from app.crud.crud_contract import CRUDContract
from app.models.event import Event
from textual.widgets import DataTable, Button, Input, Select, Label
from textual.containers import Container
from textual.app import ComposeResult
from textual.containers import Grid
from app.session import get_db
from app.models.client import Client
from app.models.contract import Contract
from datetime import datetime


class EventView(Static):
    def __init__(self, user, **kwargs) -> None:
        self.crud_event = CRUDEvent(Event)
        self.crud_client = CRUDClient(Client)
        self.crud_contract = CRUDContract(Contract)
        self.user = user
        super().__init__(**kwargs)

    TABLE_HEADERS = [
        "ID",
        "Nom de l'événement",
        "Date de début",
        "Date de fin",
        "Créé le",
        "Statut",
    ]

    selected_event: int = 0

    clients = []
    contracts = []

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button("Ajouter un événement", variant="success", name="add_event"),
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
                events = self.crud_event.get_multi(db)
                clients = self.crud_client.get_multi(db)
                contracts = self.crud_contract.get_multi(db)
                self.clients = clients
                self.contracts = contracts
                for event in events:
                    row_data = [
                        event.id,
                        event.location,
                        event.event_date_start,
                        event.event_date_end,
                        event.created_at,
                        event.status,
                    ]
                    table.add_row(*row_data)
            except Exception as e:
                table.add_row("No data found")
                self.log.warning(e)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.name == "add_event":
            self.query(DataTable).remove()
            self.query(Button).remove()
            self.query(Grid).remove()
            self.mount(EventFormCreate(user=self.user, clients=self.clients))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_user = event.data_table.get_row(event.row_key)[0]
        if self.selected_user != 0:
            self.query("#button-update").remove()
            self.query("#button-delete").remove()
            self.mount(
                Button(
                    "Modifier un événement",
                    variant="success",
                    name="update_user",
                    id="button-update",
                ),
                after="Button",
            )
            self.mount(
                Button(
                    "Supprimer un événement",
                    variant="error",
                    name="delete_user",
                    id="button-delete",
                ),
                after="#button-update",
            )


class EventFormCreate(Static):
    def __init__(self, user, clients, **kwargs) -> None:
        self.crud_contract = CRUDContract(Contract)
        self.user = user
        self.clients = clients
        super().__init__(**kwargs)

    contracts = []

    def on_mount(self) -> None:
        with get_db() as db:
            try:
                contracts = self.crud_contract.get_multi(db)
                for contract in contracts:
                    self.contracts.append({"id": contract.id, "name": contract.client.company_name})
                self.mount(
                    Select.from_values(
                        (f"{contract['id']} - {contract['name']}" for contract in self.contracts),
                        prompt="Contract",
                        id="contract_id",
                    ),
                    after="#company_name",
                )
            except Exception as e:
                self.log.warning(e)

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Event date start dd/mm/yyyy", id="event_date_start", type="text"),
            Input(placeholder="Event date end dd/mm/yyyy", id="event_date_end", type="text"),
            Input(placeholder="Location", id="location", type="text"),
            Input(placeholder="Attendees", id="attendees", type="number"),
            Input(placeholder="Notes", id="notes", type="text"),
            Select.from_values(
                (client.company_name for client in self.clients),
                prompt="Nom de l'entreprise",
                id="company_name",
            ),
            id="form",
        )
        yield Container(
            Button("Annuler", variant="warning", id="cancel"),
            Button("Créer", variant="success", id="submit"),
            classes="buttons",
        )

    def is_valid_date(self, date_str: str) -> bool:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        print(self.contracts)
        if event.control.id == "cancel":
            self.query(Static).remove()
            self.mount(EventView(user=self.user))
        if event.control.id == "submit":
            label = self.query("#invalid-credentials")
            if label:
                label.remove()
            if not all(
                [
                    self.query_one("#event_date_start", Input).value,
                    self.query_one("#event_date_end", Input).value,
                    self.query_one("#location", Input).value,
                    self.query_one("#attendees", Input).value,
                    self.query_one("#notes", Input).value,
                    self.query_one("#company_name", Select).value != Select.BLANK,
                    self.query_one("#contract_id", Select).value != Select.BLANK,
                ]
            ):
                self.mount(
                    Label("Veuillez remplir tous les champs", id="invalid-credentials"),
                    after="#contract_id",
                )
                return
            event_date_start = self.query_one("#event_date_start", Input).value
            event_date_end = self.query_one("#event_date_end", Input).value
            location = self.query_one("#location", Input).value
            attendees = self.query_one("#attendees", Input).value
            notes = self.query_one("#notes", Input).value
            client_id = self.query_one("#company_name", Select).value
            contract_id = self.query_one("#contract_id", Select).value

            if not self.is_valid_date(event_date_start) or not self.is_valid_date(event_date_end):
                if label:
                    label.remove()
                self.mount(
                    Label("Veuillez entrer une date valide", id="invalid-credentials"),
                    after="#contract_id",
                )
                return

            print(
                event_date_start, event_date_end, location, attendees, notes, client_id, contract_id
            )

            # with get_db() as db:
            #     try:
            #         event = EventCreate(
            #             event_date_start=event_date_start,
            #             event_date_end=event_date_end,
            #             location=location,
            #             attendees=attendees,
            #             notes=notes,
            #             client_id=client_id,
            #             contract_id=contract_id,
            #         )
            #         pass
            #     except Exception as e:
            #         self.log.warning(e)
