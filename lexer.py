import string
import variables

class Token:
	EOF = 'EOF' # 0

	LEFT_PAREN = 'LEFT_PAREN' #1
	RIGHT_PAREN = 'RIGHT_PAREN' #2
	LEFT_BRACE = 'LEFT_BRACE' #3
	RIGHT_BRACE = 'RIGHT_BRACE' #4
	LEFT_BRACKET = 'LEFT_BRACKET'
	RIGHT_BRACKET = 'RIGHT_BRACKET'
	SEMICOLON = 'SEMICOLON'#5
	COLON = 'COLON'
	COMMA = 'COMMA'
	DOT = 'DOT'
	DOUBLE_DOT = 'DOUBLE_DOT'
	PLUS = 'PLUS' #6
	MINUS = 'MINUS' #7
	STAR = 'STAR' #8
	SLASH = 'SLASH' #9
	DOUBLE_SLASH = 'DOUBLE_SLASH'#10
	PERCENT = 'PERCENT'
	SHL = 'SHL'#11
	SHR = 'SHR'#12

	EQUAL = 'EQUAL'#16
	EQUAL_EQUAL = 'EQUAL_EQUAL'#17
	LESS = 'LESS'#18
	LESS_EQUAL = 'LESS_EQUAL'#19
	GREATER = 'GREATER'#20
	GREATER_EQUAL = 'GREATER_EQUAL'#21
	PLUS_EQUAL = 'PLUS_EQUAL'#22
	MINUS_EQUAL = 'MINUS_EQUAL'#23
	STAR_EQUAL = 'STAR_EQUAL'#24
	SLASH_EQUAL = 'SLASH_EQUAL'#25
	DOUBLE_SLASH_EQUAL = 'DOUBLE_SLASH_EQUAL'#26
	PERCENT_EQUAL = 'PERCENT_EQUAL'
	BANG_EQUAL = 'BANG_EQUAL'#27
	SHL_EQUAL = 'SHL_EQUAL'#28
	SHR_EQUAL = 'SHR_EQUAL'#29

	IDENTIFIER = 'IDENTIFIER'#50
	STRING_LITERAL = 'STRING_LITERAL'#51
	NUMBER_LITERAL = 'NUMBER_LITERAL'#52

	IF = 'IF'#80
	ELSE = 'ELSE'#81
	FOR = 'FOR'#82
	WHILE = 'WHILE'#83
	NULL = 'NULL'#84
	TRUE = 'TRUE'#85
	FALSE = 'FALSE'#86
	FUNCTION = 'FUNCTION'#87
	RETURN = 'RETURN'#88
	BREAK = 'BREAK'
	CONTINUE = 'CONTINUE'
	LET = 'LET'#89
	NOT = 'NOT'#91
	AND = 'AND'#92 
	OR = 'OR'#93
	IN = 'IN'
	AS = 'AS'
	BOOL = 'BOOL'
	STRING = 'STRING'
	NUMBER = 'NUMBER'
	NULLTYPE = 'NULLTYPE'
	TABLE = 'TABLE'

	def __init__(self, type, line, value=None):
		self.type = type
		self.line = line
		self.value = value

	def __repr__(self):
		return f'token({self.type}, {self.value})'


class LexingException(Exception):
	pass


class Lexer:
	radix_digits = {
		2: [x for x in '01'],
		10: [x for x in '0123456789'],
		16: [x for x in '0123456789ABCDEFabcdef']
	}

	escape_characters = {
		'\\n': '\n',
		'\\t': '\t',
		'\\\\': '\\',
		'\\"': '"',
		"\\'": "'" 
	}

	keywords = {
		'if': Token.IF, 'else': Token.ELSE, 'for': Token.FOR,
		'while': Token.WHILE, 'null': Token.NULL, 'true': Token.TRUE,
		'false': Token.FALSE, 'function': Token.FUNCTION, 'return': Token.RETURN,
		'let': Token.LET, 'not': Token.NOT, 'and': Token.AND,
		'or': Token.OR, 'in': Token.IN, 'as': Token.AS,
		'bool': Token.BOOL, 'string': Token.STRING, 'number': Token.NUMBER,
		'nulltype': Token.NULLTYPE, 'break': Token.BREAK, 'continue': Token.CONTINUE,
		'table': Token.TABLE
	}

	keywords_values = {
		'true': True, 'false': False, 'null': None,
		'type': variables.TrogonTypeType, 'bool': variables.TrogonBoolType,
		'string': variables.TrogonStringType, 'number': variables.TrogonNumberType,
		'nulltype': variables.TrogonNullTypeType, 'table': variables.TrogonTableType
	}

	type_tokentypes = [Token.BOOL, Token.NULLTYPE, Token.NUMBER, Token.STRING, Token.TABLE]

	identifier_start = string.ascii_letters + '_'
	identifier_chars = identifier_start + string.digits

	def __init__(self, code):
		self.code = code
		self.line = 1
		self.start = 0
		self.pos = 0
		self.tokens = []

	def peek(self):
		if self.pos >= len(self.code):
			return None
		return self.code[self.pos]

	def peek2(self):
		if self.pos >= len(self.code) - 1:
			return None
		return self.code[self.pos + 1]

	def nextchar(self):
		if self.pos >= len(self.code):
			return None
		c = self.code[self.pos]
		self.pos += 1
		return c

	def scan(self):
		while self.pos < len(self.code):
			c = self.nextchar()

			if c in [' ', '\r', '\t']: # skip the whitespaces
				pass
			elif c == '\n':
				self.line += 1
			elif c == '(':
				self.tokens.append(Token(Token.LEFT_PAREN, self.line))
			elif c == ')':
				self.tokens.append(Token(Token.RIGHT_PAREN, self.line))
			elif c == '{':
				self.tokens.append(Token(Token.LEFT_BRACE, self.line))
			elif c == '}':
				self.tokens.append(Token(Token.RIGHT_BRACE, self.line))
			elif c == '[':
				self.tokens.append(Token(Token.LEFT_BRACKET, self.line))
			elif c == ']':
				self.tokens.append(Token(Token.RIGHT_BRACKET, self.line))
			elif c == ';':
				self.tokens.append(Token(Token.SEMICOLON, self.line))
			elif c == ':':
				self.tokens.append(Token(Token.COLON, self.line))
			elif c == ',':
				self.tokens.append(Token(Token.COMMA, self.line))

			elif c == '.':
				if self.peek() == '.':
					self.nextchar()
					self.tokens.append(Token(Token.DOUBLE_DOT, self.line))
				else:
					self.tokens.append(Token(Token.DOT, self.line))
			elif c == '+':
				if self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.PLUS_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.PLUS, self.line))

			elif c == '-':
				if self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.MINUS_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.MINUS, self.line))

			elif c == '*':
				if self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.STAR_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.STAR, self.line))

			elif c == '/':
				if self.peek() == '/':
					self.nextchar()

					if self.peek() == '=':
						self.nextchar()
						self.tokens.append(Token(Token.DOUBLE_SLASH_EQUAL, self.line))
					else:
						self.tokens.append(Token(Token.DOUBLE_SLASH, self.line))
				elif self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.SLASH_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.SLASH, self.line))

			elif c == '%':
				if self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.PERCENT_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.PERCENT, self.line))

			elif c == '=':
				if self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.EQUAL_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.EQUAL, self.line))

			elif c == '<':
				if self.peek() == '<':
					self.nextchar()

					if self.peek() == '=':
						self.nextchar()
						self.tokens.append(Token(Token.SHL_EQUAL, self.line))
					else:
						self.tokens.append(Token(Token.SHL, self.line))
				elif self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.LESS_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.LESS, self.line))

			elif c == '>':
				if self.peek() == '>':
					self.nextchar()

					if self.peek() == '=':
						self.nextchar()
						self.tokens.append(Token(Token.SHR_EQUAL, self.line))
					else:
						self.tokens.append(Token(Token.SHR, self.line))
				elif self.peek() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.GREATER_EQUAL, self.line))
				else:
					self.tokens.append(Token(Token.GREATER, self.line))

			elif c == '!':
				if self.nextchar() == '=':
					self.nextchar()
					self.tokens.append(Token(Token.BANG_EQUAL, self.line))
				else:
					raise LexingException('Expected "!=" but got "!{}" on line'.format(c, self.line))

			elif c == '#':
				while self.peek() not in ['\n', '\0', None]:
					self.nextchar()
				self.nextchar()

			elif c in '0123456789':
				tmp = [c]
				radix = 10
				dot_found = False

				if c == '0':
					if self.peek() == 'b':
						if self.peek2() in self.radix_digits[2]:
							tmp.append(self.nextchar())
							radix = 2
						else:
							raise LexingException(f"Invalid digit '{self.peek2()}' while parsing base-2 number on line {self.line}")
					elif self.peek() == 'x':
						if self.peek2() in self.radix_digits[16]:
							tmp.append(self.nextchar())
							radix = 16
						else:
							raise LexingException(f"Invalid digit '{self.peek2()}' while parsing base-16 number on line {self.line}")

				while self.peek() in self.radix_digits[radix] + ['_', '.']: # TODO: fail on `2a` or `4__`
					if self.peek() == '.' and self.peek2() == '.':
						break

					c = self.nextchar()

					if c == '.':
						if dot_found:
							raise LexingException("Error while parsing number literal on line " + str(self.line))

						dot_found = True
						tmp.append(c)
					else:
						tmp.append(c)

				value = 0
				if not dot_found:
					value = int(''.join(tmp), radix)
				else:
					if radix != 10:
						raise LexingException('Float literals are only allowed for base-10')
					value = float(''.join(tmp))

				self.tokens.append(
					Token(Token.NUMBER_LITERAL, self.line, value))

			elif c in '\'"':
				tmp = []
				literal = c

				while self.peek() != literal:
					c = self.nextchar()

					if c == '\\':
						if (c + self.peek()) in self.escape_characters:
							tmp.append(self.escape_characters[(c + self.nextchar())])
						else:
							raise LexingException(f'line {self.line}: Invalid escape sequence')
					else:
						tmp.append(c)
				else:
					self.nextchar()
					self.tokens.append(Token(Token.STRING_LITERAL, self.line, ''.join(tmp)))
					continue

				if self.peek() == None:
					raise LexingException(f'line {self.line}: Can\'t find a matching {literal}')

			elif c in self.identifier_start:
				tmp = [c]
				while self.peek() in self.identifier_chars:
					tmp.append(self.nextchar())

				tmp = ''.join(tmp)
				if tmp in self.keywords:
					value = self.keywords_values.get(tmp)
					self.tokens.append(Token(self.keywords[tmp], self.line, value))
				else:
					self.tokens.append(Token(Token.IDENTIFIER, self.line, tmp))

			else:
				raise LexingException(f'Unexpected character "{c}" on line {self.line}')


			self.start = self.pos
			#print(self.tokens)
		return self.tokens