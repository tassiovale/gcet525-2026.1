import ply.lex as lex

palavras_reservadas = {
    "main": "KW_MAIN",
    "if": "KW_IF",
    "else": "KW_ELSE",
    "while": "KW_WHILE",
    "print": "KW_PRINT",
    "read": "KW_READ",
    "int": "KW_INT",
    "bool": "KW_BOOL",
    "true": "LIT_TRUE",
    "false": "LIT_FALSE",
}

tokens = ["TK_ID", "INT_LIT", "OP_OR", "OP_AND", "OP_NOT", "OP_EQ", "OP_NE", "OP_GE", "OP_LE", "OP_GT", "OP_LT", "OP_ASSIGN", "OP_PLUS", "OP_MINUS", "OP_MULT", "OP_DIV", 
          "LBRACE", "RBRACE", "LPAREN", "RPAREN", "SEMICOLON", "COMMA"] + list(palavras_reservadas.values())

## regex
t_OP_OR = r'\|\|'
t_OP_AND = r"&&"
t_OP_EQ  = r"=="
t_OP_NE  = r"!="
t_OP_GE  = r">="
t_OP_LE  = r"<="
t_OP_GT  = r">"
t_OP_LT  = r"<"
t_OP_ASSIGN = r"="
t_OP_PLUS   = r"\+"
t_OP_MINUS  = r"-"
t_OP_MULT   = r"\*"
t_OP_DIV    = r"/"
t_OP_NOT    = r"!"

t_LBRACE = r"\{"
t_RBRACE = r"\}"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_SEMICOLON = r";"
t_COMMA = r","
t_ignore = " \t\r"

def t_COMMENT(t):
    r"//[^\n]*"
    pass

## literal
def t_INT_LIT(t):
    r'[+-]?[0-9]+'
    t.value = int(t.value)
    return t

## identificador
def t_TK_ID(t):
    r'[a-z][a-z0-9]*'
    t.type = palavras_reservadas.get(t.value, 'TK_ID')
    return t

def t_newline(t):
    r"\n+"
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

def build_lexer(**kwargs):
    import sys
    kwargs.setdefault("debug", False)
    kwargs.setdefault("optimize", False)
    return lex.lex(module=sys.modules[__name__], **kwargs)