from textual.widgets import Static, Button
from textual.app import ComposeResult
from textual.message import Message


class Dashboard(Static):
    path = "home"

    class Path(Message):
        def __init__(self, path: str) -> None:
            self.path = path
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Button("Accueil", variant="success", name="Dashboard")
        yield Button("Evenements", variant="success", name="EventView")
        yield Button("Clients", variant="success", name="ClientView")
        yield Button("Contrats", variant="success", name="ContractView")
        yield Button("Utilisateurs", variant="success", name="UserView")
        yield Button("Deconnexion", variant="success", name="logout")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name is not None:
            self.post_message(self.Path(event.button.name))
