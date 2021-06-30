from app.items.item import Item
from app.items.persistence import presentations


class Presentation(Item):

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.surveys = []
        presentations[self.id] = self

    def add_survey(self, s):
        self.surveys.append(s)