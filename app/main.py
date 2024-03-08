from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from cli.login.login import LoginForm


class MyApp(App):
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield LoginForm()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


if __name__ == "__main__":
    app = MyApp()
    app.run()
