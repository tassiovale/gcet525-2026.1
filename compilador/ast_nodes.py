class Node: pass

class Var(Node):
    def __init__(self, name):
        self.name = name

class Assign(Node):
    def __init__(self, var, expr):
        self.var = var
        self.expr = expr

class BinOp(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right