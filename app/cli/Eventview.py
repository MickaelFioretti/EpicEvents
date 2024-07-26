from textual.widgets import Static
from app.crud.crud_event import CRUDEvent
from app.models.event import Event


class EventView(Static):
    def __init__(self, user, **kwargs) -> None:
        self.crud_event = CRUDEvent(Event)
        self.user = user
        super().__init__(**kwargs)

    TABLE_HEADERS = [
        "ID",
        "Nom de l'événement",
        "Date de début",
        "Date de fin",
        "Créé le",
        "Statut",
    ]
