from background import background

class room:
	def __init__(self, context, active_instances = None, views = None, bkg = None):
		
		# resolve None input
		if bkg is None:
			bkg = background(context, None)

		if active_instances is None:
			active_instances = []

		if views is None:
			views = []

		# public variables
		self.active_instances = active_instances
		self.new_instances = []
		self.views = views
		self.background = bkg
		
		