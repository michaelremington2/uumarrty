class Organism(object):
	def __init__(self,landscape,energy_counter):
		self.energy_counter = energy_counter
		self.landscape = landscape
		self.rng = landscape.rng

	def consume(self,energy_gain):
		self.energy_counter += energy_gain

	def get_energy_counter(self):
		return self.energy_counter


class Snake(Organism):
	def __init__(self,landscape,energy_counter):
		super().__init__(landscape,energy_counter)
		self.energy_counter = energy_counter
		self.landscape = landscape
		self.rng = landscape.rng

class Krat(Organism):
	def __init__(self,landscape,energy_counter):
		super().__init__(landscape,energy_counter)
		self.energy_counter = energy_counter
		self.landscape = landscape
		self.rng = landscape.rng
