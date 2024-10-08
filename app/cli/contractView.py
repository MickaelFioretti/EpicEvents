from typing import cast
from app.crud.crud_contract import CRUDContract
from app.models.contract import Contract, ContractCreate, ContractUpdate, StatusContractEnum
from app.models.client import Client
from app.crud.crud_client import CRUDClient
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import DataTable, Button, Input, Static, Label, Select
from textual.containers import Container
from app.models.user import DepartmentEnum
from app.session import get_db
from app.core.security import decode_jwt


class ContractView(Static):
    def __init__(self, user, **kwargs) -> None:
        self.crud_contract = CRUDContract(Contract)
        self.crud_client = CRUDClient(Client)
        self.user = user
        super().__init__(**kwargs)

    TABLE_HEADERS = [
        "ID",
        "Nom de l'entreprise",
        "Statut",
        "Créé le",
        "Utilisateur",
        "Montant total",
        "Montant restant",
    ]

    selected_contract: int = 0
    clients = []
    contracts = []
    filter_active = False

    with get_db() as db:
        try:
            contracts = CRUDContract(Contract).get_multi(db)
        except Exception as e:
            print(e)

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button(
                    "Ajouter un contrat", variant="success", name="add_contract", id="button-add"
                ),
                Button("Filtre", variant="default", name="filter"),
                classes="button-container",
            )

            yield Container(
                DataTable(cursor_type="row", id="contract_table"),
                classes="table",
            )

    def on_mount(self) -> None:
        self.load_contracts()

    def load_contracts(self, filter_user_id=None) -> None:
        table = self.query_one("#contract_table", DataTable)
        table.clear(columns=True)
        table.add_columns(*self.TABLE_HEADERS)
        with get_db() as db:
            try:
                self.contracts = self.crud_contract.get_multi(db)
                self.clients = self.crud_client.get_multi(db)
                for contract in self.contracts:
                    if filter_user_id is None or contract.user_id == filter_user_id:
                        table.add_row(
                            str(contract.id),
                            contract.client.company_name,
                            contract.status,
                            contract.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            contract.user.full_name,
                            str(contract.total_amount),
                            str(contract.remaining_amount),
                        )
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
        if event.control.name == "add_contract":
            if self.has_permission([DepartmentEnum.gestion]):
                self.query(DataTable).remove()
                self.query(Button).remove()
                self.query(Grid).remove()
                self.mount(ContractFormCreate(user=self.user, clients=self.clients))
        if event.control.name == "update_contract":
            if self.has_permission([DepartmentEnum.gestion]):
                self.query(DataTable).remove()
                self.query(Button).remove()
                self.query(Grid).remove()
                self.mount(
                    ContractFormUpdate(
                        user=self.user, clients=self.clients, contract_id=self.selected_contract
                    )
                )
        if event.control.name == "delete_contract":
            if self.has_permission([DepartmentEnum.gestion]):
                with get_db() as db:
                    try:
                        if self.selected_contract:
                            self.crud_contract.remove(db, id=self.selected_contract)
                    except Exception as e:
                        self.log.warning(e)
        if event.control.name == "filter":
            if self.filter_active:
                self.load_contracts()
                self.filter_active = False
            else:
                filter_user_id = decode_jwt(self.user)["id"]
                self.load_contracts(filter_user_id)
                self.filter_active = True

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self.selected_contract = event.data_table.get_row(event.row_key)[0]
        if self.selected_contract != 0:
            self.query("#button-update").remove()
            self.query("#button-delete").remove()
            self.mount(
                Button(
                    "Modifier un contrat",
                    variant="success",
                    name="update_contract",
                    id="button-update",
                ),
                after="#button-add",
            )


LINES = StatusContractEnum.__members__.keys()


class ContractFormCreate(Static):
    def __init__(self, user, clients, **kwargs) -> None:
        self.crud_contract = CRUDContract(Contract)
        self.user = user
        self.clients = clients
        super().__init__(**kwargs)

    def compose(self) -> ComposeResult:
        yield Container(
            Select.from_values(
                (client.company_name for client in self.clients),
                prompt="Nom de l'entreprise",
                id="company_name",
            ),
            Input(placeholder="Montant total", id="total_amount", type="number"),
            Input(placeholder="Montant restant", id="remaining_amount"),
            Select.from_values(LINES, prompt="Statut", id="status"),
            id="form",
        )
        yield Container(
            Button("Annuler", variant="warning", id="cancel"),
            Button("Créer", variant="success", id="submit"),
            classes="buttons",
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel":
            self.query(Container).remove()
            self.mount(ContractView(user=self.user))
        if event.control.id == "submit":
            label = self.query("#invalid-credentials")
            if label:
                label.remove()
            if not all(
                [
                    self.query_one("#company_name", Select).value != Select.BLANK,
                    self.query_one("#total_amount", Input).value,
                    self.query_one("#remaining_amount", Input).value,
                    self.query_one("#status", Select).value != Select.BLANK,
                ]
            ):
                self.mount(
                    Label("Veuillez remplir tous les champs", id="invalid-credentials"),
                    after="#is_active",
                )
                return

            company_name = self.query_one("#company_name", Select).value
            total_amount = self.query_one("#total_amount", Input).value
            remaining_amount = self.query_one("#remaining_amount", Input).value
            status = cast(StatusContractEnum, self.query_one("#status", Select).value)
            # decode JWT token to get user_id
            user_id = decode_jwt(self.user)["id"]
            with get_db() as db:
                try:
                    contract = ContractCreate(
                        total_amount=float(total_amount),
                        remaining_amount=float(remaining_amount),
                        status=status,
                        client_id=[
                            client.id
                            for client in self.clients
                            if client.company_name == company_name
                        ][0],
                        user_id=user_id,
                    )
                    self.crud_contract.create(db, obj_in=contract)
                    self.query(Container).remove()
                    self.mount(ContractView(user=self.user))
                except Exception as e:
                    self.log.warning(e)


class ContractFormUpdate(Static):
    def __init__(self, user, clients, contract_id: int, **kwargs) -> None:
        self.crud_contract = CRUDContract(Contract)
        self.clients = clients
        self.user = user
        self.contract_id = contract_id
        super().__init__(**kwargs)

    contract_db: Contract

    def on_mount(self) -> None:
        with get_db() as db:
            try:
                contract = self.crud_contract.get(db, id=self.contract_id)
                if contract:
                    self.contract_db = contract
                    self.query_one("#company_name", Select).prompt = contract.client.company_name
                    self.query_one("#total_amount", Input).value = str(contract.total_amount)
                    self.query_one("#remaining_amount", Input).value = str(
                        contract.remaining_amount
                    )
                    self.query_one("#status", Select).value = contract.status
            except Exception as e:
                self.log.warning(e)

    def compose(self) -> ComposeResult:
        yield Container(
            Select.from_values(
                (client.company_name for client in self.clients),
                prompt="",
                id="company_name",
            ),
            Input(placeholder="Montant total", id="total_amount", type="number"),
            Input(placeholder="Montant restant", id="remaining_amount"),
            Select.from_values(LINES, prompt="Statut", id="status"),
            id="form",
        )
        yield Container(
            Button("Annuler", variant="warning", id="cancel"),
            Button("Modifier", variant="success", id="submit"),
            classes="buttons",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.id == "cancel":
            self.query(Container).remove()
            self.mount(ContractView(user=self.user))
        if event.control.id == "submit":
            label = self.query("#invalid-credentials")
            if label:
                label.remove()
            if not all(
                [
                    self.query_one("#company_name", Select).value,
                    self.query_one("#total_amount", Input).value,
                    self.query_one("#remaining_amount", Input).value,
                    self.query_one("#status", Select).value != Select.BLANK,
                ]
            ):
                self.mount(
                    Label("Veuillez remplir tous les champs", id="invalid-credentials"),
                    after="#is_active",
                )
                return
            company_name = self.query_one("#company_name", Select).value
            total_amount = self.query_one("#total_amount", Input).value
            remaining_amount = self.query_one("#remaining_amount", Input).value
            status = cast(StatusContractEnum, self.query_one("#status", Select).value)
            with get_db() as db:
                try:
                    contract = ContractUpdate(
                        total_amount=float(total_amount),
                        remaining_amount=float(remaining_amount),
                        status=status,
                        client_id=[
                            client.id
                            for client in self.clients
                            if client.company_name == company_name
                        ][0],
                        user_id=self.contract_db.user_id,
                    )
                    self.crud_contract.update(db, db_obj=self.contract_db, obj_in=contract)
                    self.query(Container).remove()
                    self.mount(ContractView(user=self.user))
                except Exception as e:
                    self.log.warning(e)
