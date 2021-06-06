import warnings

# __init__
def _set___init__(cls):

	# remark that if cls is instatiated from object it always has a __init__
	#  method
	old___init__ = cls.__init__

	# create the new function to replace the attribute
	def new___init__(self, context, *argv, screen = None, **kwargv):		
		if screen == None:
			screen = context.screen

		self._c = context
		self._s = screen

		self._active = True

		# add the instance to the list of active object
		self._c.instance_add(self)

		# try to run ev_create first. If no implementation for __init__ is
		#  provided then self.__init__ is equal to object.__init__
		if self.__init__ != object.__init__:
			old___init__(self, *argv, **kwargv)

			# having both __init__ and ev_create means that ev_create is no
			#  executed. Therefore we raise a warning
			if hasattr(self, 'ev_create'):
				warnings.warn("__init__ and ev_create are both defined",
					          RuntimeWarning)
		else:
			# try to run ev_create
			if hasattr(self, 'ev_create'):
				self.ev_create(*argv, **kwargv)
		
	cls.__init__ = new___init__

# active/activate/deactivate
def _set_active(cls):

	# add the attribute
	cls._active = True

	# define the getter
	@property
	def active(self):
		return self._active
	
	# define the setter
	@active.setter
	def active(self):
		raise TypeError, "Assignment to a protected variable"

	cls.active = active

def _set_activate(cls):

	# activate method to be added
	def new_activate(self):
		self._active = True

	# add the methods
	cls.activate = new_activate

def _set_deactivate(cls):

	# deactivate method to be added
	def new_deactivate(self):
		self._active = False

	# add the methods
	cls.deactivate = new_deactivate

# destroy
def _set_destroy(cls):
	# we don't check if cls implements destroy
	#  as it is not meant to. Actions relative
	#  to the destruction should be written in
	#  the ev_destroy - called here
	
	def new_destroy(self):
		self.c.instance_remove(self)
		try:
			self.ev_destroy()
		except AttributeError:
			pass

	cls.destroy = new_destroy


# decorator
def active_object(cls):
	# modify the __init__ method
	_set___init__(cls)

	# add activate/deactivate method
	_set_active(cls)
	_set_activate(cls)
	_set_deactivate(cls)

	# add destroy method
	_set_destroy(cls)

	return cls