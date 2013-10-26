from subprocess import Popen, PIPE, STDOUT
import re

from . import parser


def create_template():
    return {
        "functions": {},
        "tables": {}
    }


def dump(server, user, db, args=None):
    if not args:
        args = []
    # todo: error handling
    if server != "localhost":
        cmd = 'ssh %s "pg_dump -s -U postgres %s -h localhost | bzip2" | bunzip2' % (user + "@" + server, db)
    else:
        cmd = " ".join(
            ['pg_dump', '-s'] + args +
            ['-h', server, '-U', user, db]
        )
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True)
    sql = p.stdout
    return sql


def diff(left, right):
    result = {}
    for key in create_template():
        result[key] = _diff_dict(left.get(key, {}), right.get(key, {}))
    return result


def diff_empty(diff):
    for k, v in diff.items():
        for change, keys in v.items():
            if keys:
                return False
    return True


def _diff_dict(left, right):
    left_keyset = set(left.keys())
    right_keyset = set(right.keys())
    common_keyset = left_keyset.intersection(right_keyset)
    return {
        "added": left_keyset - common_keyset,
        "removed": right_keyset - common_keyset,
        "changed": set(filter(lambda x: left[x]["definition"] != right[x]["definition"], common_keyset))
    }


def parse_dump(dump):
    if not isinstance(dump, str):
        dump = dump.read()
    struct = create_template()
    position = 0
    length = len(dump)
    while position < length:
        end = dump.find("\n", position)
        if end == -1:
            end = length
        line = dump[position:end].strip()
        if not line:
            pass
        elif re.match(r"^CREATE\s+TABLE", line, re.IGNORECASE):
            p = parser.CreateTableParser(dump, position, length)
            parsed = p.parse()
            struct["tables"][parsed["name"]] = parsed
            end = p.pos
        elif re.match(r"^CREATE\s+(OR\s+REPLACE\s+)?FUNCTION", line, re.IGNORECASE):
            p = parser.CreateFunctionParser(dump, position, length)
            parsed = p.parse()
            struct["functions"][parsed["name"]] = parsed
            end = p.pos
        else:
            #print line
            pass
        position = end + 1
    return struct
