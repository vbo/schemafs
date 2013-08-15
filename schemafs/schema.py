from subprocess import Popen, PIPE, STDOUT
import re


def dump(server, user, db, args=None):
    if not args:
        args = []
    # todo: error handling
    # todo: it's much faster to use ssh ... pg_dump ... for remote connections, maybe with compression
    # like this: ssh <host> "PGPASSWORD=<pass> pg_dump -s -U postgres <db> | bzip2" | bunzip2
    cmd = " ".join(
        ['pg_dump', '-s'] + args +
        ['-h', server, '-U', user, db]
    )
    p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True)
    sql = p.stdout
    return sql


def parse_dump(dump):
    struct = {
        "tables": {},
        "functions": {}
    }
    if isinstance(dump, str):
        dump = iter(dump.splitlines(True))
    while True:
        try:
            line = dump.next()
            if line.startswith('CREATE TABLE'):
                matches = re.search(r'table\s+"?(\w+)"?', line, re.IGNORECASE)
                if matches:
                    table = matches.group(1).lower()
                else:
                    raise SyntaxError("Create table statement must contain table name")
                lines = []
                while True:
                    lines.append(line)
                    if line.rstrip().endswith(';'):
                        struct["tables"][table] = "".join(lines)
                        break
                    line = dump.next()
            elif line.startswith('CREATE FUNCTION'):
                matches = re.search(r'function\s+"?([\w]+)"?\s*\(', line, re.IGNORECASE)
                if matches:
                    function = matches.group(1).lower()
                    # todo: add argument types
                else:
                    raise SyntaxError("Create function statement must contain function name and args")
                lines = []
                while True:
                    lines.append(line)
                    in_body = re.search(r'as\s+(\$[^$]*\$|\')', line, re.IGNORECASE)
                    if in_body:
                        delimiter = in_body.group(1)
                        delimiter_start = in_body.end(1)
                        while True:
                            out_body = False
                            if delimiter.startswith('$'):
                                out_body = line.find(delimiter, delimiter_start) != -1
                            elif delimiter == "'":
                                out_body_matches = re.findall(r"('+)[^']", line[delimiter_start+1:])
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
                        try:
                            struct["functions"][function] = "".join(lines)
                        except UnboundLocalError:
                            print line
                            raise
                        break
                    line = dump.next()
        except StopIteration:
            break
    return struct
