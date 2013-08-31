from subprocess import Popen, PIPE, STDOUT
import re


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
        cmd = 'ssh %s "pg_dump -s -U postgres %s | bzip2" | bunzip2' % (user + "@" + server, db)
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
        "changed": set(filter(lambda x: left[x] != right[x], common_keyset))
    }


def parse_dump(dump):
    struct = create_template()
    if isinstance(dump, str):
        dump = iter(dump.splitlines(True))
    while True:
        try:
            line = dump.next()
            if line.startswith('CREATE TABLE'):
                matches = re.search(r'table\s+"?(\w+)"?', line, re.IGNORECASE)
                if not matches:
                    raise SyntaxError("Create table statement must contain table name")
                table = matches.group(1).lower()
                lines = []
                while True:
                    lines.append(line)
                    # todo: parse definition body (columns etc)
                    if line.rstrip().endswith(';'):
                        # todo: what about EOF?
                        struct["tables"][table] = "".join(lines)
                        break
                    line = dump.next()
            elif line.startswith('CREATE FUNCTION'):
                matches = re.search(r'function\s+"?([\w]+)"?\s*\(', line, re.IGNORECASE)
                if not matches:
                    raise SyntaxError("Create function statement must contain function name and args")
                function = matches.group(1).lower()
                lines = []
                while True:
                    lines.append(line)
                    # todo: parse argument types
                    in_body = re.search(r'as\s+(\$[^$]*\$|\')', line, re.IGNORECASE)
                    if in_body:
                        delimiter = in_body.group(1)
                        delimiter_start = in_body.end(1)
                        while True:
                            out_body = False
                            if delimiter.startswith('$'):
                                out_body = line.find(delimiter, delimiter_start) != -1
                            elif delimiter == "'":
                                out_body_matches = re.findall(r"('+)[^']", line[delimiter_start + 1:])
                                if out_body_matches:
                                    for quotes in out_body_matches:
                                        out_body = len(quotes) % 2 > 0
                                else:
                                    out_body = False
                            else:
                                raise SyntaxError("Unknown function body delimiter: '%s'" % delimiter)
                            if not out_body:
                                line = dump.next()
                                lines.append(line)
                                delimiter_start = 0
                                continue
                            break
                    if re.search(';\s*$', line):
                        struct["functions"][function] = "".join(lines)
                        break
                    line = dump.next()
        except StopIteration:
            break
    return struct
