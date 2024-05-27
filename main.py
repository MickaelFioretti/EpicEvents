from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from app.cli.login import LoginForm
from app.cli.dashboard import Dashboard
from app.cli.userList import UserList
from app.cli.clientView import ClientView


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
        self.mount(Dashboard(id="dashboard"), after="Header")

    def on_dashboard_path(self, message: Dashboard.Path) -> None:
        # router
        match message.path:
            case "Dashboard":
                if self.last_path != "Dashboard" and self.last_path != "":
                    self.query(f"#{self.last_path}").remove()
            case "events":
                print("events")
            case "ClientView":
                if self.last_path == "ClientView":
                    pass
                else:
                    if self.last_path != "":
                        self.query(f"#{self.last_path}").remove()
                    self.mount(ClientView(id="ClientView", user=self.user_token), after="Header")
            case "contracts":
                print("contracts")
            case "UserList":
                if self.last_path == "UserList":
                    pass
                else:
                    if self.last_path != "":
                        self.query(f"#{self.last_path}").remove()
                    self.mount(UserList(id="UserList"), after="Header")
            case "logout":
                self.user_token = None
                self.query("#dashboard").remove()
                self.query(f"#{self.last_path}").remove()
                self.mount(LoginForm(id="login-form"), after="Header")
            case _:
                print("default")

        self.last_path = message.path


if __name__ == "__main__":
    app = MyApp()
    app.run()
