import copy
from runtime import RuntimeException

current_state = None

# TODO: can't place it in `variables.py` due to circular import
types_passed_by_value = [0, 1, 2, 3, 6]
#[TrogonType, TrogonBool, TrogonString, TrogonNumber, TrogonNulltype]

class State:
	def get_state():
		global current_state
		return current_state

	def set_state(state):
		global current_state
		current_state = state

	def begin(self=None):
		global current_state

		if self:
			return State(self)

		current_state = State(current_state)
		return current_state

	# TODO:
	def end(self=None):
		global current_state

		if self:
			return self.parent

		current_state = current_state.parent

	def register(self, name, value, from_literal=False):
		if name in self.variables:
			raise RuntimeException(f'Tried to redefine variable {name}')

		if value.type in types_passed_by_value or from_literal:
			self.variables[name] = copy.deepcopy(value)
		else:
			self.variables[name] = copy.copy(value)

	def get(self, name):
		head = self
		while head and name not in head.variables:
			head = head.parent

		if not head or name not in head.variables:
			raise RuntimeException(f'Variable {name} is not defined')

		return head.variables[name]

	def set(self, name, value, from_literal=False):
		head = self
		while head and name not in head.variables:
			head = head.parent

		if not head or name not in head.variables:
			raise RuntimeException(f'Implicit variable definition is not allowed')

		if value.type in types_passed_by_value or from_literal:
			head.variables[name] = copy.deepcopy(value)
		else:
			head.variables[name] = copy.copy(value)

	def debug(self=None):
		state = State.get_state() if not self else self
		while state:
			print({x: state.variables[x].value for x in state.variables}, end=' -> ')
			state = state.parent
		print('end')

	def __init__(self, parent=None):
		self.parent = parent
		self.variables = {}

global_state = State()
current_state = global_state