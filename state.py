import copy
from runtime import RuntimeException
current_state = None

class State:
	def get_state():
		global current_state
		return current_state

	def begin(self=None):
		global current_state
		current_state = State(current_state)
		return current_state

	# TODO:
	def end(self=None):
		global current_state
		current_state = current_state.parent

	def register(self, name, value):
		if name in self.variables:
			raise RuntimeException(f'Tried to redefine variable {name}')

		self.variables[name] = copy.deepcopy(value)

	def get(self, name):
		head = self
		while head and name not in head.variables:
			head = head.parent

		if not head or name not in head.variables:
			raise RuntimeException(f'Variable {name} is not defined')

		return head.variables[name]

	def set(self, name, value):
		head = self
		while head and name not in head.variables:
			head = head.parent

		if not head or name not in head.variables:
			raise RuntimeException(f'Implicit variable definition is not allowed')

		head.variables[name] = copy.deepcopy(value)

	def debug():
		state = State.get_state()
		while state:
			print({x: state.variables[x].value for x in state.variables}, end=' -> ')
			state = state.parent
		print('end')

	def __init__(self, parent=None):
		self.parent = parent
		self.variables = {}

global_state = State()
current_state = global_state