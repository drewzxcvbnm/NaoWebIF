from typing import List

from app.items.item import Item

from app.items.persistence import surveys


class Survey(Item):

    def __init__(self, question: str, options: List[str]):
        super().__init__()
        self.options = options
        self.question = question
        self.status = 'Open'
        self.results = dict([(i, 0) for i in options])
        surveys[self.id] = self
