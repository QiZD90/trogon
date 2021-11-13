import sys

from lexer import Token, LexingException, Lexer
from expression import *
from statement import *
from parser import ParseException, Parser
from variables import *
from state import global_state

global_state.register('print', TrogonPrintFunction())
global_state.register('input', TrogonInputFunction())
global_state.register('table', TrogonTableFunction())

if __name__ == '__main__':
	if len(sys.argv) > 2:
		print('Usage: python trogon.py [fname]')
		sys.exit(1)

	if len(sys.argv) == 2:
		code = ''
		try:
			file =  open(sys.argv[1], 'r')
			code = file.read()
			file.close()
		except:
			print('An error occured. You\'re dumb')
			sys.exit(1)

		print("### LEXING ###")
		lexer = Lexer(code)
		tokens = lexer.scan()
		print(tokens)
		print()

		print('### PARSING ###')
		parser = Parser(tokens)
		ast = parser.parse()
		print(ast)

		print('### INTERPRETING ###')
		for s in ast:
			s.interpret()

	else:
		while True:
			print('### INPUT ###')
			code = input()
			if code == 'exit':
				break
			#print(code)
			print()

			print("### LEXING ###")
			lexer = Lexer(code)
			tokens = lexer.scan()
			print(tokens)
			print()

			print('### PARSING ###')
			parser = Parser(tokens)
			ast = parser.parse()
			print(ast)

			print('### INTERPRETING ###')
			for s in ast:
				s.interpret()