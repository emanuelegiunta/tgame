import curses
import tgame as tg 

@tg.active_object
class debug(object):
	def __init__(self):
		self.timer = 30
		self.x = 0
		self.y = 0

	def ev_step(self):
		self.timer -= 1
		if self.timer == 0:
			assert False, self._c._active_instances

	def ev_draw(self):
		self._s.addstr(self.y, self.x, str(self.timer))

	def ev_key(self, keycodes):
		if ord('\n') in keycodes:
			self.timer *= 2

		if curses.KEY_UP in keycodes:
			self.y -= 1

		if curses.KEY_DOWN in keycodes:
			self.y += 1

		if curses.KEY_LEFT in keycodes:
			self.x -= 1

		if curses.KEY_RIGHT in keycodes:
			self.x += 1

		if ord(" ") in keycodes:
			self._c.room_goto('Second')

@tg.active_object
class skipper(object):
	def ev_draw(self):
		self._s.addstr(5, 5, "second room")

	def ev_key(self, keycodes):
		if ord(" ") in keycodes:
			self._c.room_goto('Main')


def main(ctxt):
	ctxt.room_add('Main')
	ctxt.background_add('home_background')

	view_tl = tg.screen_subwin(ctxt.screen, 0, 0, 10, 40)

	debug(ctxt, screen = view_tl)

	# new room

	ctxt.room_add('Second')

	skipper(ctxt, ctxt.screen)

tg.wrapper(main)