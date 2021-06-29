import warnings

from tgame.constants import BASE_LAYER

#==============================================================================#
# Magic Methods
#  __init__
def _set___init__(cls):

	# remark that if cls is instatiated from object it always has a __init__
	#  method
	old___init__ = cls.__init__

	# create the new function to replace the attribute
	def new___init__(self, context, *argv, **kwarg):
		
		# extract the required argument, which are removed as not expected
		#  from the underlying __init__
		screen = kwarg.pop('s', kwarg.pop('screen', context.screen))
		layer = kwarg.pop('l', kwarg.pop('layer', BASE_LAYER))


		# Read and Write variables
		self.visible = True
		self.permanent = False

		# Read and Write through getters/setters variables
		self._layer = layer

		# Read Only variables
		self._c = context
		self._s = screen
		self._active = True
		

		# add the instance to the list of active object
		self._c.instance_add(self)

		# try to run ev_create first. If no implementation for __init__ is
		#  provided then self.__init__ is equal to object.__init__
		if self.__init__ != object.__init__:
			old___init__(self, *argv, **kwarg)

			# having both __init__ and ev_create means that ev_create is no
			#  executed. Therefore we raise a warning
			if hasattr(self, 'ev_create'):
				warnings.warn("__init__ and ev_create are both defined",
					          RuntimeWarning)
		else:
			# try to run ev_create
			if hasattr(self, 'ev_create'):
				self.ev_create(*argv, **kwarg)
	
	# Overload the old __init__ function
	cls.__init__ = new___init__


#==============================================================================#
# Properties
# 	layer
def _set_layer(cls):
	@property
	def layer(self):
		return self._layer

	@layer.setter
	def layer(self, value):
		self._layer = value 
		self._c.layer_update(all_rooms = True)

	cls.layer = layer

# 	active/activate/deactivate
def _set_active(cls):
	# define the getter
	@property
	def active(self):
		return self._active
	
	# define the setter
	@active.setter
	def active(self, value):
		raise TypeError("Assignment to a protected variable")

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

#  c/s
def _set_context(cls):
	@property
	def c(self):
		return self._c 

	@c.setter
	def c(self, value):
		raise TypeError("Assignment to a protected variable")

	cls.c = c

def _set_screen(cls):
	@property
	def s(self):
		return self._s
	
	@s.setter
	def s(self, value):
		raise TypeError("Assignment to a protected variable")

	cls.s = s


#==============================================================================#
# Events
#  destroy
def _set_destroy(cls):
	# we don't check if cls implements destroy
	#  as it is not meant to. Actions relative
	#  to the destruction should be written in
	#  the ev_destroy - called here
	
	def new_destroy(self):
		self._c.instance_remove(self)
		try:
			self.ev_destroy()
		except AttributeError:
			pass

	cls.destroy = new_destroy


#  draw
def _set_ev_draw(cls):
	# only if cls already has a draw event
	if hasattr(cls, 'ev_draw'):

		old_ev_draw = cls.ev_draw

		def new_ev_draw(self):
			if self.visible:
				old_ev_draw(self)

		# set the new method		
		cls.ev_draw = new_ev_draw


#==============================================================================#
# final decorator
def active_object(cls):
	# modify the __init__ method
	_set___init__(cls)

	# add setters/getters for layer
	_set_layer(cls)

	# add activate/deactivate method
	_set_active(cls)
	_set_activate(cls)
	_set_deactivate(cls)

	# context/screen
	_set_context(cls)
	_set_screen(cls)

	# draw event
	_set_ev_draw(cls)

	# add destroy method
	_set_destroy(cls)

	return cls
	
#==============================================================================#