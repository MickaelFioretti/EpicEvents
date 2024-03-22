from textual import on
from textual.widgets import Static, Button, Input, Label
from textual.app import ComposeResult
from app.session import get_db
from app.crud.crud_user import CRUDUser
from app.models.user import User, UserAuthenticate


class LoginForm(Static):
    status_connection = ""

    def __init__(self) -> None:
        super().__init__()
        self.crud_user = CRUDUser(User)

    @on(Button.Pressed)
    def on_button_pressed(self) -> None:
        email = self.query_one("#email", Input).value
        password = self.query_one("#password", Input).value

        with get_db() as db:
            try:
                user_info = UserAuthenticate(email=email, password=password)

                user = self.crud_user.authenticate(db, obj_in=user_info)
            except Exception as e:
                print(e)
                user = None

            if user:
                # L'authentification a réussi
                self.status_connection = "Connecté en tant que " + user.email
                # Ici, vous pouvez naviguer vers une autre page ou effectuer d'autres actions
            else:
                # Échec de l'authentification
                self.status_connection = "Échec de l'authentification"

        self.query_one("#email", Input).value = ""
        self.query_one("#password", Input).value = ""

    def compose(self) -> ComposeResult:
        yield Label("Status: " + self.status_connection, id="status_connection")
        yield Input(placeholder="Email", id="email")
        yield Input(placeholder="Password", id="password")
        yield Button("Login", id="login", variant="success")
