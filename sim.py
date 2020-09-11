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
		self.cell_energy_pool = cell_energy_pool
		self.rng = landscape.rng

	def add_krat(self, krat):
		# Add a krat to the population of this cells krats
		self.krats.append(krat)

	def add_snake(self, snake):
		# Add a krat to the population of this cells snakes
		self.snakes.append(snake)

	def select_krat(self):
		#returns a krat object from this cells population of krat
		krat_index = self.rng.randint(0,len(self.krats))
		return krat_index

	def select_snake(self,snake_id):
		#returns a snake object from this cells population of snakes
		snake_index = self.rng.randint(0,len(self.snake))
		return snake_index

	def pop_krat(self,krat_index):
		# Selects a krat at random from population and removes it and return it
		return self.krats.pop(krat_index)

	def pop_snake(self,snake_index):
		# Selects a snake at random from population and removes it and return it
		return self.snakes.pop(snake_index)

	def cell_forage(self,energy_consumed):
		self.self.cell_energy_pool -= energy_consumed

	def predation_cycle_snake(self):
		for snake in self.snakes:
			snake.expend_energy(self.snake_energy_cost)
			if self.rng < self.strike_success_probability:
				krat_index = self.select_krat()
				krat = self.krats[krat_index]
				snake.consume(krat)
				self.pop_krat() 
				
	def foraging_rat(self):
		for krat in self.krats:
			if krat.foraging == True:
				krat.expend_energy(self.krat_energy_cost)
				krat.gain_energy(self.krat_energy_gain)
				self.cell_forage(self.krat_energy_gain)


class Landscape(object):
	def __init__(self,size_of_landscape,number_of_days):
		self.rng = random.Random()
		self.cells = []
		self.end_time = length_of_time_days*24
		self.time_line = range(0,time_line)

	def add_cells(self,cell):
		self.cells.append(cell)


class.Sim(object):
	pass

