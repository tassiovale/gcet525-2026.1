from __future__ import annotations

import json
from types import SimpleNamespace

from lexer import build_lexer


RELATIONAL_OPS = {"OP_EQ", "OP_NE", "OP_GT", "OP_LT", "OP_GE", "OP_LE"}


# =============================================================================
#  Nós da AST
#  Cada classe representa um tipo de nó definido no design:
#
#  Program / Block / VarDecl / Assignment / IfStmt / WhileStmt /
#  PrintStmt / ReadStmt / BinaryOp / UnaryOp / Identifier / Literal
# =============================================================================

class ASTNode:
    """Base para todos os nós da AST."""
    def to_dict(self):
        raise NotImplementedError

    def __repr__(self):
        return json.dumps(self.to_dict(), indent=2)


# ── Estrutura do programa ────────────────────────────────────────────────────

class Program(ASTNode):
    """Raiz da árvore: Program └── Block"""
    def __init__(self, block: "Block"):
        self.block = block

    def to_dict(self):
        return {"node": "Program", "block": self.block.to_dict()}


class Block(ASTNode):
    """Sequência de comandos entre { }"""
    def __init__(self, commands: list):
        self.commands = commands

    def to_dict(self):
        return {"node": "Block", "commands": [c.to_dict() for c in self.commands]}


# ── Comandos ─────────────────────────────────────────────────────────────────

class VarDecl(ASTNode):
    """Declaração: tipo nome [= expr] ;
       VarDecl ├── Type: (KW_INT | KW_BOOL)  └── Name: TK_ID"""
    def __init__(self, var_type: str, name: "Identifier", initializer=None):
        self.var_type    = var_type
        self.name        = name
        self.initializer = initializer

    def to_dict(self):
        d = {"node": "VarDecl", "type": self.var_type, "name": self.name.to_dict()}
        if self.initializer is not None:
            d["initializer"] = self.initializer.to_dict()
        return d


class Assignment(ASTNode):
    """Atribuição: target = value ;
       Assignment ├── Target: TK_ID  └── Value: [Expression]"""
    def __init__(self, target: "Identifier", value: ASTNode):
        self.target = target
        self.value  = value

    def to_dict(self):
        return {
            "node":   "Assignment",
            "target": self.target.to_dict(),
            "value":  self.value.to_dict(),
        }


class IfStmt(ASTNode):
    """if (cond) then_block [else else_block]
       IfStmt ├── Condition  ├── Then: Block  └── Else: Block (opcional)"""
    def __init__(self, condition: ASTNode, then_block: Block, else_block=None):
        self.condition  = condition
        self.then_block = then_block
        self.else_block = else_block

    def to_dict(self):
        d = {
            "node":       "IfStmt",
            "condition":  self.condition.to_dict(),
            "then_block": self.then_block.to_dict(),
        }
        if self.else_block is not None:
            d["else_block"] = self.else_block.to_dict()
        return d


class WhileStmt(ASTNode):
    """while (cond) body
       WhileStmt ├── Condition  └── Body: Block"""
    def __init__(self, condition: ASTNode, body: Block):
        self.condition = condition
        self.body      = body

    def to_dict(self):
        return {
            "node":      "WhileStmt",
            "condition": self.condition.to_dict(),
            "body":      self.body.to_dict(),
        }


class PrintStmt(ASTNode):
    """print(expr, ...) ;
       PrintStmt └── Arguments: [[Expression]]"""
    def __init__(self, arguments: list):
        self.arguments = arguments

    def to_dict(self):
        return {
            "node":      "PrintStmt",
            "arguments": [a.to_dict() for a in self.arguments],
        }


class ReadStmt(ASTNode):
    """read(variavel) ;
       ReadStmt └── Target: TK_ID"""
    def __init__(self, target: "Identifier"):
        self.target = target

    def to_dict(self):
        return {"node": "ReadStmt", "target": self.target.to_dict()}


# ── Expressões ───────────────────────────────────────────────────────────────

class BinaryOp(ASTNode):
    """Operação binária: left op right
       BinaryOp ├── operator  ├── left  └── right"""
    def __init__(self, operator: str, left: ASTNode, right: ASTNode):
        self.operator = operator
        self.left     = left
        self.right    = right

    def to_dict(self):
        return {
            "node":     "BinaryOp",
            "operator": self.operator,
            "left":     self.left.to_dict(),
            "right":    self.right.to_dict(),
        }


class UnaryOp(ASTNode):
    """Operação unária: op operand
       UnaryOp ├── operator  └── operand"""
    def __init__(self, operator: str, operand: ASTNode):
        self.operator = operator
        self.operand  = operand

    def to_dict(self):
        return {
            "node":     "UnaryOp",
            "operator": self.operator,
            "operand":  self.operand.to_dict(),
        }


class Identifier(ASTNode):
    """Referência a variável: TK_ID"""
    def __init__(self, name: str):
        self.name = name

    def to_dict(self):
        return {"node": "Identifier", "name": self.name}


class Literal(ASTNode):
    """Literal: INT_LIT | LIT_TRUE | LIT_FALSE"""
    def __init__(self, kind: str, value):
        self.kind  = kind   # "int" | "bool"
        self.value = value

    def to_dict(self):
        return {"node": "Literal", "kind": self.kind, "value": self.value}


# =============================================================================
#  Parser
# =============================================================================

class RecursiveDescentParser:
    def __init__(self, source: str):
        self.source = source
        self.lexer  = build_lexer()
        self.lexer.input(source)

        self.tokens = []
        while True:
            token = self.lexer.token()
            if token is None:
                break
            self.tokens.append(token)

        eof_line = self.tokens[-1].lineno if self.tokens else 1
        self.tokens.append(
            SimpleNamespace(type="EOF", value=None, lineno=eof_line, lexpos=len(source))
        )
        self.pos = 0

    # ── helpers ──────────────────────────────────────────────────────────────

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
        print(f"Line {token.lineno}: {message}. Found {found}.")
        exit(1)

    # ── ponto de entrada ─────────────────────────────────────────────────────

    def parse(self) -> Program:
        ast = self.programa()
        self._expect("EOF", "Expected end of file")
        return ast

    # ── regras gramaticais ────────────────────────────────────────────────────

    # programa = "main" bloco ;
    def programa(self) -> Program:
        self._expect("KW_MAIN", 'Expected "main" at program start')
        block = self.bloco()
        return Program(block)

    # bloco = "{" { comando } "}" ;
    def bloco(self) -> Block:
        self._expect("LBRACE", 'Expected "{" to start block')
        commands = []
        while self.current.type not in {"RBRACE", "EOF"}:
            commands.append(self.comando())
        self._expect("RBRACE", 'Expected "}" to end block')
        return Block(commands)

    # comando = comando_atribuicao | comando_if | comando_while | entrada_saida ;
    def comando(self) -> ASTNode:
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
    def entrada_saida(self) -> ASTNode:
        if self.current.type == "KW_READ":
            return self.comando_read()
        if self.current.type == "KW_PRINT":
            return self.comando_print()
        self._error('Expected "read" or "print" command')

    # comando_atribuicao =
    #   tipo variavel [ "=" expressao ] ";" | variavel "=" expressao ";" ;
    def comando_atribuicao(self) -> ASTNode:
        # Declaração com tipo
        if self.current.type in {"KW_INT", "KW_BOOL"}:
            var_type    = self._advance().value          # "int" ou "bool"
            name_node   = self.variavel()                # Identifier
            initializer = None
            if self._match("OP_ASSIGN"):
                initializer = self.expressao()
            self._expect("SEMICOLON", 'Expected ";" after declaration')
            return VarDecl(var_type, name_node, initializer)

        # Atribuição simples
        target = self.variavel()                         # Identifier
        self._expect("OP_ASSIGN", 'Expected "=" in assignment')
        value = self.expressao()
        self._expect("SEMICOLON", 'Expected ";" after assignment')
        return Assignment(target, value)

    # comando_if = "if" "(" expressao ")" bloco [ "else" bloco ] ;
    def comando_if(self) -> IfStmt:
        self._expect("KW_IF",   'Expected "if"')
        self._expect("LPAREN",  'Expected "(" after if')
        condition = self.expressao()
        self._expect("RPAREN",  'Expected ")" after if condition')
        then_block = self.bloco()
        else_block = None
        if self._match("KW_ELSE"):
            else_block = self.bloco()
        return IfStmt(condition, then_block, else_block)

    # comando_while = "while" "(" expressao ")" bloco ;
    def comando_while(self) -> WhileStmt:
        self._expect("KW_WHILE", 'Expected "while"')
        self._expect("LPAREN",   'Expected "(" after while')
        condition = self.expressao()
        self._expect("RPAREN",   'Expected ")" after while condition')
        body = self.bloco()
        return WhileStmt(condition, body)

    # lista_expressoes = expressao { "," expressao } ;
    def lista_expressoes(self) -> list:
        expressions = [self.expressao()]
        while self._match("COMMA"):
            expressions.append(self.expressao())
        return expressions

    # comando_print = "print" "(" [ lista_expressoes ] ")" ";" ;
    def comando_print(self) -> PrintStmt:
        self._expect("KW_PRINT", 'Expected "print"')
        self._expect("LPAREN",   'Expected "(" after print')
        arguments = []
        if self.current.type != "RPAREN":
            arguments = self.lista_expressoes()
        if len(arguments) == 0:
            self._error('Expected at least one argument for "print" command')
        self._expect("RPAREN",   'Expected ")" after print arguments')
        self._expect("SEMICOLON",'Expected ";" after print command')
        return PrintStmt(arguments)

    # comando_read = "read" "(" variavel ")" ";" ;
    def comando_read(self) -> ReadStmt:
        self._expect("KW_READ", 'Expected "read"')
        self._expect("LPAREN",  'Expected "(" after read')
        target = self.variavel()
        self._expect("RPAREN",  'Expected ")" after read arguments')
        self._expect("SEMICOLON",'Expected ";" after read command')
        return ReadStmt(target)

    # variavel = letra { letra | digito } ;   (garantido pelo lexer como TK_ID)
    def variavel(self) -> Identifier:
        token = self._expect("TK_ID", "Expected identifier")
        return Identifier(token.value)

    # ── expressões (hierarquia de precedência) ────────────────────────────────
    #
    # expressao            → expressao_logica
    # expressao_logica     → termo_logico     { "||" termo_logico }
    # termo_logico         → fator_logico     { "&&" fator_logico }
    # fator_logico         → [ "!" ] expressao_relacional
    # expressao_relacional → expressao_primaria [ relop expressao_primaria ]
    # expressao_primaria   → expressao_aritmetica | booleano
    # expressao_aritmetica → termo_aritmetico  { ("+" | "-") termo_aritmetico }
    # termo_aritmetico     → fator_aritmetico  { ("*" | "/") fator_aritmetico }
    # fator_aritmetico     → [sinal] inteiro | variavel | "(" expressao ")"

    def expressao(self) -> ASTNode:
        return self.expressao_logica()

    # LogicalLevel — menor prioridade
    def expressao_logica(self) -> ASTNode:
        node = self.termo_logico()
        while True:
            op = self._match("OP_OR")
            if not op:
                break
            right = self.termo_logico()
            node  = BinaryOp(op.value, node, right)
        return node

    def termo_logico(self) -> ASTNode:
        node = self.fator_logico()
        while True:
            op = self._match("OP_AND")
            if not op:
                break
            right = self.fator_logico()
            node  = BinaryOp(op.value, node, right)
        return node

    # UnaryOp: !
    def fator_logico(self) -> ASTNode:
        op = self._match("OP_NOT")
        if op:
            operand = self.expressao_relacional()
            return UnaryOp("!", operand)
        return self.expressao_relacional()

    # RelationalLevel
    def expressao_relacional(self) -> ASTNode:
        left = self.expressao_primaria()
        if self.current.type in RELATIONAL_OPS:
            op    = self._advance()
            right = self.expressao_primaria()
            return BinaryOp(op.value, left, right)
        return left

    def expressao_primaria(self) -> ASTNode:
        if self.current.type in {"LIT_TRUE", "LIT_FALSE"}:
            return self.booleano()
        return self.expressao_aritmetica()

    # AdditiveLevel
    def expressao_aritmetica(self) -> ASTNode:
        node = self.termo_aritmetico()
        while self.current.type in {"OP_PLUS", "OP_MINUS"}:
            op    = self._advance()
            right = self.termo_aritmetico()
            node  = BinaryOp(op.value, node, right)
        return node

    # MultiplicativeLevel
    def termo_aritmetico(self) -> ASTNode:
        node = self.fator_aritmetico()
        while self.current.type in {"OP_MULT", "OP_DIV"}:
            op    = self._advance()
            right = self.fator_aritmetico()
            node  = BinaryOp(op.value, node, right)
        return node

    # Factor — maior prioridade
    def fator_aritmetico(self) -> ASTNode:
        # UnaryOp: sinal antes de inteiro  (ex: -5  ou  +3)
        sign = self._match("OP_PLUS", "OP_MINUS")
        if sign:
            integer = self._expect("INT_LIT", "Expected integer after sign")
            raw_val = integer.value
            value   = raw_val if sign.type == "OP_PLUS" else -raw_val
            return Literal("int", value)

        # Literal inteiro sem sinal
        if self.current.type == "INT_LIT":
            token = self._advance()
            return Literal("int", token.value)

        # Identificador (variável)
        if self.current.type == "TK_ID":
            return self.variavel()

        # Expressão entre parênteses
        if self._match("LPAREN"):
            expr = self.expressao()
            self._expect("RPAREN", 'Expected ")" to close expression')
            return expr

        self._error("Expected integer, identifier or parenthesized expression")

    # booleano = "true" | "false" ;
    def booleano(self) -> Literal:
        if self._match("LIT_TRUE"):
            return Literal("bool", True)
        if self._match("LIT_FALSE"):
            return Literal("bool", False)
        self._error('Expected "true" or "false"')


# =============================================================================
#  API pública
# =============================================================================

def parse_source(source: str) -> Program:
    return RecursiveDescentParser(source).parse()


# =============================================================================
#  CLI
# =============================================================================

if __name__ == "__main__":
    import argparse
    import sys

    cli = argparse.ArgumentParser(description="Recursive descent parser — outputs AST as JSON.")
    cli.add_argument("input_file", nargs="?", help="Source file. If omitted, reads stdin.")
    args = cli.parse_args()

    if args.input_file:
        with open(args.input_file, "r", encoding="utf-8") as f:
            source_code = f.read()
    else:
        source_code = sys.stdin.read()

    try:
        ast = parse_source(source_code)
    except Exception as exc:
        print(f"Syntax error: {exc}", file=sys.stderr)

    print(json.dumps(ast.to_dict(), indent=2))
