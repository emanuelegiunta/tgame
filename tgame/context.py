import curses

from room import room
from constants import CONTEXT_SPEED
from background import background
from utilities import screen_subwin

class context(object):
	def __init__(self, screen):
		# public variables
		self.speed = CONTEXT_SPEED

		# read only variables
		self._background = None
		self._screen = screen
		
		# private variables
		self._views = []				# list of current views
		self._active_instances = []		# currently active instances
		self._new_instances = []		# buffer of new instances
		self._room_dict = {}			# 
		self._room_list = []			#
		self._room = None				# current room
		self._room_next	= None			# next room after update
		self._room_next_kwarg = None	# next room's optional parameters
		self._room_last_visited = None	# last visited room (room_precedent)
 

	# public variables
	@property
	def screen(self):
		#	
		return self._screen

	@screen.setter
	def screen(self, value):
		#
		raise TypeError, "Assignment to a protected variable"

	@property
	def background(self):
		#
		return self._background

	@background.setter
	def background(self, bkg):
		self._room.background = bkg
		self._background = self._room.background
	

	# room methods
	def room_new(self, name, *argv, **kwarg):
		'''Add a new room and move into the new room
		'''

		# create and store the new room
		new_room = room(self, *argv, **kwarg)
		self.room_add(name, new_room)
		return new_room
 	
	def room_add(self, name, new_room):
		'''Add a given room to the list of rooms, and move into it
		'''
		assert (not self._room_dict.has_key(name)), "Room id already used"

		self._room_dict[name] = new_room
		self._room_list.append(new_room)

		# move into the new room
		#  e : no even on room change
		#  f : force - perform che room change now
		self._room_change(new_room, e = False, f = True)

	def room_goto(self, name, **kwarg):
		assert (self._room_dict.has_key(name)), "Moving to non-existing room"

		# retrieve the given room and move
		next_room = self._room_dict[name]
		self._room_change(next_room, **kwarg)

	def room_precedent(self, **kwarg):
		'''Moves to the last visited room.

		Input:
		ev_perform: boolean. If True a ev_room_start event will be performed

		Note:
		The method move context to the last visited room. If the current room 
		the first one, or there is no room at all the method will throw an
		error.
		'''

		# check if this is not the first room visited in the game
		assert self._room_last_visited is not None, \
			"There is no precedent room"

		next_room = self._room_last_visited
		self._room_change(next_room, **kwarg)

	def room_next(self, **kwarg):
		# throw an error if there is no room at all
		assert self._room is not None, "There is no room in the game"
		
		i = self._room_list.index(self._room)

		# throw an error if this is the last room
		assert len(self._room_list) > (i + 1), "Reached last room"

		next_room = self._room_list[(i + 1)]
		self._room_change(next_room, **kwarg)

	def room_previous(self, **kwarg):
		# throw an error if there is no room at all
		assert self._room is not None, "There is no room in the game"

		i = self._room_list.index(self._room)

		# throw an error if this is the first room
		assert i > 0, "Reached first room"

		next_room = self._room_list[(i - 1)]
		self._room_change(next_room, **kwarg)

	def room_update(self):

		# checked frequently
		if self._room_next is not None:

			# get the paramerert and reset them immediately
			next_room = self._room_next
			kwarg = self._room_next_kwarg

			self._room_next = None
			self._room_next_kwarg = None

			# accepted flags
			#  p/peek : 		a function performed after ev_step_begin
			#  e/ev_perform :	perform ev_room_start [after peek]

			peek = kwarg.pop('p', kwarg.pop('peek', None))
			ev_perform = kwarg.pop('e', kwarg.pop('ev_perform', True))

			# change the list of active objects, views and background
			self._active_instances = next_room.active_instances
			self._new_instances = next_room.new_instances
			self._views = next_room.views
			self._background = next_room.background

			# update the current room pointer
			self._room_last_visited = self._room
			self._room = next_room

			# Extra Actions:
			# 	perform the room start event
			if ev_perform:
				self.ev_perform('ev_room_start')

			# 	perform the peek if not empty
			if peek is not None:
				peek()
				

	def _room_change(self, next_room, **kwarg):
	
		# Check that this is the first change
		if self._room_next is None:

			# extract flags:
			#  f/force : peform the change now (by also calling a room update)

			force = kwarg.pop('f', kwarg.pop('force', False))

			# prepare data for the room change
			self._room_next = next_room
			self._room_next_kwarg = kwarg

			# Extra Actions:
			#  force the room change now
			if force:
				self.room_update()

		# if in the same step I'm changing room two or more times, give up
		else:
			# DEBUG
			s = ''
			for key in self._room_dict.iterkeys():
				if self._room_dict[key] == next_room:
					s += "the other is {}\n".format(key)

				if self._room_dict[key] == self._room_next:
					s += "one is {}\n".format(key)
			assert False, s

			raise RuntimeError, "Two different room change in the same step."


	# Instance methods
	def instance_add(self, inst):
		''' add an instance to the set of instances whose events are performed

		Note:
		Lazy update - to avoid obscure bugs on creation of layered objects that
		reorder the list during an event loop, new object are created at the
		beginning of the next step (another reason is that it may result 
		unexpected that an object performs ev_draw before ev_step_begin)
		see instance_update
		'''

		self._new_instances.append(inst)

	def instance_update(self):
		''' turn to "concretelly active" new instance

		Note: in practice elements from thw new_instances are moved to the list
		of active instances
		'''

		if self._new_instances:
			self._active_instances += self._new_instances
			self.layer_update()

			# empty the current _new_instances.. one way of doing it wrong is
			#  calling self._new_instance = [], as we would now lose the 
			#  connection with the room. Instead:

			self._room.new_instances = []
			self._new_instances = self._room.new_instances

	def instance_remove(self, inst):
		#
		if inst not in self._new_instances:
			self._active_instances.remove(inst)
		else:
			self._new_instances.remove(inst)
	
	def instance_of(self, *filters):

		# concatenate all the filters in one function
		def f(inst):
			for g in filters:
				
				# if g is a stirng, check the class name
				if type(g) == str:
					if inst.__class__.__name__ == g:
						return True
				
				# else assume g is a function
				else:
					if g(inst):
						return True

			return False

		# filtering instance name
		if self._new_instances:
			return filter(f, self._active_instances + self._new_instances)
		else:
			return filter(f, self._active_instances)

	def instance_all(self, *but):
		''' return all instance except those that satisfies at least one formula

		Note:
		@The Gray Area: according to TGA principle new object should not be active until the next step but they need to be visible as most instances
		link with each other at creation time.
		'''

		# concatenate all the filters in one function
		def f(inst):
			for g in but:

				# if g is a string, check the class name
				if type(g) == str:
					if inst.__class__.__name__ == g:
						return False

				# else assume g is a function
				else: 
					if g(inst):
						return False

			return True

		# filtering instance name
		if self._new_instances:
			return filter(f, self._active_instances + self._new_instances)
		else:
			return filter(f, self._active_instances)


	# layer method
	def layer_update(self, all_rooms = False):
		''' order the list of active instance by depth
		
		Note:
		This way object in lower layer are rendered before and appear "behind"
		objects on higher layer.
		'''
		if not all_rooms:
			self._active_instances.sort(key = lambda x : x.layer)
		else:
			# sort again all the list in all rooms
			#  currently used by @active_object to support layer change
			for other_room in self._room_list:
				other_room.active_instances.sort(key = lambda x : x.layer)


	# View method
	def view_new(self, *argv, **kwarg):
		'''Create a new view, store it, and return in
		'''
		
		# get the parent screen from which we derive the new screen
		screen = kwarg.pop('screen', self._screen)

		# to see why we use screen_subwin instead of .subwin, chech the 
		#  documentation of screen_subwin
		new_view = screen_subwin(screen, *argv, **kwarg)
		self.view_add(new_view)
		return new_view

	def view_add(self, view):
		'''Add a given view
		'''

		self._views.append(view)

	def view_remove(self, view):
		'''Remove a given view
		'''
		self._views.remove(view)

	def view_clear(self):
		'''Clear all views and the main screen.

		Note:
		This function may flicker, but does not require to call a refresh
		'''

		self._screen.clear()
		for view in self._views:
			view.clear()

	def view_erase(self):
		'''Clear all views and the main screen.

		Note:
		This function is faster and more stable than view_clear. In most use
		cases should be the preferred choice
		'''

		self._screen.erase()
		for view in self._views:
			view.erase()

	def view_refresh(self):
		'''Refresh all views and the main screen
		'''

		self._screen.refresh()
		for view in self._views:
			view.refresh()


	# background methods
	def background_new(self, *argv, **kwarg):
		'''Create a new background, store it, and return it
		'''
		self._room.background = background(self, *argv, **kwarg)
		self._background = self._room.background

		return self._room.background


	# event methods
	def ev_perform(self, name, *argv, **kwarg):
		for inst in self._active_instances:
			if inst.active and hasattr(inst, name):
				f = getattr(inst, name)
				f(*argv, **kwarg)
