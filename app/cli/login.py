from textual import on
from textual.widgets import Static, Button, Input
from textual.app import ComposeResult


class LoginForm(Static):
    @on(Button.Pressed)
    def on_button_pressed(self) -> None:
        email = self.query_one("#email", Input).value
        password = self.query_one("#password", Input).value

        self.query_one("#email", Input).value = ""
        self.query_one("#password", Input).value = ""

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Email", id="email")
        yield Input(placeholder="Password", id="password")
        yield Button("Login", id="login", variant="success")
