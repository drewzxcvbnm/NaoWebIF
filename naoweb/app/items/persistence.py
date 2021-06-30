
def get_id_generator():
    id = 1
    while True:
        yield (id := id+1)


presentations = {}
surveys = {}

idGenerator = get_id_generator()