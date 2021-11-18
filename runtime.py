class RuntimeException(Exception):
	pass

class ReturnException(Exception):
	def __init__(self, value):
		Exception.__init__(self, 'Uncaught return')
		self.value = value

class ContinueException(Exception):
	def __init__(self):
		Exception.__init__(self, 'Uncaught continue')

class BreakException(Exception):
	def __init__(self):
		Exception.__init__(self, 'Uncaught break')