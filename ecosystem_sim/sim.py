#rng = random.Random()
#rng = random.Random(random_seed)
import enum
import random
import numpy as np
import csv
from organismsim import Krat
from organismsim import Snake

class Cell(object):
    def __init__(self, sim, habitat_type,krat_energy_cost,snake_energy_cost,krat_energy_gain,cell_energy_pool,cell_id,rng):
        #cell represents the microhabitat and governs shorter geospatial interactions
        # Order: open, bush
        self.sim = sim
        self.krats = []
        self.snakes = []
        self._krat_energy_cost = None
        self._snake_energy_cost = None

        self.habitat_type = habitat_type
        self.landscape = sim.landscape

        self.landscape.energy

        sim.landscape.energy = new lasdmasd

        self.krat_energy_cost = krat_energy_cost
        self.snake_energy_cost = snake_energy_cost
        self.krat_energy_gain = krat_energy_gain
        self.cell_energy_pool = cell_energy_pool
        self.cell_id = cell_id
        self.rng = rng

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
    '''Cells are 10 x 10m'''
    #landscape is a container for cells and governs movements of critters in cells, and large sclae climate parameters.
    #boskilla 1 x 0.8km 80,000 m^2
    #bush (Larrea tridentata) under canopy of creosote up to 10m in diameter Square assumption (10x10m) = 100m^2 circle assumption pi*5^2 = 78.53m^2
    #grass cells (Hilaria rigida) 1 m^2 clump +0.5 m^2 radius
    #grass under or within 50cm of grass
    #bush cover 1.9% (1520m^2), grass 24.1%(19,280m^2), open 74% (59000^2)

    class MicrohabitatType(Enum):
        OPEN = 0.5
        BUSH = 0.5

    def __init__(self,
            sim,
            size_x,
            size_y
            ):
        self.sim = sim
        self.size_x = size_x
        self.size_y = size_y
        self.cells = None
        self.microhabitat_type_proportions = [self.MicrohabitatType.OPEN, self.MicrohabitatType.BUSH]


    def build(self):
        self.cells = []
        for xidx in range(self.size_x):
            self.cells[xidx] = []
            for yidx in range(self.size_y):
                cell = Cell(
                        habitat_type,
                        self.krat_energy_cost,
                        self.snake_energy_cost,
                        self.krat_energy_gain,
                        self.cell_energy_pool,
                        self.initial_snake_pop,
                        self.initial_krat_pop,
                        self.rng)
                self.cells[xidx].append(cell)


    def select_random_cell_type(self):
        microclimate_type = self.rng.choices(['open','bush'],self.open_to_bush_proportion, k = 1)
        return microclimate_type

    def gen_cell_list(self):
        for i in range(self.size_of_landscape):
            habitat_type = self.select_random_cell_type()
            cell = Cell(habitat_type,self.krat_energy_cost,self.snake_energy_cost,self.krat_energy_gain,self.cell_energy_pool, self.initial_snake_pop,self.initial_krat_pop,self.rng)
            self.add_snakes(cell)
            self.add_cell(cell)

    def cell_size(self):
        m = round(self.size_of_landscape[0]/10)
        n = round(self.size_of_landscape[1]/10)
        return (m,n)




class Sim(object):
    #compiles landscape and designates parameters to the landscape. allows landscape to progress through time.

    def __init__(file_path,rng):
        self.time_of_day = 0
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
                microhabitat_type_proportions = config_d["microhabitat_type_proportions"],
                )
        self.landscape.build()
        self.landscape.initialize_snake_pop(
                snake_initial_population_size=config_d["snake_initial_population_size"],
                snake_initial_energy=config_d["snake_initial_energy"],
                )
        self.landscape.initialize_krat_pop(
                krat_initial_population_size=config_d["krat_initial_population_size"],
                krat_initial_energy=config_d["krat_initial_energy"],
                )


    def read_configuration_file(self, filepath):
        config_d = json.read(self.file_path)
        self.configure(config_d)

    def report(self):
        pass

    def sample(self):
        pass





    def __init__(self,csv_file_path):
        self.csv_file_path = csv_file_path
        self.sim_number = 1
        self.time_of_day = 0
        self.set_parameters()
        self.rng = random.Random()
        self.landscape = Landscape(
            size_x=size_x,
            size_y=size_y,
            ...
            )
        self.landscape.build()
        self.add_cells()
        self.add_snakes()
        self.add_krats()

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
        self.strike_success_probability = float(parameters[11])
        self.krat_energy_gain = int(parameters[12])

    def hour_tick(self):
        if self.time_of_day >= 24:
            self.time_of_day = 0
        else:
            self.time_of_day += 1

    def initialize_krat(self,cell_id):
        krat = Krat(energy_counter = self.krat_initial_energy,home_cell_id = cell_id, rng = self.rng)
        return krat

    def initialize_snake(self):
        snake = Snake(energy_counter = self.snake_initial_energy,strike_success_probability = self.strike_success_probability, rng = self.rng)
        return snake

    def initialize_cell(self,cell_id):
        cell = Cell(sim=self, habitat_type = self.landscape.assign_cell_type(),krat_energy_cost = self.krat_energy_cost,snake_energy_cost = self.snake_energy_cost,krat_energy_gain = self.krat_energy_gain,cell_energy_pool = self.cell_energy_pool,cell_id = cell_id,rng = self.rng)
        return cell

    def add_cells(self):
        self.cells_wide = int(round(self.landscape_width/10))
        self.cells_height = int(round(self.landscape_height/10))
        for j in range(self.cells_height):
            x_cells = []
            for i in range(self.cells_wide):
                cell_id = (i,j)
                cell = self.initialize_cell(cell_id)
                x_cells.append(cell)
            self.landscape.cells.append(x_cells)

    def get_random_cell(self):
        row = self.rng.randrange(0,self.cells_height)
        column = self.rng.randrange(0,self.cells_wide)
        temp = self.landscape.cells[row]
        random_cell = temp[column]
        return random_cell

    def add_snakes(self):
        x = self.initial_snake_pop
        while x > 0:
            cell = self.get_random_cell()
            snake = self.initialize_snake()
            cell.add_snake(snake)
            x = x-1

    def add_krats(self):
        y = self.initial_krat_pop
        while y > 0:
            cell = self.get_random_cell()
            krat = self.initialize_krat(cell.cell_id)
            cell.add_krat(krat)
            y = y-1

if __name__ ==  "__main__":
    sim = Sim('simparameters.csv')
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

