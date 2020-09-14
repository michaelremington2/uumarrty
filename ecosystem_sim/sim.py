#rng = random.Random()
#rng = random.Random(random_seed)
import random
from organismsim import krat 
from organismsim import snake

class Cell(object):
    def __init__(self, time_of_day, habitat_type,krat_energy_cost,snake_energy_cost,krat_energy_gain,cell_energy_pool, initial_snake_pop,initial_krat_pop,rng):
        #cell represents the microhabitat and governs shorter geospatial interactions
        # Order: open, bush
        self.time_of_day = time_of_day
        self.krats = []
        self.snakes = []
        self.habitat_type = habitat_type
        self.krat_energy_cost = krat_energy_cost
        self.snake_energy_cost = snake_energy_cost
        self.krat_energy_gain = krat_energy_gain
        self.cell_energy_pool = cell_energy_pool
        self.rng = rng

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
    def __init__(self,size_of_landscape,krat_energy_cost,snake_energy_cost,krat_energy_gain,cell_energy_pool, initial_snake_pop,initial_krat_pop,rng):
        #landscape is a container for cells and governs movements of critters in cells, and large sclae climate parameters.
        self.cells = []
        self.size_of_landscape = size_of_landscape
        self.krat_energy_cost = krat_energy_cost
        self.snake_energy_cost = snake_energy_cost
        self.krat_energy_gain = krat_energy_gain
        self.cell_energy_pool = cell_energy_pool
        self.rng = rng
        self.gen_cell_list()

    def assign_cell_type(self):
        microclimate_type = self.rng.choice(['open','bush'])
        return microclimate_type

    def add_cell(self,cell):
        self.cells.append(cell)

    def gen_cell_list(self):
        for i in range(size_of_landscape):
            habitat_type = self.assign_cell_type()
            cell = Cell(habitat_type,self.krat_energy_cost,self.snake_energy_cost,self.krat_energy_gain,self.cell_energy_pool, self.initial_snake_pop,self.initial_krat_pop,self.rng)
            self.add_cell(cell)



class.Sim(object):
    #compiles landscape and designates parameters to the landscape. allows landscape to progress through time.
    def __init__(self,size_of_landscape,number_of_days):
        self.end_time = length_of_time_days*24
        self.time_line = range(0,self.end_time)
        self.time_of_day = 0
        self.rng = random.Random()

    def hour_tick(self):
        if self.time_of_day >= 24:
            self.time_of_day = 0
        else:
            self.time_of_day += 1

