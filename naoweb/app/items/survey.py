import time
from threading import Timer
from typing import List
from datetime import datetime, timedelta
from dateutil import tz

from app.items.item import Item

from app.items.persistence import surveys, pinGenerator


class Survey(Item):

    def __init__(self, question: str, options: List[str], timelimit: int = None, status: str = "Draft"):
        super().__init__()
        self.deadline = None
        self.options = options
        self.question = question
        self.timelimit = timelimit
        self.status = status
        self.results = dict([(i, 0) for i in options])
        self.pin = next(pinGenerator)
        surveys[self.id] = self

    def open(self):
        self.status = "Open"
        if self.timelimit is not None:
            self.deadline = datetime.now(tz.gettz("Europe/Riga")) + timedelta(seconds=self.timelimit)
            Timer(self.timelimit, self.close).start()

    def close(self):
        self.status = 'Closed'
