import random, string

pins = set()
presentations = {}
surveys = {}


def get_id_generator():
    id = 1
    while True:
        yield (id := id + 1)


def get_pin_generator():
    pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    while pin in pins:
        pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    yield pin


idGenerator = get_id_generator()
pinGenerator = get_pin_generator()
