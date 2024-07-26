from textual.widgets import Static
from app.crud.crud_contract import CRUDContract
from app.models.contract import Contract
from textual.app import ComposeResult
from textual.containers import Grid
from textual.widgets import DataTable, Button
from textual.containers import Container
from app.session import get_db


class ContractView(Static):
    def __init__(self, user, **kwargs) -> None:
        self.crud_contract = CRUDContract(Contract)
        self.user = user
        super().__init__(**kwargs)

    TABLE_HEADERS = [
        "ID",
        "Montant total",
        "Montant restant",
        "Statut",
        "Nom de l'entreprise",
        "Créé le",
        "Utilisateur",
    ]

    selected_contract: int = 0

    def compose(self) -> ComposeResult:
        with Grid():
            yield Container(
                Button("Ajouter un contrat", variant="success", name="add_contract"),
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
                contracts = self.crud_contract.get_multi(db)
                for contract in contracts:
                    row_data = [
                        contract.id,
                        contract.total_amount,
                        contract.remaining_amount,
                        contract.status,
                        contract.client.company_name,
                        contract.created_at,
                        contract.user.full_name,
                    ]
                    table.add_row(*row_data)
            except Exception as e:
                self.log.warning(e)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.control.name == "add_contract":
            self.query(DataTable).remove()
            self.query(Button).remove()
            self.query(Grid).remove()
