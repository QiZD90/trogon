from runtime import *
from state import *
from lexer import *
import copy
import random

class TrogonObject:
	NULL = 0
	NUMBER = 1
	STRING = 2
	BOOL = 3
	FUNCTION = 4
	TABLE = 5
	TYPE = 6

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
	equal = lambda x, y: TrogonFalse
	greater = not_supported_error('>')
	less = not_supported_error('<')

	def to(self, o):
		raise RuntimeException(
			f'Can\'t cast <{typename[self.type]}> to <{typename[o.type]}>')

	def __init__(self, type, value):
		self.type = type
		self.value = value

	def __hash__(self):
		return hash((self.type, self.value))

	def __eq__(self, x):
		if self is x:
			return TrogonTrue

		return self.equal(x).value

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

	def equal(self, y):
		if y.type != TrogonObject.NULL:
			return TrogonFalse

		return TrogonTrue

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

	def __init__(self, value=False): # TODO: check if value is bool :P
		self.value = value
	
TrogonTrue, TrogonFalse = TrogonBool(True), TrogonBool(False)


class TrogonNumber(TrogonObject):
	type = TrogonObject.NUMBER

	def unary_minus(self):
		return TrogonNumber(-self.value)

	def if_second_operand_is_number(f, operator):
		def inner(x, y):
			if y.type != TrogonObject.NUMBER:
				TrogonObject.not_supported_error(operator)(x, y)
				return TrogonNull # just to be safe :)

			return TrogonNumber(f(x.value, y.value))

		return inner

	def dot(self, argument):
		return TrogonObject.dot(self, argument)


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

		return TrogonObject.to(self, o)

	def __init__(self, value=0): # TODO: check if value is int/float
		self.value = value


class TrogonString(TrogonObject):
	type = TrogonObject.STRING

	# TODO: this needs a proper lexer and parser
	# TODO: some way to escape braces?
	def format(self, arguments):
		table = arguments[0]
		if table.type != TrogonObject.TABLE:
			raise RuntimeException('Expected table as an argument to string.format')

		pos = 0
		result = []
		while pos < len(self.value):
			char = self.value[pos]
			if char == '{':
				argname = []
				pos += 1
				while pos < len(self.value) and self.value[pos] != '}':
					if self.value[pos] == '{':
						raise RuntimeException('Unexpected { in a format pattern')
					argname.append(self.value[pos])
					pos += 1

				if self.value[pos] != '}':
					raise RuntimeException('Expected } in a format pattern')

				s = ''.join(table.subscript(TrogonString(argname)).to(TrogonString).value)
				result.append(s)
			elif char == '}':
				raise RuntimeException('Unexpected } in a format pattern')
			else:
				result.append(char)
			pos += 1

		return TrogonString(''.join(result))

	def dot(self, argument):
		if argument == 'length':
			return TrogonCallable(0, lambda _: TrogonNumber(len(self.value)))
		if argument == 'format':
			return TrogonCallable(1, lambda x: self.format(x))

		return TrogonObject.dot(self, argument)

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
			self.value[index.value] = str(value.value[0])

		return self

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

	def __init__(self, value=None):
		self.value = [x for x in value] if value else []

	def __hash__(self):
		return hash(''.join(self.value))


class TrogonTable(TrogonObject):
	type = TrogonObject.TABLE

	def clear(self):
		self.value.clear()
		return TrogonNull

	def remove(self, arguments):
		key = arguments[0]

		if key.type == TrogonObject.TABLE:
			raise RuntimeException('Tables can\'t be table keys')

		if key in self.value:
			del self.value[key]

		return TrogonNull

	def dot(self, argument):
		if argument == 'clear':
			return TrogonCallable(0, lambda _: self.clear())
		if argument == 'remove':
			return TrogonCallable(1, lambda x: self.remove(x))
		if argument == 'length':
			return TrogonCallable(0, lambda _: TrogonNumber(len(self.value)))

		TrogonObject.dot(self, argument)

	def subscript(self, index):
		if index.type == TrogonObject.TABLE:
			raise RuntimeException('Can\'t subscript tables with tables!')

		if index in self.value:
			return self.value[index]

		return TrogonNull

	def subscript_assign(self, index, value):
		if index.type == TrogonObject.TABLE:
			raise RuntimeException('Can\'t subscript tables with tables!')

		v = copy.deepcopy(value) if value.type in types_passed_by_value else copy.copy(value)
		self.value[index] = v
		return self 

	def equal(self, y):
		if y.type != TrogonObject.TABLE:
			return TrogonObject.equal(self, y)

		if len(self.value) != len(y.value):
			return TrogonFalse

		for k, v in self.value.items():
			if k not in y.value or v != y.value[k]:
				return TrogonFalse

		return TrogonTrue

	def to(self, o):
		if o == TrogonTable:
			return self

		elif o == TrogonString: # TODO: cross referencing table
			pairs = []
			for key in self.value:
				key_string = ''.join(key.to(TrogonString).value)
				if key.type == TrogonObject.STRING:
					key_string = "'" + key_string + "'"

				value = self.value[key]
				value_string = None
				if self == value:
					value_string = r'{...}'
				else:
					value_string = ''.join(value.to(TrogonString).value)
					if value.type == TrogonObject.STRING:
						value_string = "'" + value_string + "'"

				pairs.append(key_string + ': ' + value_string)

			return TrogonString('{' + ', '.join(pairs) + '}')

		elif o == TrogonBool:
			return TrogonTrue if len(self.value) > 0 else TrogonFalse

		return TrogonObject.to(self, o)

	def __init__(self):
		self.value = {}


class TrogonCallable(TrogonObject):
	type = TrogonObject.FUNCTION
	value = None

	def check_arity(self, arguments):
		if len(arguments) != self.arity:
			raise RuntimeException(
				f'Expected {self.arity} arguments, got {len(arguments)}')

	def call(self, arguments):
		if len(arguments) != self.arity:
			raise RuntimeException(
				f'Expected {self.arity} arguments, got {len(arguments)}')

		return self.function(arguments)

	def to(self, o):
		if o == TrogonCallable:
			return self

		elif o == TrogonBool:
			return TrogonTrue

		elif o == TrogonString:
			return TrogonString('<function>')

		return TrogonObject.to(self, o)

	def __init__(self, arity, function):
		self.arity = arity
		self.function = function


class TrogonPrintFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def equal(self, y):
		return TrogonTrue if isinstance(y, TrogonPrintFunction) else TrogonFalse

	def call(self, arguments):
		self.check_arity(arguments)

		print(''.join(arguments[0].to(TrogonString).value))
		return TrogonNull

	def __init__(self):
		self.arity = 1


class TrogonPrintFormattedFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def equal(self, y):
		return TrogonTrue if isinstance(y, TrogonPrintFormattedFunction) else TrogonFalse

	def call(self, arguments):
		self.check_arity(arguments)

		pattern, table = arguments
		print(''.join(pattern.format([table]).to(TrogonString).value), end='')
		return TrogonNull

	def __init__(self):
		self.arity = 2


class TrogonInputFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def equal(self, y):
		return TrogonTrue if isinstance(y, TrogonInputFunction) else TrogonFalse

	def call(self, arguments):
		self.check_arity(arguments)
		return TrogonString(input())

	def __init__(self):
		self.arity = 0


class TrogonFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def equal(self, y):
		if not isinstance(y, TrogonFunction):
			return TrogonFalse

		return TrogonBool(self.arity == y.arity and self.block == y.block)

	def call(self, arguments):
		self.check_arity(arguments)

		state = self.state.begin()
		state_previous = State.get_state()
		State.set_state(state)

		for i, argname in enumerate(self.argnames):
			state.register(argname, arguments[i])
		
		if self.name and self.name not in self.argnames:
			state.register(self.name, self)

		try:
			result = self.block.evaluate()
		except ReturnException as e:
			result = e.value
		except (ContinueException, BreakException) as e:
			raise RuntimeException('Uncaught break or continue')
		finally:
			state.end()
			State.set_state(state_previous)

		return result

	def __hash__(self):
		return hash((self.arity, self.block))

	def __init__(self, arity, name, argnames, block):
		self.arity = arity
		self.name = name
		self.argnames = argnames
		self.block = block
		self.state = State.get_state()


class TrogonRandomFunction(TrogonCallable):
	type = TrogonObject.FUNCTION

	def equal(self, y):
		return TrogonTrue if isinstance(y, TrogonRandomFunction) else TrogonFalse

	def call(self, arguments):
		self.check_arity(arguments)
		x, y = arguments

		if x.type != TrogonObject.NUMBER or y.type != TrogonObject.NUMBER or\
		   not isinstance(x.value, int) or not isinstance(y.value, int):
			raise RuntimeException('Random takes 2 integer arguments')

		return TrogonNumber(random.randrange(x.value, y.value))

	def __init__(self):
		self.arity = 2


class TrogonType(TrogonCallable):
	type = TrogonObject.TYPE

	def equal(self, y):
		if not isinstance(y, TrogonType):
			return TrogonFalse

		return TrogonTrue if self.value == y.value else TrogonFalse

	def call(self, arguments):
		self.check_arity(arguments)
		return self.value()

	def to(self, o):
		if o == TrogonType:
			return self

		elif o == TrogonBool:
			return TrogonTrue

		return TrogonObject.to(self, o)

	def __init__(self, value):
		self.value = value
		self.arity = 0

TrogonTypeType = TrogonType(TrogonType)
TrogonBoolType = TrogonType(TrogonBool)
TrogonStringType = TrogonType(TrogonString)
TrogonNumberType = TrogonType(TrogonNumber)
TrogonNullTypeType = TrogonType(TrogonNullType)
TrogonFunctionType = TrogonType(TrogonFunction)
TrogonTableType = TrogonType(TrogonTable)


typename = {
	TrogonObject.NULL: 'nulltype',
	TrogonObject.NUMBER: 'number',
	TrogonObject.STRING: 'string',
	TrogonObject.TABLE: 'table',
	TrogonObject.BOOL: 'bool',
	TrogonObject.FUNCTION: 'function',
	TrogonObject.TYPE: 'type'
}