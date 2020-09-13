class Organism(object):
	def __init__(self,landscape,energy_counter):
		self.energy_counter = energy_counter
		self.landscape = landscape
		self.alive = True
		self.rng = landscape.rng

	def consume(self,energy_gain):
		self.energy_counter += energy_gain

	def get_energy_counter(self):
		return self.energy_counter

	def expend_energy(self,energy_cost):
		self.energy_counter -= energy_cost

	def natural_death(self):
		if self.energy_counter == 0:
			self.alive = False


class Snake(Organism):
	def __init__(self,landscape,energy_counter):
		super().__init__(landscape,energy_counter)
		self.energy_counter = energy_counter
		self.landscape = landscape
		self.rng = landscape.rng

class Krat(Organism):
	def __init__(self,landscape,energy_counter,home_cell):
		super().__init__(landscape,energy_counter)
		self.energy_counter = energy_counter
		self.landscape = landscape
		self.home_cell = home_cell
		self.foraging = False
		self.rng = landscape.rng
