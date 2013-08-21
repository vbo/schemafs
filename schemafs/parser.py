import re


class ParseError(Exception):
    pass


class BaseParser(object):

    def __init__(self, stmt):
        self.stmt = stmt
        self.pos = 0
        self.len = len(self.stmt)
        self.skip_whitespace()

    def skip_whitespace(self):
        i = self.pos
        while i < self.len:
            if not self.stmt[i].isspace():
                break
            i += 1
        self.pos = i

    def expect(self, words, optional=False):
        if not isinstance(words, basestring):
            for word in words:
                r = self.expect(word, optional)
                if not r:
                    return r
                self.skip_whitespace()
            return True
        here = self.its_here(words)
        if here != -1:
            self.pos = here
            self.skip_whitespace()
            return True
        if optional:
            return False
        raise ParseError()

    def expect_optional(self, words):
        return self.expect(words, optional=True)

    def parse_ident(self):
        ident = self.parse_ident_part()
        if self.stmt[self.pos] == '.':
            self.pos += 1
            ident += '.' + self.parse_ident_part()
        self.skip_whitespace()
        return ident

    def parse_ident_part(self):
        is_quoted = self.stmt[self.pos] == '"'
        if is_quoted:
            after_quote = self.stmt.find('"', self.pos + 1) + 1
            result = self.stmt[self.pos:after_quote]
            self.pos = after_quote
            return result
        end = self.pos
        while end < self.len:
            at = self.stmt[end]
            if at.isspace() or at in ',)(;.':
                break
            end += 1
        result = self.stmt[self.pos:end].lower()
        self.pos = end
        return result

    def get_expression(self):
        braces = 0
        in_quote = False
        end = self.pos
        while end < self.len:
            at = self.stmt[end]
            # todo: rewrite it so not "in_quote" if on the top
            if at == '(' and not in_quote:
                braces += 1
            elif at == ')' and not in_quote:
                if not braces:
                    break
                braces -= 1
            elif at == "'":
                in_quote = not in_quote
            elif at == ',' and not in_quote and not braces:
                break
            elif at == ';' and not braces and not in_quote:
                break
            end += 1
        if self.pos == end:
            raise ParseError("Empty expression")
        result = self.stmt[self.pos:end].strip()
        self.pos = end
        return result

    def get_string(self):
        is_quoted = self.stmt[self.pos] == "'"
        if is_quoted:
            escape = False
            end = self.pos + 1
            while end < self.len:
                at = self.stmt[end]
                if at == '\\':
                    escape = not escape
                elif not escape and at == "'":
                    next = end + 1
                    if next < self.len and self.stmt[next] == "'":
                        end = next
                    else:
                        break
                end += 1
            result = self.stmt[self.pos:end + 1]
            self.pos = end + 1
            self.skip_whitespace()
            return result
        end = self.pos
        while end < self.len:
            at = self.stmt[end]
            if at.isspace() or at in ',);':
                break
            end += 1
        if self.pos == end:
            raise ParseError("Empty unquoted string")
        result = self.stmt[self.pos:end]
        self.pos = end
        self.skip_whitespace()
        return result

    def its_here(self, word):
        end = self.pos + len(word)
        if end > self.len or self.stmt[self.pos:end].lower() != word.lower():
            return -1
        if end == self.len:
            return end
        bound = self.stmt[end]
        if bound.isspace() or bound in ';),[':
            return end
        if word in '(,[]':
            return end


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
            "definition": definition,
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
