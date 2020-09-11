#rng = random.Random()
#rng = random.Random(random_seed)
import random
from organismsim import krat 
from organismsim import snake

class Cell(object):
	def __init__(self,landscape, habitat_type,krat_energy_cost,snake_energy_cost,krat_energy_gain,strike_success_probability,cell_energy_pool):
		# Order: open, bush
		self.landscape = landscape
		self.sim_time = landscape.sim_time
		self.krats = []
		self.snakes = []
		self.habitat_type = habitat_type
		self.krat_energy_cost = krat_energy_cost
		self.snake_energy_cost = snake_energy_cost
		self.krat_energy_gain = krat_energy_gain
		self.cell_energy_pool = 
		self.rng = landscape.rng

	def add_krat(self, krat):
		# Add a krat to the population of this cells krats
		self.krats.append(krat)

	def add_snake(self, snake):
		# Add a krat to the population of this cells snakes
		self.snakes.append(snake)

	def select_krat(self,krat_id):
		#returns a krat object from this cells population of krat
		return self.krats[krat_id]

	def select_snake(self,snake_id):
		#returns a snake object from this cells population of snakes
		return self.snakes[snake_id]

	def pop_krat(self):
		# Selects a krat at random from population and removes it and return it
		krat_index = self.rng.randint(0,len(self.krats))
		return self.krats.pop(krat_index)

	def pop_snake(self):
		# Selects a snake at random from population and removes it and return it
		for snake in self.snakes
		return self.snakes.pop(snake_index)

	def predation_cycle_snake(self):
		for snake in self.snakes:
			snake.expend_energy(self.snake_energy_cost)
			if self.rng < self.strike_success_probability:
				krat = self.pop_rat() 
				snake.consume(rat)

	def foraging_rat(self):
		for krat in self.krats:
			krat.expend_energy(self.krat_energy_cost)
			krat.gain_energy(self.krat_energy_gain)


class Landscape(object):
	def __init__(self,size_of_landscape,number_of_days):
		self.rng = random.Random()
		self.cells = []
		self.end_time = length_of_time_days*24

	def add_cells(self,cell):
		self.cells.append(cell)


class.Sim(object):
	pass

