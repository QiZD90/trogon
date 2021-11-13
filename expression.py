from state import State
from lexer import Token
from runtime import RuntimeException
from variables import *

class Expression:
	LITERAL = 0
	LVALUE = 1
	UNARY = 2
	BINARY = 3
	LOGICAL = 4
	BLOCK = 5
	IF = 6
	CALL = 7
	SUBSCRIPTION = 8
	CAST = 9

	def evaluate(self):
		return None

	def __init__(self, type, value=None, children=[]):
		self.type = type
		self.value = value
		self.children = children

	def __repr__(self):
		return f'({self.type} {self.value} {self.children})'


class LiteralExpression(Expression):
	def evaluate(self):
		return self.value

	def __init__(self, value):
		self.type = Expression.LITERAL

		if isinstance(value, str):
			self.value = TrogonString(value)
		elif isinstance(value, int) or isinstance(value, float):
			self.value = TrogonNumber(value)
		elif isinstance(value, bool):
			self.value = TrogonBool(value)
		elif isinstance(value, TrogonType):
			self.value = TrogonType(value.value)
		else:
			self.value = TrogonNull

	def __repr__(self):
		return f'(LIT {str(self.value)})'


class LvalueExpression(Expression):
	def evaluate(self):
		return TrogonNull

	def assign(self, value):
		return TrogonNull

	def __init__(self, value):
		self.type = Expression.LVALUE
		self.value = value

	def __repr__(self):
		return f'(GENERIC LVALUE {self.value})'


class VariableExpression(LvalueExpression):
	def evaluate(self):
		return State.get_state().get(self.name)

	def assign(self, value):
		State.get_state().set(self.name, value)
		return State.get_state().get(self.name)

	def __init__(self, name):
		self.type = Expression.LVALUE
		self.name = name

	def __repr__(self):
		return f'(VAR {self.name})'


class DotExpression(LvalueExpression):
	def evaluate(self):
		return self.left.evaluate().dot(self.right.evaluate())

	def assign(self, value):
		# TODO:
		raise RuntimeException('Assignment to a dot expression is not implemented')

	def __init__(self, left, right):
		self.type = Expression.LVALUE
		self.left = left
		self.right = right

	def __repr__(self):
		return f'(DOT {self.left} {self.right})'


class SubscriptionExpression(LvalueExpression):
	def evaluate(self):
		return self.expression.evaluate().subscript(self.index.evaluate())

	def assign(self, value):
		return self.expression.evaluate().subscript_assign(
			self.index.evaluate(), value)

	def __init__(self, expression, index):
		self.type = Expression.LVALUE
		self.expression = expression
		self.index = index

	def __repr__(self):
		return f'(SUBSCR {self.expression} {self.index})'


class CastExpression(Expression):
	def evaluate(self):
		return self.left.evaluate().to(self.right.evaluate().value)

	def __init__(self, left, right):
		self.type = Expression.CAST
		self.left = left
		self.right = right

	def __repr__(self):
		return f'(CAST {self.left} {self.right})'


class CallExpression(Expression):
	def evaluate(self):
		return self.expression.evaluate().call(self.arguments)

	def __init__(self, expression, arguments=[]):
		self.type = Expression.CALL
		self.expression = expression
		self.arguments = arguments

	def __repr__(self):
		return f'(CALL {self.expression} {self.arguments})'


class UnaryExpression(Expression):
	functions = {
		Token.MINUS: lambda x: x.evaluate().unary_minus()
	}

	def evaluate(self):
		return UnaryExpression.functions[self.operator](self.operand)

	def __init__(self, operator, operand):
		self.type = Expression.UNARY
		self.operator = operator
		self.operand = operand

	def __repr__(self):
		return f'({self.operator} {self.operand})'


class BinaryExpression(Expression):
	def assign(f):
		def inner(x, y):
			if x.type not in (Expression.LVALUE, Expression.SUBSCRIPTION):
				raise RuntimeException('Expected lvalue!')

			return x.assign(f(x, y) if f else y)

		return inner

	functions = {
		Token.PLUS: lambda x, y: x.add(y),
		Token.MINUS: lambda x, y: x.sub(y),
		Token.STAR: lambda x, y: x.mul(y),
		Token.SLASH: lambda x, y: x.divide(y),
		Token.DOUBLE_SLASH: lambda x, y: x.div(y),
		Token.PERCENT: lambda x, y: x.mod(y),
		Token.SHL: lambda x, y: x.shl(y),
		Token.SHR: lambda x, y: x.shr(y),

		Token.EQUAL: assign(None),
		Token.PLUS_EQUAL: assign(lambda x, y: x.add(y)),
		Token.MINUS_EQUAL: assign(lambda x, y: x.sub(y)),
		Token.STAR_EQUAL: assign(lambda x, y: x.mul(y)),
		Token.SLASH_EQUAL: assign(lambda x, y: x.divide(y)),
		Token.DOUBLE_SLASH_EQUAL: assign(lambda x, y: x.div(y)),
		Token.PERCENT_EQUAL: assign(lambda x, y: x.mod(y)),
		Token.SHL_EQUAL: assign(lambda x, y: x.shl(y)),
		Token.SHR_EQUAL: assign(lambda x, y: x.shr(y)),

		Token.EQUAL_EQUAL: lambda x, y: x.equal(y),
		Token.BANG_EQUAL: lambda x, y: not x.equal(y),

		Token.GREATER: lambda x, y: x.greater(y),
		Token.LESS: lambda x, y: x.less(y),
		Token.GREATER_EQUAL: 
			lambda x, y: x.equal(y) or x.greater(y),
		Token.LESS_EQUAL:
			lambda x, y: x.equal(y) or x.less(y),
	}


	def evaluate(self):
		function = BinaryExpression.functions[self.operator]

		assignments = (
			Token.EQUAL, Token.PLUS_EQUAL,Token.MINUS_EQUAL, Token.STAR_EQUAL,
			Token.SLASH_EQUAL, Token.DOUBLE_SLASH_EQUAL, Token.PERCENT_EQUAL,
			Token.SHL_EQUAL, Token.SHR_EQUAL
		)

		if self.operator in assignments:
			return function(self.left, self.right.evaluate())

		return function(self.left.evaluate(), self.right.evaluate())

	def __init__(self, operator, left, right):
		self.type = Expression.BINARY
		self.operator = operator
		self.left = left
		self.right = right

	def __repr__(self):
		return f'({self.operator} {self.left} {self.right})'


class LogicalExpression(Expression):
	# TODO: reimplement and move to TrogonObject
	def evaluate(self):
		if self.operator == Token.AND:
			if not self.left.evaluate().to(TrogonBool).value:
				return TrogonFalse

			return self.right.evaluate().to(TrogonBool)

		elif self.operator == Token.OR:
			if self.left.evaluate().to(TrogonBool).value:
				return TrogonTrue

			return self.right.evaluate().to(TrogonBool)

	def __init__(self, operator, left, right):
		self.type = Expression.LOGICAL
		self.operator = operator
		self.left = left
		self.right = right

	def __repr__(self):
		return f'({self.operator} {self.left} {self.right})'


class BlockExpression(Expression):
	def evaluate(self):
		result = TrogonNull
		found_return = False

		State.begin()
		for s in self.statements:
			#if s.type == Statement.RETURN:
			#	result = s.expression.evaluate()
			#	found_return = True
			#	break

			s.interpret()

		if not found_return:
			result = self.expression.evaluate() if self.expression else TrogonNull
		State.end()

		return result

	def __init__(self, statements, expression):
		self.type = Expression.BLOCK
		self.statements = statements
		self.expression = expression

	def __repr__(self):
		return f'(BLOCK {self.statements} ->{self.expression})'


class IfExpression(Expression):
	def evaluate(self):
		if self.condition.evaluate().to(TrogonBool).value == True:
			return self.true_block.evaluate()
		elif self.else_block:
			return self.else_block.evaluate()

	def __init__(self, condition, true_block, else_block=None):
		self.type = Expression.IF;
		self.condition = condition
		self.true_block = true_block
		self.else_block = else_block

	def __repr__(self):
		return f'(IF {self.condition} {self.true_block} {self.else_block})'


class FunctionDeclarationExpression(Expression):
	def evaluate(self):
		return TrogonFunction(
			len(self.argnames), self.name, self.argnames, self.block)

	def __init__(self, name, argnames, block):
		self.name = name
		self.argnames = argnames
		self.block = block

	def __repr__(self):
		return f'(DEF {self.name}, {self.argnames}, {self.block})'