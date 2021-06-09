# We need a dictionary-like class that makes
#  a[key] returns the value if present or 0
#  if not present
class _timer_tdict(dict):
	def __getitem__(self, key):
		if self.has_key(key):
			return dict.__getitem__(self, key)
		else:
			return -1


# __init__
def _set___init__(cls):

	# all *_object has __init__
	#
	old___init__ = cls.__init__

	def new___init__(self, *argv, **kwarg):

		# Read Only variable 
		self._timer = _timer_tdict()

		# run the old init
		old___init__(self, *argv, **kwarg)

	# add the new init
	cls.__init__ = new___init__

def _set_timer(cls):

	@property
	def timer(self):
		return self._timer
	
	@timer.setter 
	def timer(self, value):
		raise ValueError, "Assignment to a protected variable"

	cls.timer = timer

# ev_step_begin
def _set_ev_step_begin(cls):

	flg_ev_step_begin = False

	if hasattr(cls, 'ev_step_begin'):
		flg_ev_step_begin = True
		old_ev_step_begin = cls.ev_step_begin

	def new_ev_step_begin(self):

		# update all the currently active allarms
		_recicle_bin = []
		for (_key, _time) in self._timer.iteritems():
			if _time == 0:
				_recicle_bin.append(_key)
			else:
				self._timer[_key] -= 1

		for _key in _recicle_bin:
			self._timer.pop(_key)

		# execute the old event
		if flg_ev_step_begin:
			old_ev_step_begin(self)

	# add the new method
	cls.ev_step_begin = new_ev_step_begin


def timer(cls):
	#
	# add __init__
	_set___init__(cls)
	_set_timer(cls)

	# add ev_step_begin
	_set_ev_step_begin(cls)


	return cls