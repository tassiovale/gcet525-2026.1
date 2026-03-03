from parser import parse_source
from semantic.symbol_stack import SymbolTableStack
from semantic.type_checker import TypeChecker

source = """
main {
  int a = 3;
  bool b;
  if (a > 0) {
    b = true;
  }
}
"""

ast = parse_source(source)

symtab = SymbolTableStack()
checker = TypeChecker(symtab)

checker.visit(ast)

print("Programa semanticamente válido!")