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