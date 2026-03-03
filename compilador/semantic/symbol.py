class Symbol:
    def __init__(self, nome, tipo, linha):
        self.nome = nome
        self.tipo = tipo
        self.linha = linha

    def __repr__(self):
        return f"{self.nome}:{self.tipo} (linha {self.linha})"