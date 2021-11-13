from state import State
from expression import *
from variables import *

class Statement:
	NULL = 0
	EXPR = 1
	LET = 2
	PRINT = 3
	WHILE = 4
	FOR = 5
	RETURN = 6
	FUNCDECL = 7

	def interpret(self):
		pass

	def __init__(self, type, args=[]):
		self.type = type
		self.args = args

	def __repr__(self):
		return f'({self.type} {str(self.args)});'


class ExpressionStatement(Statement):
	def interpret(self):
		self.expression.evaluate()

	def __init__(self, expression):
		self.type = Statement.EXPR
		self.expression = expression

	def __repr__(self):
		return f'(EXPR {str(self.expression)});'


class LetStatement(Statement):
	def interpret(self):
		State.get_state().register(
			self.name, self.expression.evaluate() if self.expression else TrogonNull)

	def __init__(self, name, expression=None):
		self.type = Statement.LET
		self.name = name
		self.expression = expression

	def __repr__(self):
		return f'(LET {self.name} {self.expression})'


# TODO: rn it works different from any other language
# and is just a way to return from a block early
# but it's not very practical, because if you try to return with a condition
# you just return from an if-statement branch block
class ReturnStatement(Statement):
	def interpret(self):
		pass

	def __init__(self, expression):
		self.type = Statement.RETURN
		self.expression = expression

	def __repr__(self):
		return f'(RETURN {self.expression})'


class WhileStatement(Statement):
	def interpret(self):
		while self.condition.evaluate().to(TrogonBool).value == True:
			self.block.evaluate()

	def __init__(self, condition, block):
		self.type = Statement.WHILE
		self.condition = condition
		self.block = block

	def __repr__(self):
		return f'(WHILE {self.condition} {self.block}'


class ForStatement(Statement):
	def interpret(self):
		state = State.begin()

		if self.has_let:
			state.register(self.lvalue.name, self.left_bound.evaluate())
		else:
			state.set(self.lvalue.name, self.left_bound.evaluate())

		counter = state.get(self.lvalue.name)
		while abs(counter.sub(self.right_bound.evaluate()).value) >= 1:
			state.set(self.lvalue.name, counter)

			self.block.evaluate()

			counter.value += (1 if self.right_bound.evaluate().greater(counter) else -1)

		state.end()

	def __init__(self, lvalue, left_bound, right_bound, block, has_let=False):
		self.type = Statement.FOR
		self.lvalue = lvalue
		self.left_bound = left_bound
		self.right_bound = right_bound
		self.block = block
		self.has_let = has_let

	def __repr__(self):
		return f'(FOR {self.lvalue.name}:={self.left_bound} to {self.right_bound} {self.block})'


class FunctionDeclarationStatement(Statement):
	def interpret(self):
		state = State.get_state()
		state.register(self.expression.name, self.expression.evaluate())

	def __init__(self, expression):
		self.type = Statement.FUNCDECL
		self.expression = expression

	def __repr__(self):
		return f'(DEFSTMT {self.expression})'