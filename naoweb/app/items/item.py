from app.items.persistence import idGenerator
from datetime import datetime
from dateutil import tz


class Item:

    def __init__(self):
        self.id = next(idGenerator)
        self.creationdatetime = datetime.now(tz.gettz("Europe/Riga"))
        self.viewtime = self.creationdatetime.strftime("%c")
