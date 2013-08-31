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
        at = self.stmt[self.pos]
        is_quoted = at == "'"
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
        is_dollar = at == "$"
        if is_dollar:
            start = self.pos
            self.pos += 1
            tag = self.stmt[self.pos:self.stmt.find("$")]
            self.pos += len(tag)
            self.expect("$")
            end_quote = "$" + tag + "$"
            while not self.expect_optional(end_quote):
                self.pos += 1
            result = self.stmt[start:self.pos].strip()
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


