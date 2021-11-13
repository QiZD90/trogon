from expression import *
from statement import *
from state import *

class ParseException(Exception):
	pass

class Parser:
	final_tokentypes = [
		Token.STRING_LITERAL, Token.NUMBER_LITERAL,
		Token.TRUE, Token.FALSE, Token.NULL]

	expression_with_block_predicate = [Token.IF, Token.LEFT_BRACE, Token.FUNCTION]

	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.line = 0


	# ==== Utils ====

	def peek(self):
		if self.pos >= len(self.tokens):
			return None
		return self.tokens[self.pos]

	def next(self):
		if self.pos >= len(self.tokens):
			return None

		t = self.tokens[self.pos]
		self.pos += 1
		self.line = t.line
		return t

	def expect(self, type, s):
		t = self.next()
		if not t or t.type != type:
			raise ParseException(f'line {self.line}: ' + s + f' got {t.type if t else None}')

		return t

	def next_is(self, tokentype):
		if type(tokentype) in (list, tuple):
			return self.peek() and self.peek().type in tokentype
		else:
			return self.peek() and self.peek().type == tokentype

	def match(self, tokentype):
		if self.next_is(tokentype):
			self.next()
			return True

		return False


	# ==== Some actual AST parsing functions ====

	def final(self):
		if self.next_is(Parser.final_tokentypes):
			return LiteralExpression(self.next().value)

		if self.next_is(Token.IDENTIFIER):
			return VariableExpression(self.next().value)

		if self.match(Token.LEFT_PAREN):
			expression = self.expression()
			self.expect(Token.RIGHT_PAREN, 'Expected )')
			return expression

	def subscription(self):
		expression = self.final()

		while self.match(Token.LEFT_BRACKET):
			print('>',expression)
			expression = SubscriptionExpression(expression, self.expression())
			print('<',expression)
			self.expect(Token.RIGHT_BRACKET, 'Expected ]')

		return expression
			

	def call(self):
		expression = self.subscription()

		while self.match(Token.LEFT_PAREN):
			arguments = []
			while not self.next_is(Token.RIGHT_PAREN):
				arguments.append(self.expression())

				if not self.next_is(Token.RIGHT_PAREN):
					self.expect(Token.COMMA, 'Expected ,')

			self.expect(Token.RIGHT_PAREN, 'Expected )')
			expression = CallExpression(expression, arguments)

		return expression


	def unary(self):
		if self.match(Token.MINUS):
			return UnaryExpression(Token.MINUS, self.final())

		return self.call()

	#TODO:!!!!!
	def cast(self):
		expression = self.unary()
		return expression

		if self.match(Token.AS):
			
			return CastExpression(expression,)

	def factor(self):
		expression = self.cast()

		tokens = (Token.SLASH, Token.STAR, Token.DOUBLE_SLASH, Token.PERCENT)
		while self.next_is(tokens):
			expression = BinaryExpression(self.next().type, expression, self.cast())

		return expression

	def term(self):
		expression = self.factor()
		tokens = (Token.PLUS, Token.MINUS)
		while self.next_is(tokens):
			expression = BinaryExpression(self.next().type, expression, self.factor())

		return expression

	def shift(self):
		expression = self.term()

		tokens = (Token.SHL, Token.SHR)
		while self.next_is(tokens):
			expression = BinaryExpression(self.next().type, expression, self.term())

		return expression

	def comparison(self):
		expression = self.shift()

		tokens = (Token.GREATER, Token.LESS, Token.GREATER_EQUAL, Token.LESS_EQUAL)
		if self.next_is(tokens):
			expression = BinaryExpression(self.next().type, expression, self.shift())

		return expression

	def equality(self):
		expression = self.comparison()

		tokens = (Token.EQUAL_EQUAL, Token.BANG_EQUAL)
		if self.next_is(tokens):
			expression = BinaryExpression(self.next().type, expression, self.comparison())

		return expression

	def logicalfactor(self):
		expression = self.equality()

		tokens = Token.AND
		while self.next_is(tokens):
			expression = LogicalExpression(self.next().type, expression, self.equality())

		return expression

	def logicalterm(self):
		expression = self.logicalfactor()

		tokens = Token.OR
		while self.next_is(tokens):
			expression = LogicalExpression(self.next().type, expression, self.logicalfactor())

		return expression

	def assign(self):
		expression = self.logicalterm()
		if expression and self.match(Token.EQUAL):
			expression = BinaryExpression(Token.EQUAL, expression, self.assign())

		return expression

	def ifexpr(self):
		if self.match(Token.IF):
			condition = self.expression()
			true_block = self.block()
			else_block = None

			if self.match(Token.ELSE):
				else_block = self.block()

			return IfExpression(condition, true_block, else_block)

		return self.assign()

	def funcdeclexpr(self, name_expected=False):
		if self.match(Token.FUNCTION):
			name = None
			if self.next_is(Token.IDENTIFIER):
				name = self.next().value
			elif name_expected:
				raise ParseException('Expected function name')

			self.expect(Token.LEFT_PAREN, 'Expected (')
			argnames = []
			while not self.next_is(Token.RIGHT_PAREN):
				arg = self.expect(Token.IDENTIFIER, 'Expected IDENTIFIER').value
				argnames.append(arg)

				if not self.next_is(Token.RIGHT_PAREN):
					self.expect(Token.COMMA, 'Expected comma')
			self.expect(Token.RIGHT_PAREN, 'Expected )')

			block = self.block()
			return FunctionDeclarationExpression(name, argnames, block)

		return self.ifexpr()

	def expression_without_block(self):
		return self.assign()

	def expression_with_block(self):
		if self.next_is(Token.LEFT_BRACE):
			return self.block()
		else:
			return self.funcdeclexpr()

	def expression(self):
		if self.next_is(Parser.expression_with_block_predicate):
			return self.expression_with_block()
		else:
			return self.expression_without_block()
		

	def block(self):
		statements = []
		expression = None

		self.expect(Token.LEFT_BRACE, 'Expected {')
		while not self.next_is(Token.RIGHT_BRACE):
			obj = self.statement_or_expression()
			if isinstance(obj, Expression):
				if self.next_is(Token.RIGHT_BRACE):
					expression = obj
					break
				else:
					obj = ExpressionStatement(obj)

			statements.append(obj)

		self.expect(Token.RIGHT_BRACE, 'Expected }')
		return BlockExpression(statements, expression)

	def let_statement(self):
		self.expect(Token.LET, 'Expected let')
		identifier = self.expect(Token.IDENTIFIER, 'Expected identifier')

		expression = None
		if self.match(Token.EQUAL):
			expression = self.expression()

		return LetStatement(identifier.value, expression)

	def while_statement(self):
		self.expect(Token.WHILE, 'Expected while')
		condition = self.expression()
		block = self.block()

		return WhileStatement(condition, block)

	def for_statement(self):
		self.expect(Token.FOR, 'Expected for')
		has_let = self.match(Token.LET)
		lvalue = self.expression()
		if not lvalue or not lvalue.type == Expression.LVALUE:
			raise ParseException('Expected variable')

		self.expect(Token.IN, 'Expected in')
		left_bound = self.expression()
		self.expect(Token.DOUBLE_DOT, 'Expected ..')
		right_bound = self.expression()
		block = self.block()

		return ForStatement(
			lvalue, left_bound, right_bound, block, has_let=has_let)

	def return_statement(self):
		self.expect(Token.RETURN, 'Expected return')
		if self.next_is(Token.SEMICOLON):
			return ReturnStatement(None)

		return ReturnStatement(self.expression())

	def statement(self, can_return_expr=False):
		if self.next_is(Token.LET):
			statement = self.let_statement()
			self.expect(Token.SEMICOLON, 'Expected ;')
			return statement

		elif self.next_is(Token.WHILE):
			return self.while_statement()

		elif self.next_is(Token.FOR):
			return self.for_statement()

		elif self.next_is(Token.RETURN):
			return self.return_statement()

		elif self.next_is(Token.FUNCTION):
			expression = self.funcdeclexpr()
			if can_return_expr:
				return expression

			if not expression.name:
				raise ParseException('Expected function name')

			return FunctionDeclarationStatement(expression)

		elif self.match(Token.SEMICOLON):
			return Statement(Statement.NULL, [])

		elif self.next_is(Parser.expression_with_block_predicate):
			expression = self.expression_with_block()
			if self.match(Token.SEMICOLON): # optional ;
				return ExpressionStatement(expression)
			return ExpressionStatement(expression) if not can_return_expr else expression

		expression = self.expression_without_block()
		if can_return_expr and not self.next_is(Token.SEMICOLON):
			return expression

		self.expect(Token.SEMICOLON, 'Expected ;')
		return ExpressionStatement(expression)

	def statement_or_expression(self):
		return self.statement(True)

	# corner case:
	# if a % 3 == 0 {'Fizz'} else {''} + if a % 5 == 0 {'Buzz'} else {''}
	# 
	# rn it's parsed like (IF ...) (PLUS None None) (IF ...)
	def parse(self):
		statements = []
		while self.peek() != None:
			statements.append(self.statement())
		return statements