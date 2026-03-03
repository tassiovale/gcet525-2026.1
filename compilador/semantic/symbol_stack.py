from semantic.symbol import Symbol
from semantic.symbol_table import SymbolTable

class SymbolTableStack:
    def __init__(self):
        self.stack = []

    def push_scope(self, nome):
        print(f"\n>> ENTER scope: {nome}")
        self.stack.append(SymbolTable(nome))

    def pop_scope(self):
        scope = self.stack.pop()
        print(f"<< EXIT scope: {scope.escopo_nome}")

    def add_symbol(self, nome, tipo, linha):
        if not self.stack:
            print("Nenhum escopo ativo")
            exit(1)
        symbol = Symbol(nome, tipo, linha)
        self.stack[-1].add(symbol)

    def lookup(self, nome):
        for table in reversed(self.stack):
            symbol = table.lookup(nome)
            if symbol:
                return symbol
        print(f"Erro: '{nome}' não declarado")
        exit(1)

    def print_stack(self):
        print("\n--- PILHA DE ESCOPOS ---")
        for table in reversed(self.stack):
            print(table)
        print("------------------------")