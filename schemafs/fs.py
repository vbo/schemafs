import os.path
from glob import iglob


def from_struct(root, struct):
    for t in struct.keys():
        directory = os.path.join(root, t)
        os.mkdir(directory)
        for name, definition in struct[t].items():
            with open(os.path.join(directory, '%s.sql' % name), 'w') as fl:
                fl.write(definition)


def to_struct(root, struct):
    for t in struct.keys():
        directory = os.path.join(root, t)
        if not os.path.isdir(directory):
            continue
        for g in iglob(os.path.join(directory, "*.sql")):
            name = os.path.splitext(os.path.basename(g))[0]
            struct[t][name] = open(g).read()
    return struct
