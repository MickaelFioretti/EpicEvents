from textual.widgets import Static, Button
from textual.app import ComposeResult
from textual.message import Message

from app.core.security import decode_jwt
from app.models.user import DepartmentEnum


class Dashboard(Static):
    def __init__(self, user, **kwargs) -> None:
        self.user = decode_jwt(user)
        super().__init__(**kwargs)

    path = "home"

    class Path(Message):
        def __init__(self, path: str) -> None:
            self.path = path
            super().__init__()

    def has_permission(self, department, required_departments):
        if not required_departments:
            return True
        return department in required_departments

    def compose(self) -> ComposeResult:
        user_department = self.user["department"]

        # Define the buttons with their required permissions
        buttons = [
            ("Accueil", "Dashboard", []),
            ("Evenements", "EventView", []),
            ("Clients", "ClientView", []),
            ("Contrats", "ContractView", []),
            ("Utilisateurs", "UserView", []),
            ("Deconnexion", "logout", [DepartmentEnum.gestion]),
        ]

        # Generate buttons based on permissions
        for label, name, required_departments in buttons:
            if self.has_permission(user_department, required_departments):
                yield Button(label, variant="success", name=name)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name is not None:
            self.post_message(self.Path(event.button.name))
