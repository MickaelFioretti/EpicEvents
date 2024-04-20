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
        yield Button("Evenements", variant="success")
        yield Button("Clients", variant="success")
        yield Button("Contrats", variant="success")
        yield Button("Utilisateurs", variant="success", name="UserList")
        yield Button("Deconnexion", variant="success", name="logout")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name is not None:
            self.post_message(self.Path(event.button.name))
