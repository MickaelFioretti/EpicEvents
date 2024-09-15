from textual.widgets import Static
from app.core.security import decode_jwt
from app.crud.crud_event import CRUDEvent
from app.crud.crud_client import CRUDClient
from app.crud.crud_contract import CRUDContract
from app.crud.crud_user import CRUDUser
from app.models.event import Event, EventCreate, EventUpdate
from textual.widgets import DataTable, Button, Input, Select, Label
from textual.containers import Container
from textual.app import ComposeResult
from textual.containers import Grid
from app.models.user import DepartmentEnum, User
from app.session import get_db
from app.models.client import Client, ClientRead
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
        "Localisation",
        "Participants",
        "Notes",
        "Date de début",
        "Date de fin",
        "Numéro de contrat",
        "Nom de l'entreprise",
        "Support",
    ]

    selected_event: int = 0

    clients = []
    contracts = []
    filter_active = False

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button("Ajouter un événement", variant="success", name="add_event"),
                Button("Filtre", variant="default", name="filter"),
                classes="button-container",
            )

            yield Container(
                DataTable(cursor_type="row", id="events_table"),
                classes="table",
            )

    def on_mount(self) -> None:
        self.load_events()

    def load_events(self) -> None:
        table = self.query_one("#events_table", DataTable)
        table.clear(columns=True)
        table.add_columns(*self.TABLE_HEADERS)
        with get_db() as db:
            try:
                events = self.crud_event.get_multi(db)
                self.clients = self.crud_client.get_multi(db)
                contracts = self.crud_contract.get_multi(db)
                self.contracts = contracts
                for event in events:
                    # ci filter_active et true alors on afficher tous les event avec un event.user None
                    if not self.filter_active or (self.filter_active and event.user is None):
                        row_data = [
                            event.id,
                            event.location,
                            event.attendees,
                            event.notes,
                            event.event_date_start.strftime("%d/%m/%Y"),
                            event.event_date_end.strftime("%d/%m/%Y"),
                            event.contract_id,
                            event.client.company_name,
                            event.user.full_name,
                        ]
                        table.add_row(*row_data)
            except Exception as e:
                table.add_row("No data found")
                self.log.warning(e)

    def has_permission(self, required_departments):
        user_department = decode_jwt(self.user)["department"]
        # Allow access if required_departments is empty
        if not required_departments:
            return True
        return user_department in required_departments

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.name == "add_event":
            if self.has_permission([DepartmentEnum.gestion]):
                self.query(DataTable).remove()
                self.query(Button).remove()
                self.query(Grid).remove()
                self.mount(EventFormCreate(user=self.user, clients=self.clients))
        if event.control.name == "update_event":
            if self.has_permission([DepartmentEnum.gestion]):
                self.query(DataTable).remove()
                self.query(Button).remove()
                self.query(Grid).remove()
                self.mount(
                    EventFormUpdate(user=self.user, event=self.selected_event, clients=self.clients)
                )
        if event.control.name == "delete_event":
            if self.has_permission([DepartmentEnum.gestion]):
                with get_db() as db:
                    try:
                        self.crud_event.remove(db, id=self.selected_event)
                        self.query(DataTable).remove()
                        self.query(Button).remove()
                        self.query(Grid).remove()
                        self.mount(EventView(user=self.user))
                    except Exception as e:
                        self.log.warning(e)
        if event.control.name == "filter":
            if self.filter_active:
                self.filter_active = False
                self.load_events()
            else:
                self.filter_active = True
                self.load_events()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_event = event.data_table.get_row(event.row_key)[0]
        if self.selected_event != 0:
            self.query("#button-update").remove()
            self.query("#button-delete").remove()
            self.mount(
                Button(
                    "Modifier un événement",
                    variant="success",
                    name="update_event",
                    id="button-update",
                ),
                after="Button",
            )


class EventFormCreate(Static):
    def __init__(self, user, clients, **kwargs) -> None:
        self.crud_contract = CRUDContract(Contract)
        self.crud_event = CRUDEvent(Event)
        self.user = user
        self.clients: list[ClientRead] = clients
        super().__init__(**kwargs)

    contracts = []

    def on_mount(self) -> None:
        contracts = []
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
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel":
            self.query(Container).remove()
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

            if not self.is_valid_date(event_date_start) or not self.is_valid_date(event_date_end):
                if label:
                    label.remove()
                self.mount(
                    Label("Veuillez entrer une date valide", id="invalid-credentials"),
                    after="#contract_id",
                )
                return

            location = self.query_one("#location", Input).value
            attendees = self.query_one("#attendees", Input).value
            notes = self.query_one("#notes", Input).value
            client_id = self.query_one("#company_name", Select).value
            contract_id = str(self.query_one("#contract_id", Select).value)

        with get_db() as db:
            try:
                event_create = EventCreate(
                    event_date_start=datetime.strptime(event_date_start, "%d/%m/%Y"),
                    event_date_end=datetime.strptime(event_date_end, "%d/%m/%Y"),
                    location=location,
                    attendees=int(attendees),
                    notes=notes,
                    client_id=[
                        client.id for client in self.clients if client.company_name == client_id
                    ][0],
                    contract_id=[
                        contract["id"]
                        for contract in self.contracts
                        if contract["name"] == contract_id.split(" - ")[1]
                    ][0],
                )
                self.crud_event.create(db, obj_in=event_create)
                self.query(Container).remove()
                self.mount(EventView(user=self.user))
            except Exception as e:
                self.log.warning(e)


class EventFormUpdate(Static):
    def __init__(self, user, event, clients, **kwargs) -> None:
        self.crud_event = CRUDEvent(Event)
        self.user = user
        self.event = event
        self.clients: list[ClientRead] = clients
        self.crud_contract = CRUDContract(Contract)
        self.crud_user = CRUDUser(User)
        super().__init__(**kwargs)

    event_db: Event
    contracts = []
    users = []

    def on_mount(self) -> None:
        with get_db() as db:
            try:
                event_update = self.crud_event.get(db, id=self.event)
                self.event_db = event_update
                self.users = self.crud_user.get_multi(db)
                contracts = self.crud_contract.get_multi(db)
                for contract in contracts:
                    self.contracts.append({"id": contract.id, "name": contract.client.company_name})
                if event_update:
                    self.query_one(
                        "#event_date_start", Input
                    ).value = event_update.event_date_start.strftime("%d/%m/%Y")
                    self.query_one(
                        "#event_date_end", Input
                    ).value = event_update.event_date_end.strftime("%d/%m/%Y")
                    self.query_one("#location", Input).value = event_update.location
                    self.query_one("#attendees", Input).value = str(event_update.attendees)
                    self.query_one("#notes", Input).value = event_update.notes
                    self.query_one("#company_name", Select).value = event_update.client.company_name
                    self.mount(
                        Select.from_values(
                            (
                                f"{contract['id']} - {contract['name']}"
                                for contract in self.contracts
                            ),
                            prompt=f"{event_update.contract_id} - {event_update.contract.client.company_name}",
                            id="contract_id",
                        ),
                        after="#company_name",
                    )
                    self.mount(
                        Select.from_values(
                            (user.full_name for user in self.users),
                            prompt=f"{event_update.user.full_name}",
                            id="support",
                        ),
                        after="#contract_id",
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
            Button("Modifier", variant="success", id="submit"),
            classes="buttons",
        )

    def is_valid_date(self, date_str: str) -> bool:
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel":
            self.query(Container).remove()
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
                ]
            ):
                self.mount(
                    Label("Veuillez remplir tous les champs", id="invalid-credentials"),
                    after="#support",
                )
                return

            event_date_start = self.query_one("#event_date_start", Input).value
            event_date_end = self.query_one("#event_date_end", Input).value

            if not self.is_valid_date(event_date_start) or not self.is_valid_date(event_date_end):
                if label:
                    label.remove()
                self.mount(
                    Label("Veuillez entrer une date valide", id="invalid-credentials"),
                    after="#support",
                )
                return

            location = self.query_one("#location", Input).value
            attendees = self.query_one("#attendees", Input).value
            notes = self.query_one("#notes", Input).value
            client_id = self.query_one("#company_name", Select).value
            contract_id = self.query_one("#contract_id", Select).value
            if contract_id == Select.BLANK:
                contract_id = self.query_one("#contract_id", Select).prompt
            support = self.query_one("#support", Select).value
            if support == Select.BLANK:
                support = self.query_one("#support", Select).prompt

        with get_db() as db:
            try:
                event_update = EventUpdate(
                    event_date_start=datetime.strptime(event_date_start, "%d/%m/%Y"),
                    event_date_end=datetime.strptime(event_date_end, "%d/%m/%Y"),
                    location=location,
                    attendees=int(attendees),
                    notes=notes,
                    client_id=[
                        client.id for client in self.clients if client.company_name == client_id
                    ][0],
                    contract_id=[
                        contract["id"]
                        for contract in self.contracts
                        if contract["name"] == str(contract_id).split(" - ")[1]
                    ][0],
                    user_id=[user.id for user in self.users if user.full_name == support][0],
                )

                self.crud_event.update(db, db_obj=self.event_db, obj_in=event_update)
                self.query(Container).remove()
                self.mount(EventView(user=self.user))
            except Exception as e:
                self.log.warning(e)
