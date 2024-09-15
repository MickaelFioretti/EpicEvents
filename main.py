from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from app.cli.login import LoginForm
from app.cli.dashboard import Dashboard
from app.cli.userView import UserView
from app.cli.clientView import ClientView
from app.cli.contractView import ContractView
from app.cli.Eventview import EventView

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

logging.basicConfig(level=logging.DEBUG)

# Initialiser Sentry avec l'intégration de logging
sentry_logging = LoggingIntegration(
    level=logging.INFO,  # Capture info and above as breadcrumbs
    event_level=logging.ERROR,  # Send errors as events
)

sentry_sdk.init(
    dsn="https://2f49aa2397861af51f481a23604163b9@o4507741033070592.ingest.de.sentry.io/4507957996879952",
    integrations=[sentry_logging],
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)


class MyApp(App):
    CSS_PATH = "app/style.tcss"
    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    user_token: str | None = None
    last_path: str = ""

    def compose(self) -> ComposeResult:
        yield Header()
        yield LoginForm(id="login-form")
        yield Footer()

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

    def on_login_form_login(self, message: LoginForm.Login) -> None:
        print("User logged in the app")
        access_token = message.user["access_token"]
        self.user_token = access_token
        self.query("#login-form").remove()
        self.mount(Dashboard(id="dashboard", user=self.user_token), after="Header")

    def on_dashboard_path(self, message: Dashboard.Path) -> None:
        # router
        match message.path:
            case "Dashboard":
                if self.last_path != "Dashboard" and self.last_path != "":
                    self.query(f"#{self.last_path}").remove()
            case "EventView":
                if self.last_path == "EventView":
                    pass
                else:
                    if self.last_path != "":
                        self.query(f"#{self.last_path}").remove()
                    self.mount(EventView(id="EventView", user=self.user_token), after="Header")
            case "ClientView":
                if self.last_path == "ClientView":
                    pass
                else:
                    if self.last_path != "":
                        self.query(f"#{self.last_path}").remove()
                    self.mount(ClientView(id="ClientView", user=self.user_token), after="Header")
            case "ContractView":
                if self.last_path == "ContractView":
                    pass
                else:
                    if self.last_path != "":
                        self.query(f"#{self.last_path}").remove()
                    self.mount(
                        ContractView(id="ContractView", user=self.user_token), after="Header"
                    )
            case "UserView":
                if self.last_path == "UserView":
                    pass
                else:
                    if self.last_path != "":
                        self.query(f"#{self.last_path}").remove()
                    self.mount(UserView(id="UserView"), after="Header")
            case "logout":
                self.user_token = None
                self.query("#dashboard").remove()
                self.query(f"#{self.last_path}").remove()
                self.mount(LoginForm(id="login-form"), after="Header")
            case _:
                print("default")

        self.last_path = message.path


if __name__ == "__main__":
    MyApp().run()
