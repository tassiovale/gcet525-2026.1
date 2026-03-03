from compilador.semantic.symbol import Symbol

class SymbolTable:
    def __init__(self, escopo_nome):
        self.escopo_nome = escopo_nome
        self.symbols = {}

    def add(self, symbol):
        if symbol.nome in self.symbols:
            raise Exception(
                f"Erro: '{symbol.nome}' já declarado no escopo {self.escopo_nome}"
            )
        self.symbols[symbol.nome] = symbol

    def lookup(self, nome):
        return self.symbols.get(nome, None)

    def __repr__(self):
        return f"{self.escopo_nome}: {list(self.symbols.values())}"