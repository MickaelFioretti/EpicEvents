from textual.widgets import Static, Button, Input
from textual.app import ComposeResult


class LoginDisplay(Static):
    pass


class LoginForm(Static):
    def on_button_pressed(self, event: Button.Pressed) -> None:
        pass

    def compose(self) -> ComposeResult:
        yield Input("Email", id="email")
        yield Input("Password", id="password")
        yield Button("Login", id="login", variant="success")
