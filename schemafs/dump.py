from subprocess import Popen, PIPE, STDOUT
import re


def dump(server, db, args=None):
    if not args:
        args = []
    p = Popen(" ".join(
        ['pg_dump', '-s'] + args +
        ['-h', server, db]
    ), stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True, shell=True)
    sql = p.stdout
    return sql


def parse(dump):
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
                lines = []
                delimiter = None
                while True:
                    lines.append(line)
                    in_body = re.search(r'as\s+(\$[^$]*\$|\')', line, re.IGNORECASE)
                    if in_body:
                        delimiter = in_body.group(1)
                        delimiter_start = in_body.end(1)
                        while True:
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
                                raise ArgumentError()
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
