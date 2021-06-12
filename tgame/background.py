import curses

from utilities import screen_size, extension_set, chratt
from constants import BACKGROUND_EXT

# helper function
def _background_from_file(filename, height, width):
	filename = extension_set(filename, BACKGROUND_EXT)

	with open(filename, 'r') as f:
		data = f.read()

	# format data
	if data[-1] == '\n':
		data = data[:-1]

	data = data.split('\n')

	# check that data is a rectangle of the right size by verifing that it has
	# "height" rows each of lenght "width"
	#
	# REMARK - patched the unhelpful message returned if the screen is not of the right size. The function should be more flexible in general
	assert {len(row) for row in data} == {width}, "malformed background file. screen width = {:d}, background width(s) = {}".format(
			width, {len(row) for row in data}
		)
	assert len(data) == height, "malformed background file. screen heigth = {:d}, background heigth = {:d}".format(height, len(data))

	# create the char dictionary
	out = {}

	for y in range(height):
		for x in range(width):
			if data[y][x] != " ":	
				out[y, x] = (data[y][x], curses.A_NORMAL)

	return out

# public function
def background_screenshot(context):
	s = context.screen
	h, w = screen_size(s)
	bkg = {}

	# fill the bkg dictionary with screen characters
	for y in range(h):
		for x in range(w):
			c, a = chratt(s.inch(y, x))

			if c != " ":
				bkg[y, x] = (c, a)

	# return a background
	return background(context, bkg = bkg)

# main class
class background(object):
	def __init__(self, context, bkg = None):
		# bkg can be formatted in several ways:
		#
		#  string -> interpreted as filename
		#
		#  has __getitem__ -> interpreted as a dictionaty of tuples of the form
		#   (y, x) : (c, a) with y,x coordinates, c characted and a attribute
		#
		#  None -> interpreted as an empty dictionary

		self._c = context
		self._s = context.screen
		self._h, self._w = screen_size(self._s)

		if bkg is None:
			self._bkg = {}

		elif type(bkg) == str:
			self._bkg = _background_from_file(bkg, self._h, self._w)

		elif hasattr(bkg, '__getitem__') and hasattr(bkg, '__setitem__'):
			self._bkg = bkg

	def ch_set(self, y, x, c, a = curses.A_NORMAL):
		assert (y >= 0) and (self._h > y), "y coordinate out of boundaries"
		assert (x >= 0) and (self._w > x), "x coordinate out of boundaries"
		self._bkg[y, x] = (c, curses.A_NORMAL)

	def eff_add(self, a):
		'''Change the attribute of all character

		Note:
		Unexpected behaviour! Only the character in the dictionary are changed.
		This means that loading a background from file and then changing the
		attribute (eg. A_REVERSE) only reverse the non-space character of the
		background
		'''

		for key, (bkg_c, bkg_a) in self._bkg.iteritems():
			self._bkg[key] = (bkg_c, bkg_a | a)


	def ch_get(self, y, x):
		assert (y >= 0) and (self._h > y), "y coordinate out of boundaries"
		assert (x >= 0) and (self._w > x), "x coordinate out of boundaries"
		# if y, x is not in the dictionary returns an empty character
		return self._bkg.get((y, x), (" ", curses.A_NORMAL))

	def ch_del(self, y, x):
		assert (y >= 0) and (self._h > y), "y coordinate out of boundaries"
		assert (x >= 0) and (self._w > x), "x coordinate out of boundaries"
		self._bkg.pop((y, x))

	def draw(self):
		for (y, x), (c, a) in self._bkg.iteritems():
			self._s.addch(y, x, c, a)
