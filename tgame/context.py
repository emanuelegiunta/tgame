import curses

from room import room
from constants import CONTEXT_SPEED
from background import background

class context(object):
	def __init__(self, screen):
		# public variables
		self.speed = CONTEXT_SPEED

		# read only variables
		self._background = None
		self._screen = screen
		
		# private variables
		self._views = []
		self._active_instances = []
		self._room_dict = {}
		self._room_list = []
		self._room = None
		self._room_last_visited = None
 
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
		self.background = self._room.background
	
	# room methods
	def room_add(self, name, *argv, **kwarg):
		'''Add a new room and move into the new room
		'''

		assert (not self._room_dict.has_key(name)), "Room id already used"

		# create and store the new room
		new_room = room(self, *argv, **kwarg)
		self._room_dict[name] = new_room
		self._room_list.append(new_room)

		# move into the new room
		self._room_change(new_room, ev_perform = False)
 
	def room_goto(self, name, ev_perform = True):
		assert (self._room_dict.has_key(name)), "Moving to non-existing room"

		# retrieve the given room and move
		next_room = self._room_dict[name]
		self._room_change(next_room, ev_perform)

	def room_precedent(self, ev_perform = True):
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
		self._room_change(next_room, ev_perform)

	def room_next(self, ev_perform = True):
		# throw an error if there is no room at all
		assert self._room is not None, "There is no room in the game"
		
		i = self._room_list.index(self._room)

		# throw an error if this is the last room
		assert len(self._room_list) > (i + 1), "Reached last room"

		next_room = self._room_list[(i + 1)]
		self._room_change(next_room, ev_perform)

	def room_previous(self, ev_perform = True):
		# throw an error if there is no room at all
		assert self._room is not None, "There is no room in the game"

		i = self._room_list.index(self._room)

		# throw an error if this is the first room
		assert i > 0, "Reached first room"

		next_room = self._room_list[(i - 1)]
		self._room_change(next_room, ev_perform)

	def _room_change(self, next_room, ev_perform):
		self.view_clear()
		self._room_last_visited = self._room
		self._room = next_room

		# change the list of active objects, views and background
		self._active_instances = next_room.active_instances
		self._views = next_room.views
		self._background = next_room.background
		
		# perform the room start event
		if ev_perform:
			self._room_start_ev()

	# Instance methods
	def instance_add(self, inst):
		#
		self._active_instances.append(inst)

	def instance_remove(self, inst):
		#
		self._active_instances.remove(inst)
	
	def instance_of(self, *filters):

		# stirng are interpreted as "the of inst's class is the given string"
		for i in len(filters):
			if type(filters[i]) == str:
				filters[i] = lambda inst : \
							     inst.__class__.__name__ == filters[i]

		# concatenate all the filters in one function
		def f(inst):
			for g in filters:
				if not g(inst):
					return False

			return True

		# filtering instance name
		return filter(f, self._active_instances)

	def instance_all(self, *but):

		# stirng are interpreted as "the of inst's class is the given string"
		for i in len(but):
			if type(filters[i]) == str:
				but[i] = lambda inst : inst.__class__.__name__ == but[i]

		# concatenate all the filters in one function
		def f(inst):
			for g in but:
				if g(inst):
					return False

			return True

		# filtering instance name
		return filter(f, self._active_instances)


	# View method
	def view_add(self, view):
		#
		self._views.append(view)

	def view_remove(self, view):
		#
		self._views.remove(view)

	def view_clear(self):
		self._screen.clear()
		for view in self._views:
			view.clear()

	def view_erase(self):
		self._screen.erase()
		for view in self._views:
			view.erase()

	def view_refresh(self):
		# refresh the main view
		self._screen.refresh()
		# refresh the views of the current room
		for view in self._views:
			view.refresh()


	# background methods
	def background_add(self, *argv, **kwarg):
		self._room.background = background(self, *argv, **kwarg)
		self._background = self._room.background


	# event methods
	def ev_perform(self, name, *argv, **kwarg):
		for inst in self._active_instances:
			if inst.active:
				
				try:
					f = getattr(inst, name)
					f(*argv, **kwarg)
				except AttributeError:
					pass

					