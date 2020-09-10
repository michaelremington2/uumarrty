import random
class Cell(object):
	def __init__(self,landscape, habitat_type,rat_energy_cost,snake_energy_cost,rat_energy_gain,strike_success_probability):
		# Order: open, bush
		self.landscape = landscape
		self.sim_time = landscape.sim_time
		self.rats = []
		self.snakes = []
		self.habitat_type = habitat_type
		self.rat_energy_cost = rat_energy_cost
		self.snake_energy_cost = snake_energy_cost
		self.rat_energy_gain = rat_energy_gain
		self.rng = landscape.rng

	def add_rat(self, rat):
		# Add a rat to the population of this cells rats
		pass

	def add_snake(self, snake):
		# Add a rat to the population of this cells snakes
		pass

	def select_rat(self):
		#returns a rat object from this cells population of rat
		pass

	def select_snake(self):
		#returns a snake object from this cells population of rat
		pass

	def pop_rat(self):
		# Selects a rat at random from population and removes it and return it
		rat_index = random.randint(0,len(self.rats)-1)
		return self.rats.pop(rat_index)

	def pop_snake(self):
		# Selects a snake at random from population and removes it and return it
		snake_index = self.rng.randint(0,len(self.snakes)-1)
		return self.snakes.pop(snake_index)

	def predation_cycle_snake(self):
		for snake in self.snakes:
			snake.expend_energy(self.snake_energy_cost)
			if self.rng < self.strike_success_probability:
				rat = self.pop_rat() 
				snake.consume(rat)

	def foraging_rat(self):
		for rat in self.rats:
			rat.expend_energy(self.rat_energy_cost)
			rat.gain_energy(self.rat_energy_gain)


class Landscape(object):
	pass

class.Sim(object):
	pass

