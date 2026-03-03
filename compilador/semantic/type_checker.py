from parser import (
    Program, Block, VarDecl, Assignment, IfStmt, WhileStmt,
    PrintStmt, ReadStmt, BinaryOp, UnaryOp, Identifier, Literal
)

class TypeChecker:
    def __init__(self, symtab):
        self.symtab = symtab

    # -------- Dispatcher --------
    def visit(self, node):
        method = "visit_" + node.__class__.__name__
        return getattr(self, method)(node)

    # -------- Estrutura --------
    def visit_Program(self, node: Program):
        self.symtab.push_scope("global")
        self.visit(node.block)
        self.symtab.pop_scope()

    def visit_Block(self, node: Block):
        self.symtab.push_scope("block")
        for cmd in node.commands:
            self.visit(cmd)
        self.symtab.pop_scope()

    # -------- Comandos --------
    def visit_VarDecl(self, node: VarDecl):
        if node.initializer is not None:
            init_type = self.visit(node.initializer)
            if init_type != node.var_type:
                raise Exception(
                    f"Erro: tipo incompatível na inicialização de '{node.name.name}'. "
                    f"Esperado {node.var_type}, obtido {init_type}."
                )
        # linha não está disponível nos nós da AST
        self.symtab.add_symbol(node.name.name, node.var_type, 0)

    def visit_Assignment(self, node: Assignment):
        symbol = self.symtab.lookup(node.target.name)
        value_type = self.visit(node.value)
        if symbol.tipo != value_type:
            raise Exception(
                f"Erro: atribuição incompatível para '{node.target.name}'. "
                f"Esperado {symbol.tipo}, obtido {value_type}."
            )

    def visit_IfStmt(self, node: IfStmt):
        cond_type = self.visit(node.condition)
        if cond_type != "bool":
            raise Exception(
                f"Erro: condição do if deve ser bool, obtido {cond_type}."
            )
        self.visit(node.then_block)
        if node.else_block is not None:
            self.visit(node.else_block)

    def visit_WhileStmt(self, node: WhileStmt):
        cond_type = self.visit(node.condition)
        if cond_type != "bool":
            raise Exception(
                f"Erro: condição do while deve ser bool, obtido {cond_type}."
            )
        self.visit(node.body)

    def visit_PrintStmt(self, node: PrintStmt):
        for arg in node.arguments:
            self.visit(arg)

    def visit_ReadStmt(self, node: ReadStmt):
        # Apenas garante que a variável foi declarada.
        self.symtab.lookup(node.target.name)

    # -------- Expressões --------
    def visit_BinaryOp(self, node: BinaryOp):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if node.operator in {"+", "-", "*", "/"}:
            if left_type != "int" or right_type != "int":
                raise Exception(
                    f"Erro: operação aritmética requer int, obtido {left_type} e {right_type}."
                )
            return "int"

        if node.operator in {"&&", "||"}:
            if left_type != "bool" or right_type != "bool":
                raise Exception(
                    f"Erro: operação lógica requer bool, obtido {left_type} e {right_type}."
                )
            return "bool"

        if node.operator in {">", ">=", "<", "<="}:
            if left_type != "int" or right_type != "int":
                raise Exception(
                    f"Erro: operação relacional requer int, obtido {left_type} e {right_type}."
                )
            return "bool"

        if node.operator in {"==", "!="}:
            if left_type != right_type:
                raise Exception(
                    f"Erro: comparação requer tipos iguais, obtido {left_type} e {right_type}."
                )
            return "bool"

        raise Exception(f"Erro: operador binário desconhecido {node.operator}.")

    def visit_UnaryOp(self, node: UnaryOp):
        operand_type = self.visit(node.operand)
        if node.operator == "!":
            if operand_type != "bool":
                raise Exception(
                    f"Erro: operador '!' requer bool, obtido {operand_type}."
                )
            return "bool"
        raise Exception(f"Erro: operador unário desconhecido {node.operator}.")

    def visit_Identifier(self, node: Identifier):
        symbol = self.symtab.lookup(node.name)
        return symbol.tipo

    def visit_Literal(self, node: Literal):
        return node.kind
