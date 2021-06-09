import curses

BACKGROUND_EXT = "bkg"

CONTEXT_SPEED = 30

KEY_ENTER = 10

BASE_LAYER = 0

# SKIP and OFFSET are used assuming the least
#  in this way users are "forced" to set the right default value
MENU_XSKIP = 1		#
MENU_YSKIP = 1		#
MENU_XOFFSET = 0	#
MENU_YOFFSET = 0	#
MENU_ALIGN = 'l'
MENU_KEY_UP = curses.KEY_UP
MENU_KEY_DOWN = curses.KEY_DOWN
MENU_KEY_LEFT = curses.KEY_LEFT
MENU_KEY_RIGHT = curses.KEY_RIGHT
MENU_KEY_ENTER = ord('\n')
MENU_ATTRIBUTE_ON = curses.A_REVERSE
MENU_ATTRIBUTE_OFF = curses.A_NORMAL

MENU_ACTION_PREFIXES = ['opt', 'Opt', 'option', 'Option', 'opt_', 'Opt_',\
	                    'option_', 'Option_']