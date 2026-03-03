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
            raise Exception("Nenhum escopo ativo")
        symbol = Symbol(nome, tipo, linha)
        self.stack[-1].add(symbol)

    def lookup(self, nome):
        for table in reversed(self.stack):
            symbol = table.lookup(nome)
            if symbol:
                return symbol
        raise Exception(f"Erro: '{nome}' não declarado")

    def print_stack(self):
        print("\n--- PILHA DE ESCOPOS ---")
        for table in reversed(self.stack):
            print(table)
        print("------------------------")