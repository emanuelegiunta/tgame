import curses


# screen functions
def screen_size(screen):
	''' Return the size of the screen
	
	Input:
	screen: curses.window object

	Output (h, w):
	h: height of the given window
	w: width of the given window

	Note:
	The ouput does not return the actual size of the window but the usable size
	The difference begin that the actual window size, returned by getmaxyx(),
	has the bottom right corner issue - i.e. addch(h-1, w-1, <char>) does not return errors
	'''
	
	h, w = screen.getmaxyx()
	h -= 1
	return (h, w)

def screen_subwin(screen, y, x, h, w):
	''' Return a subview of the given screen

	Input:
	screen: the main screen from which the subview is derived
	y, x: coordinate of the top left corner of the new view
	h, w: height and width of the new view

	Output:
	A view of the specified size.

	Note:
	the view returned is actually higher by one caracter. This is required to
	address with minimal discomfort the bottom right issue, i.e. using
	screen.addch(h, w, *argv) will cause an error.
	'''

	# for easier debug check if the screen fit

	try:	
		return screen.subwin(h + 1, w, y, x)
	except:
		# guess what the cause of the error was
		screen_h, screen_w = screen_size(screen)
		if not x + w <= screen_w:
			raise ValueError, "New view's width exceed parent view's width"
		elif not y + h <= screen_h:
			raise ValueError, "New view's heigth exceed parent view's heigth"

		# if the guessing is not right, give up
		else:
			raise


# file functions
def extension_get(filename):
	'''Return the extension of a file
	
	Input:
	filename: name of the file analysed

	Output:
	the file extension or None if the file has no extension
	'''
	if '.' not in filename:
		return None
	else:
		return filename.split('.')[-1]

def extension_set(filename, extension):
	'''Set the extension of a file

	Input:
	filename: name of the input file
	extension: the extension to set in filename (dot excluded)

	Ouput:
	the new filename of the form "prefix.extension"

	None:
	If the given filename has no extension, i.e. is not in the form
	"prefix.suffix", where suffix does not contains '.', the output is
	"filename.extension"
	'''

	if '.' not in filename:
		return filename + '.' + extension
	else:
		# look for the last dot
		for i in range(-1, -len(filename)-1, -1):
			if filename[i] == '.':
				break

		# return the result
		return filename[:i] + '.' + extension


# draw functions
def draw_canvas(screen, x, y, w, h, **kwarg):
	''' Draw a canvas on a given screen

	Input:
	screen: curses.window object
	x: first coordinate of the top-left corner of the canvas
	y: second coordinate of the top-left corner of the canvas
	n: width of the canvas - including sides
	m: heigth of the canvas - including sides

	Note:
	draw a 1-char width rectangle of side length [n] and [m] respectively.
	Setting [n] or [m] smaller than 2 raises an error
	'''

	c = kwarg.pop('c', kwarg.pop('character', ' '))
	a = kwarg.pop('a', kwarg.pop('attribute', curses.A_NORMAL))

	# draw upper and lower border
	screen.addstr(y, x, c*w, a)
	screen.addstr(y + h - 1, x, c*w, a)

	# draw the columns
	for i in range(1, h - 1):
		screen.addch(y + i, x, c, a)
		screen.addch(y + i, x + w - 1, c, a)

def draw_rectangle(screen, x, y, w, h, **kwarg):
	'''draw a rectangle of given size

	INPUT:
	x, y = top left coordinate of the rectangle
	w, h = width and heigth of the rectangle
	[c, character] = character used to fill the rectangle
	[a, attribute] = attribute used to fill the rectangle
	'''

	c = kwarg.pop('c', kwarg.pop('character', ' '))
	a = kwarg.pop('c', kwarg.pop('attribute', curses.A_NORMAL))

	for i in range(h):
		screen.addstr(y + i, x, c*w, a)

# miscellaneous functions
def chratt(data):
	'''Helper for curses.inch()

	Input:
	data: an integer containing information about printed char with attributes

	Output: (ch, att):
	ch: character contained in data
	att: attribute of the contained in data

	Note:
	data has to follow curses formatting conventions. tipical use case is
	ch, att = chratt(curses.inch(y, x))
	'''

	ch = chr(data % (1 << 8))
	att = data - (data % (1 << 8))
	return ch, att
