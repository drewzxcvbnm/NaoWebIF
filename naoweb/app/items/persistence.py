import random, string

pins = set()
presentations = {}
surveys = {}
surveyQuestions = {}


def get_id_generator():
    id = 1
    while True:
        yield (id := id + 1)


def get_pin_generator():
    while True:
        pin = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
        if pin in pins:
            continue
        yield pin


idGenerator = get_id_generator()
pinGenerator = get_pin_generator()
