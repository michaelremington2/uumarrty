#rng = random.Random()
#rng = random.Random(random_seed)
import random
import csv
from organismsim import Krat 
from organismsim import Snake

class Cell(object):
    def __init__(self, time_of_day, habitat_type,krat_energy_cost,snake_energy_cost,krat_energy_gain,cell_energy_pool,rng):
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

    def select_krat(self,krat_index = None):
        #returns a random index for the krat
        if krat_index == None:
            krat_index = self.rng.randint(0,len(self.krats))
        krat = self.krats[krat_index]
        return krat

    def select_snake(self,snake_index = None):
        #returns a snake object from this cells population of snakes
        if snake_index == None:
            snake_index = self.rng.randint(0,len(self.snake))
        snake = self.snakes[snake_index]
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
                krat = self.select_krat()
                snake.consume(krat)
                self.pop_krat() 
                
    def foraging_rat(self):
        for krat in self.krats:
            if krat.foraging == True:
                krat.expend_energy(self.krat_energy_cost)
                krat.gain_energy(self.krat_energy_gain)
                self.cell_forage(self.krat_energy_gain)


class Landscape(object):
    def __init__(self,size_of_landscape,cell_energy_pool,rng,open_to_bush_proportion = [0.5,0.5]):
        '''Cells are 10 x 10m'''
        #landscape is a container for cells and governs movements of critters in cells, and large sclae climate parameters.
        #boskilla 1 x 0.8km 80,000 m^2
        #bush (Larrea tridentata) under canopy of creosote up to 10m in diameter Square assumption (10x10m) = 100m^2 circle assumption pi*5^2 = 78.53m^2
        #grass cells (Hilaria rigida) 1 m^2 clump +0.5 m^2 radius
        #grass under or within 50cm of grass
        #bush cover 1.9% (1520m^2), grass 24.1%(19,280m^2), open 74% (59000^2)
        self.cells = []
        self.size_of_landscape = size_of_landscape # tuple of width and height
        self.open_to_bush_proportion = open_to_bush_proportion
        self.rng = rng
        self.gen_cell_list()

    def assign_cell_type(self):
        microclimate_type = self.rng.choices(['open','bush'],self.open_to_bush_proportion, k = 1)
        return microclimate_type

    def add_cell(self,cell):
        self.cells.append(cell)

    def gen_cell_list(self):
        for i in range(size_of_landscape):
            habitat_type = self.assign_cell_type()
            cell = Cell(habitat_type,self.krat_energy_cost,self.snake_energy_cost,self.krat_energy_gain,self.cell_energy_pool, self.initial_snake_pop,self.initial_krat_pop,self.rng)
            self.add_snakes(cell)
            self.add_cell(cell)

    def cell_size(self):
        m = round(self.size_of_landscape[0]/10)
        n = round(self.size_of_landscape[1]/10)
        return (m,n)




class Sim(object):
    #compiles landscape and designates parameters to the landscape. allows landscape to progress through time.
    def __init__(self,csv_file_path):
        self.csv_file_path = csv_file_path
        self.sim_number = 1
        self.time_of_day = 0
        self.set_parameters()
        self.rng = random.Random()
        self.landscape_dimensions = [self.landscape_width,self.landscape_height]
        self.landscape = Landscape(self.landscape_dimensions,self.cell_energy_pool,self.rng)

    def open_file(self):
        '''Enter the general file name. This command opens the file then appends the data to a list.'''
        with open(self.csv_file_path, 'r') as sim_file:
            sim_parameters= []
            for row in csv.reader(sim_file):
                sim_parameters.append(row)
            self.number_of_sims = len(sim_parameters)- 1
            return sim_parameters

    def unpack_parameters(self,sim_number):
        sim_parameters = self.open_file()
        if self.number_of_sims == 0:
            RaiseValueError('Input sim parameters')
        return sim_parameters[sim_number]

    def set_parameters(self):
        parameters = self.unpack_parameters(1)
        self.end_time = int(parameters[1])*24
        self.time_line = range(0,self.end_time)
        self.landscape_width = int(parameters[2])
        self.landscape_height = int(parameters[3])
        self.initial_snake_pop = int(parameters[4])
        self.initial_krat_pop = int(parameters[5])
        self.cell_energy_pool = int(parameters[6])
        self.snake_initial_energy = int(parameters[7])
        self.krat_initial_energy = int(parameters[8])
        self.snake_energy_cost = int(parameters[9])
        self.krat_energy_cost = int(parameters[10])
        self.snake_strike_success_probability = float(parameters[11])
        self.krat_energy_gain = int(parameters[12])

    def hour_tick(self):
        if self.time_of_day >= 24:
            self.time_of_day = 0
        else:
            self.time_of_day += 1

    def add_snakes(self,cell):
        for i in range(self.initial_snake_pop):
            snake = Snake(energy_counter = self.snake_initial_energy,strike_success_probability = self.snake_strike_success_probability, rng = self.rng)
            cell.add_snake(snake)

    def add_krats(self,cell):
        for i in range(self.initial_snake_pop):
            krat = Krat(energy_counter = self.krat_initial_energy,home_cell = cell, rng = self.rng)
            cell.add_krat(krat)

    def initialize_cell(self):
        pass

    def initialize_landscape(self):
        pass

if __name__ ==  "__main__":
    sim = Sim('simparameters.csv')
    print(sim.end_time)

