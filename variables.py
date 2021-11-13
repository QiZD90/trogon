from runtime import *
from state import State

class TrogonObject:
	NULL = 0
	NUMBER = 1
	STRING = 2
	BOOL = 3
	FUNCTION = 4
	TABLE = 5

	def unary_minus(self):
		raise RuntimeException(
			f'Unary minus is not supported for type <{typename[self.type]}>')

	def call(self, arguments):
		raise RuntimeException(
			f'Call is not supported for type <{typename[self.type]}>')

	def dot(self, argument):
		raise RuntimeException(
			f'<{typename[self.type]}> doesn\'t have a property {argument}')

	def subscript(self, index):
		raise RuntimeException(
			f'Subscription is not supported for type <{typename[self.type]}>')

	def subscript_assign(self, index, value):
		raise RuntimeException(
			f'Subscription is not supported for type <{typename[self.type]}>')

	def not_supported_error(operator):
		def inner(x, y):
			raise RuntimeException(
				f'{operator} is not supported for types <{typename[x.type]}> and '
				+ f'<{typename[y.type]}>')

		return inner

	add = not_supported_error('+')
	sub = not_supported_error('-')
	mul = not_supported_error('*')
	divide = not_supported_error('/')
	div = not_supported_error('//')
	mod = not_supported_error('%')
	shl = not_supported_error('<<')
	shr = not_supported_error('>>')
	equal = not_supported_error('==')
	greater = not_supported_error('>')
	less = not_supported_error('<')

	def to(self, o):
		raise RuntimeException(
			f'Can\'t cast <{typename[self.type]}> to <{typename[o.type]}>')

	def __init__(self, type, value):
		self.type = type
		self.value = value

	def __repr__(self):
		return f'<{self.type}>'


class TrogonNullType(TrogonObject):
	type = TrogonObject.NULL

	def to(self, o):
		if o == TrogonNull:
			return self

		elif o == TrogonBool:
			return TrogonFalse

		elif o == TrogonString:
			return TrogonString('null')

		return TrogonObject.to(self, o)

	def __init__(self):
		self.value = None

TrogonNull = TrogonNullType()


class TrogonBool(TrogonObject):
	type = TrogonObject.BOOL

	def equal(self, y):
		if y.type != TrogonObject.BOOL:
			return TrogonObject.equal(self, y)

		return TrogonBool(True if self.value == y.value else False)

	def to(self, o):
		if o == TrogonBool:
			return self

		elif o == TrogonString:
			return TrogonString('true' if self.value == True else 'false')

		elif o == TrogonNumber:
			return TrogonNumber(1 if self.value == True else 0)

		return TrogonObject.to(self, o)

	def __init__(self, value): # TODO: check if value is bool :P
		self.value = value
	
TrogonTrue, TrogonFalse = TrogonBool(True), TrogonBool(False)


class TrogonNumber(TrogonObject):
	type = TrogonObject.NUMBER

	unary_minus = lambda x: TrogonNumber(-self.value)

	def if_second_operand_is_number(f, operator):
		def inner(x, y):
			if y.type != TrogonObject.NUMBER:
				TrogonObject.not_supported_error(operator)(x, y)
				return TrogonNull # just to be safe :)

			return TrogonNumber(f(x.value, y.value))

		return inner


	add = if_second_operand_is_number(lambda x, y: x + y, '+')
	sub = if_second_operand_is_number(lambda x, y: x - y, '-')
	mul = if_second_operand_is_number(lambda x, y: x * y, '*')
	divide = if_second_operand_is_number(lambda x, y: x / y, '/') # TODO: !! division by zero !!
	div = if_second_operand_is_number(lambda x, y: x // y, '//')
	mod = if_second_operand_is_number(lambda x, y: x % y, '%')
	shl = if_second_operand_is_number(lambda x, y: x << y, '<<')
	shr = if_second_operand_is_number(lambda x, y: x >> y, '>>')

	def equal(self, y):
		if y.type != TrogonObject.NUMBER:
			return TrogonObject.equal(self, y)

		return TrogonTrue if self.value == y.value else TrogonFalse

	def greater(self, y):
		if y.type != TrogonObject.NUMBER:
			return TrogonObject.greater(self, y)

		return TrogonTrue if self.value > y.value else TrogonFalse

	def less(self, y):
		if y.type != TrogonObject.NUMBER:
			return TrogonObject.less(self, y)

		return TrogonTrue if self.value < y.value else TrogonFalse

	def to(self, o):
		if o == TrogonNumber:
			return self

		elif o == TrogonString:
			return TrogonString(str(self.value))

		elif o == TrogonBool:
			return TrogonTrue if self.value != 0 else TrogonFalse

		return TrogonObject.to(o)

	def __init__(self, value): # TODO: check if value is int/float
		self.value = value


class TrogonString(TrogonObject):
	type = TrogonObject.STRING

	def equal(self, y):
		if y.type != TrogonObject.STRING:
			return TrogonObject.equal(self, y)

		return TrogonTrue if self.value == y.value else TrogonFalse

	def add(self, y):
		if y.type != TrogonObject.STRING:
			TrogonObject.not_supported_error('+')(self, y)
			return TrogonNull

		return TrogonString(self.value + y.value)

	def subscript(self, index):
		if index.type != TrogonObject.NUMBER:
			raise RuntimeException(
				f'Can\'t subscript strings with <{typename[index.type]}>')

		if type(index.value) != int:
			raise RuntimeException('Can\'t subscript strings with a non-integer')

		if index.value < 0 or index.value >= len(self.value):
			raise RuntimeException('String subscription out of bounds')

		return TrogonString(self.value[index.value])

	def subscript_assign(self, index, value):
		if index.type != TrogonObject.NUMBER:
			raise RuntimeException(
				f'Can\'t subscript strings with <{typename[index.type]}>')

		if type(index.value) != int:
			raise RuntimeException('Can\'t subscript strings with a non-integer')

		if index.value < 0 or index.value >= len(self.value):
			raise RuntimeException('String subscription out of bounds')

		if value.type != TrogonObject.STRING:
			raise RuntimeException(
				f'Can\'t assign <{typename[index.type]}> to a string character!')

		if len(value.value) > 1:
			raise RuntimeException('Can\'t assign a string to a string character')

		if not value.value:
			del self.value[index.value]
		else:
			self.value[index.value] = value.value[0]

		return TrogonString(self.value[index.value])

	# TODO: == > < !!!!

	def to(self, o):
		if o == TrogonString:
			return self

		elif o == TrogonNumber:
			# TODO: yeah, it should be a something like `try_to_parse` function
			return TrogonNumber(int(''.join(self.value)))

		elif o == TrogonBool:
			return TrogonTrue if len(self.value) > 0 else TrogonFalse

		return TrogonObject.to(self, o)

	def __init__(self, value):
		self.value = [x for x in value]


class TrogonTable(TrogonObject):
	type = TrogonObject.TABLE

	def to(self, o):
		if o == TrogonTable:
			return self

		elif o == TrogonString:
			return None
			#f'\{","\}'

		elif o == TrogonBool:
			return bool(self.value)

		return TrogonObject.to(self, o)

	def __init__(self, value):
		pass


class TrogonCallable(TrogonObject):
	type = TrogonObject.FUNCTION
	value = None

	def call(self, arguments):
		if len(arguments) != self.arity:
			raise RuntimeException(
				f'Expected {self.arity} arguments, got {len(arguments)}')
		return TrogonNull

	def to(self, o):
		if o == TrogonCallable:
			return self

		elif o == TrogonBool:
			return TrogonTrue

		return TrogonObject.to(self, o)

	def __init__(self, arity):
		self.arity = arity


class TrogonPrintFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def call(self, arguments):
		TrogonCallable.call(self, arguments)
		print(''.join(arguments[0].evaluate().to(TrogonString).value))
		return TrogonNull

	def __init__(self):
		self.arity = 1


class TrogonInputFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def call(self, arguments):
		TrogonCallable.call(self, arguments)
		return TrogonString(input())

	def __init__(self):
		self.arity = 0


class TrogonFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def call(self, arguments):
		TrogonCallable.call(self, arguments)

		state = State.begin()
		for i, argname in enumerate(self.argnames):
			state.register(argname, arguments[i].evaluate())

		if self.name:
			state.register(self.name, self)

		result = self.block.evaluate()
		state.end()

		return result

	def __init__(self, arity, name, argnames, block):
		self.arity = arity
		self.name = name
		self.argnames = argnames
		self.block = block


class TrogonTableFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def call(self, arguments):
		TrogonCallable.call(self, arguments)
		return TrogonTable()

	def __init__(self):
		self.arity = 0


typename = {
	TrogonObject.NULL: 'nulltype',
	TrogonObject.NUMBER: 'number',
	TrogonObject.STRING: 'string',
	TrogonObject.TABLE: 'table',
	TrogonObject.BOOL: 'bool',
	TrogonObject.FUNCTION: 'function'
}