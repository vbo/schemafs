import re

from .. import schema
from ._base import BaseParser, ParseError
from ._table import CreateTableParser
from ._function import CreateFunctionParser


def parse_dump(dump):
    if not isinstance(dump, str):
        dump = dump.read()
    struct = schema.create_template()
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
            p = CreateTableParser(dump, position, length)
            parsed = p.parse()
            struct["tables"][parsed["name"]] = parsed
            end = p.pos
        elif re.match(r"^CREATE\s+(OR\s+REPLACE\s+)?FUNCTION", line, re.IGNORECASE):
            p = CreateFunctionParser(dump, position, length)
            parsed = p.parse()
            struct["functions"][parsed["name"]] = parsed
            end = p.pos
        else:
            #print line
            pass
        position = end + 1
    return struct
