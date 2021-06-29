from app.items.item import  Item


class Presentation(Item):

    def __init__(self, name):
        super().__init__()
        self.name = name
