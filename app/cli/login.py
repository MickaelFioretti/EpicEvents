from typing import Dict
from textual.widgets import Button, Input, Label, Static
from textual.app import ComposeResult
from textual.reactive import reactive
from app.session import get_db
from app.crud.crud_user import CRUDUser
from app.models.user import User, UserAuthenticate
from textual.message import Message


class LoginForm(Static):
    user = reactive(None)

    def __init__(self, **kwargs) -> None:
        self.crud_user = CRUDUser(User)
        super().__init__(**kwargs)

    class Login(Message):
        def __init__(self, user: Dict[str, str]) -> None:
            self.user = user
            super().__init__()

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Email", id="email", value="admin@admin.com")
        yield Input(placeholder="Password", id="password", value="changethis")
        yield Button("Login", id="login", variant="success")

    async def on_button_pressed(self, event: Button.Pressed) -> User | None:
        email = self.query_one("#email", Input).value
        password = self.query_one("#password", Input).value
        label = self.query("#invalid-credentials")
        if label:
            label.remove()

        with get_db() as db:
            try:
                user_info = UserAuthenticate(email=email, password=password)

                user = self.crud_user.authenticate(db, obj_in=user_info)
            except Exception as e:
                self.log.warning(e)
                user = None

            if user is not None:
                self.query_one("#email", Input).value = ""
                self.query_one("#password", Input).value = ""
                self.post_message(self.Login(user))
            else:
                self.mount(Label("Invalid credentials", id="invalid-credentials"))
