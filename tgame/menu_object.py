import curses

from active_object import active_object
from constants import *

# __init__ helper
def _assume_actions_match(suffix, string_list):
	'''Helper for _assume_actions

	Input:
	suffix : a string
	string_list : a list of strings

	Output:
	a stirng s if s is the only element of string_list of the form s =
	= prefix + suffix with suffix in MENU_ACTION_PREFIXES
	'''

	# format the suffix to match possible methods
	#  - spaces replaced with underscores
	suffix = suffix.replace(' ', '_')
 	found_something = False	# turn true after the firs entry is detected
	out = None

	for prefix in MENU_ACTION_PREFIXES:
		# check if the word is the first entry in the list
		if prefix + suffix in string_list:
			if not found_something:		# if this is the first one
				out = prefix + suffix
				found_something = True

			else:						# if this is not the first one
				return None
	
	# remark that we don't need to check if we found something since
	#  out is None by default.
	return out

def _assume_actions(self):
	'''Tries to assume the action array of a menu

	Input:
	instance of @menu_object

	Output:
	True if the action succeded, False otherwise

	Note:
	The function tries to assume the action array by looking at self's methods
	trying to find, for each entry opt of self.options a correspoding method called prefix + opt with prefix in MENU_ACTION_PREFIXES. This may fail if either no string or more than one stirng match.

	Remark:
	This function DOES NOT raise errors.
	'''

	# get the methods starting with 'opt'
	methods = dir(self)

	self.actions = []
	for col in self.options:
		new_col = []
		self.actions.append(new_col)

		for opt in col:
			# some options can be left empty by passing None
			if opt is None:
				act = None
			else:
				# look for a matching string in methods
				act = _assume_actions_match(opt, methods)

				# if we could not assume an action for opt, give up
				if act is None:
					return False
			
			new_col.append(act)

	# if you made it that far, that's a good sign right?
	return True

# self.w helper
def _compute_maxw(self):
	# create a list such that to each column in self.options associates
	#  the length of the longest string.

	# current implementation raise errors if there is an empty column.
	#  this can be avoided by end user
	maxw = []
	for col in self.options:
		# if the column is empty or None
		if not col or col == [None]*len(col):
			maxw.append(0)

		# if the column is non-empty and at least one element is not None
		#  assuming all None elements are string
		else:
			maxw.append(max(len(s) for s in \
				filter(lambda x : type(x) == str, col)))

	return maxw

# ev_key helpers
def _key_up_down(self, sign):
	'''Describe the response of the menu to up/down key

	Input:
	sign: the kind of key pressed. +1 for down, -1 for up

	Note:
	the probably strange convetion above makes sense if you consider than to go
	up you need to substract something to the y-coordinate, while to go down
	you need to add 1 to the y-coordinate
	'''

	_n = len(self.options[self._menu_optx])

	# Do-While
	while True:

		self._menu_opty = (self._menu_opty + sign) % _n

		if self.options[self._menu_optx][self._menu_opty] is not None:
			break

def _key_left_right(self, sign):
	# number of columns
	_n = len(self.options)

	# Do-Until
	while True:
		self._menu_optx = (self._menu_optx + sign) % _n

		if len(self.options[self._menu_optx]) > self._menu_opty and \
				self.options[self._menu_optx][self._menu_opty] is not None:

			# exit the Do-Util loop
			break


# new __init__ + getters/setters
def _set____init__(cls):
	
	# remark: active_object add a init statement which does the basic job
	old___init__ = cls.__init__

	# create the new function to replace the attribute
	def new___init__(self, context, *argv, **kwarg):
		#
		# new keyarg : xskip, yskip (space between options) align (l/c/r)
		#  Remark - some of the following variables are used in other functions
		#  which look inside this scope occasionally. Change them with care

		# read & write variables
		#  graphic
		self.x = 0
		self.y = 0
		self.xoff = MENU_XOFFSET
		self.yoff = MENU_YOFFSET
		self.xskip = MENU_XSKIP
		self.yskip = MENU_YSKIP
		self.align = MENU_ALIGN
		self.atton = MENU_ATTRIBUTE_ON
		self.attoff = MENU_ATTRIBUTE_OFF
		#  control
		self.key_up = MENU_KEY_UP
		self.key_down = MENU_KEY_DOWN
		self.key_left = MENU_KEY_LEFT
		self.key_right = MENU_KEY_RIGHT
		self.key_enter = MENU_KEY_ENTER
		#  behaviour
		self.options = None
		self.actions = None

		# Internal variables
		self._menu_optx = 0
		self._menu_opty = 0
		
		# run the old init
		old___init__(self, context, *argv, **kwarg)

		# self.options cannot be left empty
		if self.options is None:
			raise ValueError, "Menu object with unspecified options"

		# when self.actions is empty, we try to assume the role of each
		#  entry in self.options
		if self.actions is None:
			if not _assume_actions(self):
				raise ValueError, "Could not assume actions from instance methods and given options - please explicitly specify them using self.actions"

		
	# Overload the old __init__ function
	cls.__init__ = new___init__

def _set_hw(cls):

	@property
	def w(self):
		
		try:
			# w = sum(maxw) + (#col - 1)*xskip
			maxw = _compute_maxw(self)
			return sum(maxw) + (len(self.options) - 1)*self.xskip
		except:
			if self.options == None:
				raise ValueError, "Computing menu width before passing menu's list of options"
			else:
				raise	

	@w.setter
	def w(self, value):
		raise ValueError, "Assignment to a protected variable"

	@property
	def h(self):

		try:
			# h = #rows + (#rows - 1)*yskip
			#  (#rows - 1)*(yskip + 1) + 1
			return (max(len(col) for col in self.options) - 1) \
				*(self.yskip + 1) + 1
		except:
			if self.options == None:
				raise ValueError, "Computing menu height before passing menu's list of options"
			else:
				raise

	@h.setter
	def h(self, value):
		raise ValueError, "Assignment to a protected variable"

	cls.w = w
	cls.h = h


# new ev_draw
def _set_ev_draw(cls):

	# to check is previously cls had a flg_ev_draw
	flg_ev_draw = False

	if hasattr(cls, 'ev_draw'):
		old_ev_draw = cls.ev_draw
		flg_ev_draw = True

	# define the new function to attach to cls
	def new_ev_draw(self):
		# perform the draw_event of the underlying object
		if flg_ev_draw:
			old_ev_draw(self)

		# _maxw[i] is the length of the longest string int the i-th column
		_maxw = _compute_maxw(self)

		# draw the options
		_x = self.x + self.xoff

		# print all the entrie of option
		#  recall than the elements are arranged in a 2D array (a vector of 
		#  columns). So, the string self.options[i][j] has x-coordinate
		#  depending on i and y-coordinate depending on j
		#
		for _i, col in enumerate(self.options):
			for _j, _string in enumerate(col):
				
				# Exclude the case in which _string is None
				if _string is not None:

					# set the y-coordinate
					_y = self.y + self.yoff + (1 + self.yskip)*_j

					# choose the attribute
					if _i == self._menu_optx and _j == self._menu_opty:
						_att = self.atton
					else:
						_att = self.attoff

					# handle the allignment
					if self.align == 'l':
						_dx = 0

					elif self.align == 'c':
						_dx = (_maxw[_i] - len(_string))/2

					elif self.align == 'r':
						_dx = _maxw[_i] - len(_string)

					self._s.addstr(_y, _x + _dx, _string, _att)

			# after we are done with this column we move _x to the right
			_x += _maxw[_i] + self.xskip

		# we clear local variable so than the ev_draw function called next
		#  will not by accident pick them instead of throwing a NameError or 
		#  an UnboundLocalError
		del _x, _dx, _y, _maxw, _i, _j, _string, _att

	# overload the method
	cls.ev_draw = new_ev_draw


# new ev_key
def _set_ev_key(cls):
	flg_ev_key = False

	if hasattr(cls, 'ev_key'):
		old_ev_key = cls.ev_key
		flg_ev_key = True

	# define the new function
	def new_ev_key(self, keycodes):
		# noone wants an invisible menu to do anything
		if self.visible:

			# check for arrow key
			if self.key_up in keycodes:
				_key_up_down(self, -1)

			elif self.key_down in keycodes:
				_key_up_down(self, 1)

			elif self.key_left in keycodes:
				_key_left_right(self, -1)

			elif self.key_right in keycodes:
				_key_left_right(self, 1)

			elif self.key_enter in keycodes:
				# get the right method
				f = getattr(self, \
					self.actions[self._menu_optx][self._menu_opty])

				# execute the method
				f()

		if flg_ev_key:
			old_ev_key(self, keycodes)

	# add the new method to cls
	cls.ev_key = new_ev_key


# decorator
def menu_object(cls):

	# set the draw function before calling the @active_object decorator
	#  so that code here is treated as user code (i.e. it does not skip the
	#  visible check)
	_set_ev_draw(cls)

	# apply precendent decorator
	cls = active_object(cls)

	# method modifier
	_set____init__(cls)

	_set_hw(cls)

	_set_ev_key(cls)

	return cls