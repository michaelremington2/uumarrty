#rng = random.Random()
#rng = random.Random(random_seed)
from enum import Enum,auto
import random
import numpy as np
import json
from organismsim import Krat
from organismsim import Snake

class Cell(object):
    def __init__(self, sim, habitat_type,krat_energy_cost,snake_energy_cost,krat_energy_gain,cell_energy_pool,cell_id):
        #cell represents the microhabitat and governs shorter geospatial interactions
        # Order: open, bush
        self.sim = sim
        self.krats = []
        self.snakes = []
        self._krat_energy_cost = None
        self._snake_energy_cost = None

        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.krat_energy_cost = krat_energy_cost
        self.snake_energy_cost = snake_energy_cost
        self.krat_energy_gain = krat_energy_gain
        self.cell_energy_pool = cell_energy_pool
        self.cell_id = cell_id
        self.rng = self.sim.rng

    @property
    def krat_energy_cost(self):
        return self._krat_energy_cost
    @krat_energy_cost.setter
    def krat_energy_cost(self, value):
        self._krat_energy_cost = value
    @krat_energy_cost.deleter
    def krat_energy_cost(self):
        self._krat_energy_cost = None

    @property
    def snake_energy_cost(self):
        return self._snake_energy_cost
    @snake_energy_cost.setter
    def snake_energy_cost(self, value):
        self._snake_energy_cost = value
    @snake_energy_cost.deleter
    def snake_energy_cost(self):
        del self._snake_energy_cost

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
            if self.rng < snake.strike_success_probability:
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
    '''Landscape is an object that is composed of Cells are 10m x 10m that range across the x and the y of the landscape.
    landscapes is responsible for generating cells'''
    class MicrohabitatType(Enum):
        OPEN = auto()
        BUSH = auto()

    def __init__(self,sim,size_x,size_y,microhabitat_open_bush_proportions):
        self.sim = sim
        self.size_x = size_x
        self.size_y = size_y
        self.cells = None
        self.cells_x = int(round(self.size_x/10))
        self.cells_y = int(round(self.size_y/10))
        self.microhabitat_open_bush_proportions = microhabitat_open_bush_proportions
        self.rng = self.sim.rng


    def build(self,cell_energy_pool,krat_energy_cost,snake_energy_cost, krat_energy_gain):
        self.cells = []
        for yidx in range(self.cells_y):
            temp_x = []
            for xidx in range(self.cells_x):
                cell_id = (xidx,yidx)
                cell = Cell(
                    sim = self.sim,
                    habitat_type = self.select_random_cell_type(),
                    cell_energy_pool = cell_energy_pool,
                    krat_energy_cost = krat_energy_cost,
                    snake_energy_cost = snake_energy_cost,
                    krat_energy_gain = krat_energy_gain,
                    cell_id = cell_id)
                temp_x.append(cell)
            self.cells.append(temp_x)


    def select_random_cell_type(self):
        microclimate_type = self.rng.choices([self.MicrohabitatType.OPEN,self.MicrohabitatType.BUSH],self.microhabitat_open_bush_proportions, k = 1)
        return microclimate_type

    def get_random_cell(self):
        row = self.sim.rng.randrange(0,self.cells_y)
        column = self.sim.rng.randrange(0,self.cells_x)
        temp = self.cells[row]
        random_cell = temp[column]
        return random_cell

    def initialize_krat(self,sim,energy_counter,cell_id):
        krat = Krat(sim = sim,energy_counter = energy_counter,home_cell_id = cell_id)
        return krat

    def initialize_snake(self,sim,energy_counter,strike_success_probability):
        snake = Snake(sim = sim, energy_counter = energy_counter,strike_success_probability = strike_success_probability)
        return snake

    def initialize_snake_pop(self,initial_snake_pop,snake_initial_energy,strike_success_probability):
        x = initial_snake_pop
        while x > 0:
            cell = self.get_random_cell()
            snake = self.initialize_snake(sim = self.sim,energy_counter = snake_initial_energy,strike_success_probability= strike_success_probability)
            cell.add_snake(snake)
            x = x-1

    def initialize_krat_pop(self,initial_krat_pop,energy_counter):
        y = initial_krat_pop
        while y > 0:
            cell = self.get_random_cell()
            krat = self.initialize_krat(sim = self.sim, energy_counter = energy_counter, cell_id = cell.cell_id)
            cell.add_krat(krat)
            y = y-1




class Sim(object):
    #compiles landscape and designates parameters to the landscape. 
    def __init__(self,file_path,rng = None):
        self.file_path = file_path
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng

    def configure(self, config_d):
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"]
                )
        self.landscape.build(
                cell_energy_pool = config_d["cell_energy_pool"],
                krat_energy_cost = config_d["krat_energy_cost"],
                snake_energy_cost = config_d["snake_energy_cost"],
                krat_energy_gain = config_d["krat_energy_gain"])
        self.landscape.initialize_snake_pop(
                initial_snake_pop=config_d["initial_snake_pop"],
                snake_initial_energy=config_d["snake_initial_energy"],
                strike_success_probability = config_d["strike_success_probability"]
                )
        self.landscape.initialize_krat_pop(
                initial_krat_pop=config_d["initial_krat_pop"],
                energy_counter=config_d["krat_initial_energy"]
                )

    def read_configuration_file(self):
        with open(self.file_path) as f:
            config_d = json.load(f)
        sim1 =config_d['sim'][0]
        self.configure(sim1)

    def hour_tick(self):
        if self.time_of_day >= 24:
            self.time_of_day = 0
        else:
            self.time_of_day += 1

    def report(self):
        cells = sim.landscape.cells
        counter = 0
        print(str(np.shape(cells)))
        for cell_width in cells:
            for cell in cell_width:
                cell_id = '{},{}'.format(cell.cell_id[0],cell.cell_id[1])
                krat_count = str(len(cell.krats))
                snake_count = str(len(cell.snakes))
                prompt = 'iter {}, cell_id {}, krats {}, snakes {}'.format(counter,cell_id,krat_count,snake_count)
                print(prompt)
                counter = counter + 1

    def sample(self):
        pass


if __name__ ==  "__main__":
    sim = Sim('data.txt')
    sim.read_configuration_file()
    sim.report()


