from __future__ import annotations

import json
from types import SimpleNamespace

from lexer import build_lexer


RELATIONAL_OPS = {"OP_EQ", "OP_NE", "OP_GT", "OP_LT", "OP_GE", "OP_LE"}


class ParserError(Exception):
    """Raised when the parser finds invalid syntax."""


class RecursiveDescentParser:
    def __init__(self, source: str):
        self.source = source
        self.lexer = build_lexer()
        self.lexer.input(source)

        self.tokens = []
        while True:
            token = self.lexer.token()
            if token is None:
                break
            self.tokens.append(token)

        eof_line = self.tokens[-1].lineno if self.tokens else 1
        self.tokens.append(SimpleNamespace(type="EOF", value=None, lineno=eof_line, lexpos=len(source)))
        self.pos = 0

    @property
    def current(self):
        return self.tokens[self.pos]

    def _advance(self):
        token = self.current
        self.pos += 1
        return token

    def _match(self, *token_types):
        if self.current.type in token_types:
            return self._advance()
        return None

    def _expect(self, token_type: str, message: str | None = None):
        if self.current.type != token_type:
            expected = message or f"Expected token {token_type}"
            self._error(expected, self.current)
        return self._advance()

    def _error(self, message: str, token=None):
        token = token or self.current
        found = "EOF" if token.type == "EOF" else f"{token.type} ({token.value!r})"
        raise ParserError(f"Line {token.lineno}: {message}. Found {found}.")

    def parse(self):
        ast = self.programa()
        self._expect("EOF", "Expected end of file")
        return ast

    # programa = "main" bloco ;
    def programa(self):
        self._expect("KW_MAIN", 'Expected "main" at program start')
        block = self.bloco()
        return {"node": "program", "block": block}

    # bloco = "{" { comando } "}" ;
    def bloco(self):
        self._expect("LBRACE", 'Expected "{" to start block')
        commands = []
        while self.current.type not in {"RBRACE", "EOF"}:
            commands.append(self.comando())
        self._expect("RBRACE", 'Expected "}" to end block')
        return {"node": "block", "commands": commands}

    # comando = comando_atribuicao | comando_if | comando_while | entrada_saida ;
    def comando(self):
        token_type = self.current.type

        if token_type in {"KW_INT", "KW_BOOL", "TK_ID"}:
            return self.comando_atribuicao()
        if token_type == "KW_IF":
            return self.comando_if()
        if token_type == "KW_WHILE":
            return self.comando_while()
        if token_type in {"KW_READ", "KW_PRINT"}:
            return self.entrada_saida()

        self._error("Expected a command")

    # entrada_saida = comando_read | comando_print ;
    def entrada_saida(self):
        if self.current.type == "KW_READ":
            return self.comando_read()
        if self.current.type == "KW_PRINT":
            return self.comando_print()
        self._error('Expected "read" or "print" command')

    # comando_atribuicao =
    #   tipo variavel [ "=" expressao ] ";" | variavel "=" expressao ;
    def comando_atribuicao(self):
        if self.current.type in {"KW_INT", "KW_BOOL"}:
            var_type = self._advance().value
            variable = self.variavel()
            initializer = None
            if self._match("OP_ASSIGN"):
                initializer = self.expressao()
            self._expect("SEMICOLON", 'Expected ";" after declaration')
            return {
                "node": "declaration",
                "var_type": var_type,
                "variable": variable,
                "initializer": initializer,
            }

        variable = self.variavel()
        self._expect("OP_ASSIGN", 'Expected "=" in assignment')
        value = self.expressao()

        self._expect("SEMICOLON", 'Expected ";" after assignment')
        return {"node": "assignment", "variable": variable, "value": value}

    # tipo = "int" | "bool" ;
    # (parsed inside comando_atribuicao)

    # comando_if = "if" "(" expressao ")" bloco [ "else" bloco ] ;
    def comando_if(self):
        self._expect("KW_IF", 'Expected "if"')
        self._expect("LPAREN", 'Expected "(" after if')
        condition = self.expressao()
        self._expect("RPAREN", 'Expected ")" after if condition')
        then_block = self.bloco()
        else_block = None
        if self._match("KW_ELSE"):
            else_block = self.bloco()
        return {
            "node": "if",
            "condition": condition,
            "then_block": then_block,
            "else_block": else_block,
        }

    # comando_while = "while" "(" expressao ")" bloco ;
    def comando_while(self):
        self._expect("KW_WHILE", 'Expected "while"')
        self._expect("LPAREN", 'Expected "(" after while')
        condition = self.expressao()
        self._expect("RPAREN", 'Expected ")" after while condition')
        body = self.bloco()
        return {"node": "while", "condition": condition, "body": body}

    # lista_expressoes = expressao { "," expressao } ;
    def lista_expressoes(self):
        expressions = [self.expressao()]
        while self._match("COMMA"):
            expressions.append(self.expressao())
        return expressions

    # comando_print = "print" "(" [ lista_expressoes ] ")" ";" ;
    def comando_print(self):
        self._expect("KW_PRINT", 'Expected "print"')
        self._expect("LPAREN", 'Expected "(" after print')
        expressions = []
        if self.current.type != "RPAREN":
            expressions = self.lista_expressoes()
        self._expect("RPAREN", 'Expected ")" after print arguments')
        self._expect("SEMICOLON", 'Expected ";" after print command')
        return {"node": "print", "expressions": expressions}

    # comando_read = "read" "(" variavel ")" ";" ;
    # Accepts comma-separated variables too, matching the grammar comment.
    def comando_read(self):
        self._expect("KW_READ", 'Expected "read"')
        self._expect("LPAREN", 'Expected "(" after read')

        variable = self.variavel()

        self._expect("RPAREN", 'Expected ")" after read arguments')
        self._expect("SEMICOLON", 'Expected ";" after read command')
        return {"node": "read", "variable": variable}

    # variavel = letra { letra | digito } ;
    # (already constrained by lexer token TK_ID)
    def variavel(self):
        token = self._expect("TK_ID", "Expected identifier")
        return {"node": "identifier", "name": token.value}

    # expressao = expressao_logica ;
    def expressao(self):
        return self.expressao_logica()

    # expressao_logica = termo_logico { "||" termo_logico } ;
    def expressao_logica(self):
        node = self.termo_logico()
        while True:
            op = self._match("OP_OR")
            if not op:
                break
            right = self.termo_logico()
            node = {"node": "binary", "operator": op.value, "left": node, "right": right}
        return node

    # termo_logico = fator_logico { "&&" fator_logico } ;
    def termo_logico(self):
        node = self.fator_logico()
        while True:
            op = self._match("OP_AND")
            if not op:
                break
            right = self.fator_logico()
            node = {"node": "binary", "operator": op.value, "left": node, "right": right}
        return node

    # fator_logico = [ "!" ] expressao_relacional ;
    def fator_logico(self):
        if self._match("OP_NOT"):
            operand = self.expressao_relacional()
            return {"node": "unary", "operator": "!", "operand": operand}
        return self.expressao_relacional()

    # expressao_relacional = expressao_primaria [ operador_relacional expressao_primaria ] ;
    def expressao_relacional(self):
        left = self.expressao_primaria()
        if self.current.type in RELATIONAL_OPS:
            op = self._advance()
            right = self.expressao_primaria()
            return {"node": "binary", "operator": op.value, "left": left, "right": right}
        return left

    # expressao_primaria = expressao_aritmetica | booleano ;
    def expressao_primaria(self):
        if self.current.type in {"LIT_TRUE", "LIT_FALSE"}:
            return self.booleano()
        return self.expressao_aritmetica()

    # expressao_aritmetica = termo_aritmetico { ("+" | "-") termo_aritmetico } ;
    def expressao_aritmetica(self):
        node = self.termo_aritmetico()
        while self.current.type in {"OP_PLUS", "OP_MINUS"}:
            op = self._advance()
            right = self.termo_aritmetico()
            node = {"node": "binary", "operator": op.value, "left": node, "right": right}
        return node

    # termo_aritmetico = fator_aritmetico { ("*" | "/") fator_aritmetico } ;
    def termo_aritmetico(self):
        node = self.fator_aritmetico()
        while self.current.type in {"OP_MULT", "OP_DIV"}:
            op = self._advance()
            right = self.fator_aritmetico()
            node = {"node": "binary", "operator": op.value, "left": node, "right": right}
        return node

    # fator_aritmetico = inteiro | variavel | "(" expressao ")" ;
    def fator_aritmetico(self):

        ## se for inteiro -> [ sinal ] sequencia_de_digitos
        sign = self._match("OP_PLUS", "OP_MINUS")
        if sign:
            integer = self._expect("INT_LIT", "Expected integer after sign")
            value = integer.value if sign.type == "OP_PLUS" else -integer.value
            return {"node": "int_literal", "value": value}

        if self.current.type == "INT_LIT":
            token = self._advance()
            return {"node": "int_literal", "value": token.value}

        ## se for variavel -> letra{letra | digito}
        if self.current.type == "TK_ID":
            return self.variavel()

        if self._match("LPAREN"):
            expr = self.expressao()
            self._expect("RPAREN", 'Expected ")" to close expression')
            return expr

        self._error("Expected integer, identifier or parenthesized expression")

    # booleano = "true" | "false" ;
    def booleano(self):
        if self._match("LIT_TRUE"):
            return {"node": "bool_literal", "value": True}
        if self._match("LIT_FALSE"):
            return {"node": "bool_literal", "value": False}
        self._error('Expected "true" or "false"')


def parse_source(source: str):
    return RecursiveDescentParser(source).parse()


if __name__ == "__main__":
    import argparse
    import sys

    cli = argparse.ArgumentParser(description="Recursive descent parser for the toy language.")
    cli.add_argument("input_file", nargs="?", help="Source file. If omitted, reads stdin.")
    args = cli.parse_args()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    else:
        source_code = sys.stdin.read()

    try:
        ast = parse_source(source_code)
    except ParserError as exc:
        print(f"Syntax error: {exc}", file=sys.stderr)
        raise SystemExit(1)

    print(json.dumps(ast, indent=2))
