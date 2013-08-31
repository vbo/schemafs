import re

from . import BaseParser, ParseError


class CreateTableParser(BaseParser):

    COLUMN_DEF_NOTNULL_RE = re.compile(r'^(.+)\s+NOT\s+NULL$', re.IGNORECASE)
    COLUMN_DEF_NULL_RE = re.compile(r'^(.+)\s+NULL$', re.IGNORECASE)
    COLUMN_DEF_DEFAULT_RE = re.compile(r'^(.+)\s+DEFAULT\s+(.+)$', re.IGNORECASE)

    def __init__(self, stmt):
        super(CreateTableParser, self).__init__(stmt)
        self.parsed = {
            "name": None,
            "constrains": {},
            "columns": [],
            "with": None,
            "tablespace": None,
            "inherits": []
        }

    def parse(self):
        self.expect(["CREATE", "TABLE"])
        self.expect_optional(["IF", "NOT", "EXISTS"])
        table_name = self.parse_ident()
        # todo: canonical table name
        # todo: work with schema
        self.parsed["name"] = table_name
        self.expect("(")
        while not self.expect_optional(")"):
            if self.expect_optional("CONSTRAINT"):
                self.parse_constrain()
            else:
                self.parse_column()
            if self.expect_optional(")"):
                break
            else:
                self.expect(",")
        while not self.expect_optional(";"):
            if self.expect_optional("INHERITS"):
                self.parse_inherits()
            elif self.expect_optional("WITHOUT"):
                self.expect("OIDS")
                self.parsed["with"] = "OIDS=false"
            elif self.expect_optional("WITH"):
                # todo: I think storage_parameter may be in braces
                if self.expect_optional("OIDS") or self.expect_optional("OIDS=true"):
                    self.parsed["with"] = "OIDS=true"
                elif self.expect_optional("OIDS=false"):
                    self.parsed["with"] = "OIDS=false"
                else:
                    self.parsed["with"] = self.get_expression()
            elif self.expect_optional("TABLESPACE"):
                self.parsed["tablespace"] = self.get_string()
            else:
                raise ParseError("Unsupported command")
        return self.parsed

    def parse_constrain(self):
        name = self.parse_ident()
        definition = self.get_expression()
        self.parsed["constrains"][name] = definition

    def parse_column(self):
        name = self.parse_ident()
        definition = self.get_expression()
        column = {
            "name": name,
            "nullable": True,
            "default": None,
            "type": None
        }
        matched = self.COLUMN_DEF_NOTNULL_RE.match(definition)
        if matched:
            definition = matched.group(1).strip()
            column["nullable"] = False
        else:
            matched = self.COLUMN_DEF_NULL_RE.match(definition)
            if matched:
                definition = matched.group(1).strip()
                column["nullable"] = True
            # here the definition cleaned up from NULL-ability qualifiers
        matched = self.COLUMN_DEF_DEFAULT_RE.match(definition)
        if matched:
            definition = matched.group(1).strip()
            column["default"] = matched.group(2).strip()
            # now, it cleaned up from DEFAULT descriptor too
        column["type"] = definition
        self.parsed["columns"].append(column)

    def parse_inherits(self):
        self.expect('(')
        while not self.expect_optional(')'):
            self.parsed["inherits"].append(self.parse_ident())
            if self.expect_optional(')'):
                break
            self.expect(',')
