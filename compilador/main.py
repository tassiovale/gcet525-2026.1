from parser import parse_source
from semantic.symbol_stack import SymbolTableStack
from semantic.type_checker import TypeChecker

source_path = "source.txt"

with open(source_path, "r", encoding="utf-8") as f:
    source = f.read()

ast = parse_source(source)

symtab = SymbolTableStack()
checker = TypeChecker(symtab)

checker.visit(ast)

print("Programa semanticamente válido!")
