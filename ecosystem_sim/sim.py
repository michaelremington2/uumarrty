#!/usr/bin/python

from enum import Enum,auto
import random
import numpy as np
import json
from organismsim import Krat
from organismsim import Snake
from organismsim import Movement

class Cell(object):
    def __init__(self, sim, habitat_type,krat_energy_cost,snake_energy_cost,cell_energy_pool,cell_id):
        #cell represents the microhabitat and governs shorter geospatial interactions
        # Order: open, bush
        self.sim = sim
        self.krats = []
        self.snakes = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.krat_energy_cost = krat_energy_cost
        self.snake_energy_cost = snake_energy_cost
        self.cell_energy_pool = cell_energy_pool
        self.cell_id = cell_id
        self.rng = self.sim.rng

    def add_krat(self, krat):
        # Add a krat to the population of this cells krats
        self.krats.append(krat)

    def add_snake(self, snake):
        # Add a krat to the population of this cells snakes
        self.snakes.append(snake)

    def select_krat(self,krat_index = None):
        #returns a random index for the krat
        if krat_index == None:
            krat_index = self.rng.randint(0,len(self.krats)-1)
        krat = self.krats[krat_index]
        return krat

    def select_snake(self,snake_index = None):
        #returns a snake object from this cells population of snakes
        if snake_index == None:
            snake_index = self.rng.randint(0,len(self.snake)-1)
        snake = self.snakes[snake_index]
        return snake

    def pop_krat(self,krat_index):
        # Selects a krat at random from population and removes it and return it
        return self.krats.pop(krat_index)

    def pop_snake(self,snake_index):
        # Selects a snake at random from population and removes it and return it
        return self.snakes.pop(snake_index)

    def cell_forage(self,energy_consumed):
        #if energy_consumed != None:
        self.cell_energy_pool -= energy_consumed

    def krat_move(self):
        for krat in self.krats:
            new_cell_id = krat.organism_movement()
            if new_cell_id != self.cell_id:
                moving_krat = (new_cell_id,krat,self.cell_id)
                self.landscape.krat_move_pool.append(moving_krat)
                self.pop_krat(self.krats.index(krat))

    def snake_move(self):
        for snake in self.snakes:
            new_cell_id = snake.organism_movement()
            if new_cell_id != self.cell_id:
                moving_snake = (new_cell_id,snake)
                self.landscape.snake_move_pool.append(moving_snake)
                self.pop_snake(self.snakes.index(snake))

    def krat_grave(self,krat):
        if krat.alive == False:
            self.pop_krat(self.krats.index(krat))

    def snake_grave(self,snake):
        if snake.alive == False:
            self.pop_krat(self.krats.index(snake))

    def predation_cycle_snake(self):
        for snake in self.snakes:
            snake.hunting_period()
            if self.rng.random() < snake.strike_success_probability and len(self.krats) > 0:
                #print('successful_strike!')
                snake.expend_energy(self.snake_energy_cost)
                krat = self.select_krat()
                snake.consume(krat.energy_counter)
                self.pop_krat(self.krats.index(krat))
            self.snake_grave(snake)

    def foraging_rat(self):
        for krat in self.krats:
            krat.foraging_period()
            krat.expend_energy(self.krat_energy_cost)
            if krat.foraging == True and krat.alive == True:
                krat_energy_gain = krat.energy_gain(self.cell_energy_pool)
                if self.cell_energy_pool > 0:
                    krat.forage(krat_energy_gain)
                    self.cell_forage(krat_energy_gain)
            self.krat_grave(krat)


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
        self.cells_x_columns = int(round(self.size_x/10))
        self.cells_y_rows = int(round(self.size_y/10))
        self.microhabitat_open_bush_proportions = microhabitat_open_bush_proportions
        self.krat_move_pool = []
        self.snake_move_pool = []
        self.rng = self.sim.rng


    def build(self,cell_energy_pool,krat_energy_cost,snake_energy_cost):
        self.cells = []
        for yidx in range(self.cells_y_rows):
            temp_x = []
            for xidx in range(self.cells_x_columns):
                cell_id = (yidx,xidx)
                cell = Cell(
                    sim = self.sim,
                    habitat_type = self.select_random_cell_type(),
                    cell_energy_pool = cell_energy_pool,
                    krat_energy_cost = krat_energy_cost,
                    snake_energy_cost = snake_energy_cost,
                    cell_id = cell_id)
                temp_x.append(cell)
            self.cells.append(temp_x)


    def select_random_cell_type(self):
        microclimate_type = self.rng.choices([self.MicrohabitatType.OPEN,self.MicrohabitatType.BUSH],self.microhabitat_open_bush_proportions, k = 1)
        return microclimate_type

    def select_random_cell(self):
        row = self.rng.randrange(0,self.cells_y_rows)
        column = self.rng.randrange(0,self.cells_x_columns)
        temp = self.cells[row]
        random_cell = temp[column]
        return random_cell

    def select_cell(self,cell_id):
        row = cell_id[0]
        column = cell_id[1]
        temp = self.cells[row]
        cell = temp[column]
        return cell

    def initialize_krat(self,sim,energy_counter,cell_id,foraging_rate):
        krat = Krat(sim = sim,energy_counter = energy_counter,home_cell_id = cell_id,foraging_rate = foraging_rate)
        return krat

    def initialize_snake(self,sim,energy_counter,strike_success_probability):
        snake = Snake(sim = sim,
         energy_counter = energy_counter,
         strike_success_probability = strike_success_probability)
        return snake

    def initialize_snake_pop(self,initial_snake_pop,snake_initial_energy,strike_success_probability):
        x = initial_snake_pop
        while x > 0:
            cell = self.select_random_cell()
            snake = self.initialize_snake(sim = self.sim,energy_counter = snake_initial_energy,strike_success_probability= strike_success_probability)
            cell.add_snake(snake)
            snake.current_cell(cell.cell_id)
            x = x-1

    def initialize_krat_pop(self,initial_krat_pop,energy_counter,foraging_rate):
        y = initial_krat_pop
        while y > 0:
            cell = self.select_random_cell()
            krat = self.initialize_krat(sim = self.sim,
                                        energy_counter = energy_counter,
                                        cell_id = cell.cell_id, 
                                        foraging_rate = foraging_rate)
            cell.add_krat(krat)
            krat.current_cell(cell.cell_id)
            y = y-1

    def relocate_krats(self):
        for i, krat in enumerate(self.krat_move_pool):
            new_cell_id = krat[0]
            krat_object = krat[1]
            new_cell = self.select_cell(new_cell_id)
            new_cell.add_krat(krat_object)
            krat_object.current_cell(new_cell_id)
        self.krat_move_pool = []

    def relocate_snakes(self):
        for j, snake in enumerate(self.snake_move_pool):
            new_cell_id = snake[0]
            snake_object = snake[1]
            new_cell = self.select_cell(new_cell_id)
            new_cell.add_snake(snake_object)
            snake_object.current_cell(new_cell_id)
        self.snake_move_pool = []

    def landscape_stats(self,cell):
        cell_krat_energy = sum([krat.energy_counter for krat in cell.krats])
        cell_snake_energy = sum([snake.energy_counter for snake in cell.snakes])
        data = [sim.time,sim.time_of_day,cell.cell_id,cell.cell_energy_pool,len(cell.krats),cell_krat_energy,len(cell.snakes),cell_snake_energy ]
        sim.report.append(data)

    def landscape_dynamics(self):
        for cell_width in self.cells:
            for cell in cell_width:
                cell.predation_cycle_snake()
                cell.foraging_rat()
                self.landscape_stats(cell)
                cell.snake_move()
                cell.krat_move()
        self.relocate_krats()
        self.relocate_snakes()
        #print(len(self.krat_move_pool))


class Sim(object):
    #compiles landscape and designates parameters to the landscape. 
    def __init__(self,file_path,rng = None):
        self.file_path = file_path
        self.report = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng

    def configure(self, config_d):
        self.end_time = 24 #config_d["days_of_sim"]*24
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"]
                )
        self.landscape.build(
                cell_energy_pool = config_d["cell_energy_pool"],
                krat_energy_cost = config_d["krat_energy_cost"],
                snake_energy_cost = config_d["snake_energy_cost"])
        self.landscape.initialize_snake_pop(
                initial_snake_pop=config_d["initial_snake_pop"],
                snake_initial_energy=config_d["snake_initial_energy"],
                strike_success_probability = config_d["strike_success_probability"]
                )
        self.landscape.initialize_krat_pop(
                initial_krat_pop=config_d["initial_krat_pop"],
                energy_counter=config_d["krat_initial_energy"],
                foraging_rate = float(config_d["krat_energy_gain"])
                )

    def read_configuration_file(self):
        with open(self.file_path) as f:
            config_d = json.load(f)
        sim1 =config_d['sim'][0]
        self.configure(sim1)

    def hour_tick(self):
        if self.time_of_day >= 23:
            self.time_of_day = 0
        else:
            self.time_of_day += 1

    def main(self):
        self.time = 0
        self.time_of_day = 0
        self.read_configuration_file()
        for i in range(self.end_time):
            self.landscape.landscape_dynamics()
            self.hour_tick()
            self.time += 1
        self.report_writer(array = self.report,file_name = 'Cell_stats_sim_1.csv')

    def test(self):
        self.read_configuration_file()
        cells = self.landscape.cells
        for cell_width in cells:
            for cell in cell_width:
                cell_id = '{},{}'.format(cell.cell_id[0],cell.cell_id[1])
                #print(cell_id)
        

    def report_writer(self,array,file_name):
        import csv
        with open(file_name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(array)





if __name__ ==  "__main__":
    sim = Sim('data.txt')
    sim.main()
    #sim.read_configuration_file()
    #move = Movement(sim)
    #cell = (5,6)
    #new_cell = move.new_cell(cell,weight = 1.5)
    #print(new_cell)



