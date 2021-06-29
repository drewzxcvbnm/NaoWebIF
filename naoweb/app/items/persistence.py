
def getIdGenerator():
    id = 1
    while True:
        yield (id := id+1)


presentations = {}

idGenerator = getIdGenerator()