from . import BaseParser, ParseError


class CreateFunctionParser(BaseParser):

    MODES = ("IN", "OUT", "INOUT", "VARIADIC")

    def init(self):
        self.start = self.pos
        self.parsed = {
            "name": None,
            "arguments": [],
            "returns": None,
            "body": None,
            "attributes": "",
            "definition": None
        }

    def parse(self):
        self.expect("CREATE")
        self.expect_optional(["OR", "REPLACE"])
        self.expect("FUNCTION")
        self.parsed["name"] = self.parse_ident()
        self.expect("(")
        while not self.expect_optional(")"):
            mode = None
            for variant in self.MODES:
                if self.expect_optional(variant):
                    mode = variant
            argument = self.parse_argument()
            argument["mode"] = mode
            self.parsed["arguments"].append(argument)
            if self.expect_optional(")"):
                break
            self.expect(",")
        self.expect("RETURNS")
        # todo: it's really optional where there are some OUT/INOUT params
        start = self.pos
        end = self.pos
        while not self.expect_optional("AS"):
            self.pos += 1
            end += 1
        if start == end:
            raise ParseError("Empty RETURNS")
        self.parsed["returns"] = self.stmt[start:end].strip()
        # todo: parse attributes
        self.parsed["body"] = self.get_string()
        # todo: parse attributes carefully
        end = self.pos
        while True:
            if end == self.len or self.stmt[end] == ';':
                break
            end += 1
        self.parsed["attributes"] = self.stmt[self.pos:end]
        self.pos = end
        self.parsed["definition"] = self.stmt[self.start:self.pos + 1]
        assert self.pos == self.len or self.stmt[self.pos] == ";"
        return self.parsed

    def parse_argument(self):
        parsed = {
            "mode": None,
            "name": None,
            "type": None,
            "default": None
        }
        before_arg = self.pos
        # first assume that name is not given
        parsed["type"] = self.parse_argument_type()
        after_arg_type = self.pos
        # check that we just reached the end of definition
        # or proceed to DEFAULT qualifier
        at = self.stmt[self.pos]
        if at not in "),=" and not self.expect_optional("DEFAULT"):
            # seems that name is given
            # get back in time, parse name first and than type
            self.pos = before_arg
            parsed["name"] = self.parse_ident()
            parsed["type"] = self.parse_argument_type()
        else:
            # name is not given, we've just parsed a right type
            self.pos = after_arg_type
        if self.expect_optional("=") or self.expect_optional("DEFAULT"):
            parsed["default"] = self.get_expression()
        return parsed

    def parse_argument_type(self):
        end = self.pos
        while end < self.len:
            at = self.stmt[end]
            if at.isspace() or at in "(),":
                break
            end += 1
        if end == self.pos:
            raise ParseError("Empty function argument type")
        parsed = self.stmt[self.pos:end]
        self.pos = end
        self.skip_whitespace()
        is_time = False
        # check for more-than-one-word types
        lowered = parsed.lower()
        if lowered == "character" and self.expect_optional("varying"):
            parsed = "character varying"
        elif lowered == "double" and self.expect_optional("precision"):
            parsed = "double precision"
        elif lowered in ("timestamp", "time"):
            is_time = True
        if self.stmt[self.pos] == "(":
            parsed += self.get_expression()
        if is_time:
            tz_opts = ("with time zone", "without time zone")
            for opt in tz_opts:
                if self.expect_optional(opt.split(" ")):
                    parsed += " " + opt
                    break
        if self.expect_optional("["):
            self.expect("]")
            parsed += "[]"
        return parsed

