import curses
from time import sleep

from context import context

def _keycodes_get(screen):
	keycode_vec = []

	while True:
		keycode = screen.getch()

		if keycode != -1:
			keycode_vec.append(keycode)
		else:
			break

	return keycode_vec

def wrapper(func = None):

	def _main(screen):
		# Curses setting
		curses.curs_set(False)
		curses.use_default_colors()

		# To aviod printing in the bottom right corner
		y, x = screen.getmaxyx()
		screen.resize(y + 1, x)
		
		# Screen settings
		screen.clear()
		screen.nodelay(True)
		
		# Create the context
		ctxt = context(screen)

		# Execute, if given, the main function
		if func is not None:
			func(ctxt)

		# Starts the main loop
		while(True):

			# Executes the events in order:
			ctxt.ev_perform('ev_step_begin')
			ctxt.ev_perform('ev_key', _keycodes_get(screen))
			ctxt.ev_perform('ev_step')

			ctxt.view_erase()
			ctxt.background.draw()
			ctxt.ev_perform('ev_draw')
			ctxt.ev_perform('ev_step_end')

			# End of step. Notice that sleep should be done in another thread
			ctxt.view_refresh()
			sleep(1.0/ctxt.speed)
			

	curses.wrapper(_main)