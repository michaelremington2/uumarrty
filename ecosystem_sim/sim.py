#!/usr/bin/python
from enum import Enum,auto
import random
import numpy as np
import json
from organismsim import Krat
from organismsim import Snake
from organismsim import Owl
import math
import time
#look up contact rates based on spatial scale and tempor
#brownian motion 

class Cell(object):
    def __init__(self, sim, habitat_type,krat_energy_cost,snake_energy_cost,cell_energy_pool,cell_id):
        #cell represents the microhabitat and governs shorter geospatial interactions
        # Order: open, bush
        self.sim = sim
        self.krats = []
        self.snakes = []
        self.owls = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.krat_energy_cost = krat_energy_cost
        self.snake_energy_cost = snake_energy_cost
        self.cell_energy_pool = cell_energy_pool
        self.cell_id = cell_id
        self.krat_incubation_list = []
        self.snake_incubation_list = []      
        self.rng = self.sim.rng

    def __hash__(self):
        return id(self)

    def add_krat(self, krat):
        # Add a krat to the population of this cells krats
        self.krats.append(krat)

    def add_snake(self, snake):
        # Add a snake to the population of this cells snakes
        self.snakes.append(snake)

    def add_owl(self,owl):
        self.owls.append(owl)

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
        self.cell_energy_pool -= energy_consumed

    def cell_over_populated(self):
        if len(self.krats) > 50:
            raise ValueError("Krats mating too much")
        if len(self.snakes) > 20:
            raise ValueError("snakes mating too much")

    def other_critter_predation(self,snake):
        probability_of_encounter = (self.sim.time_step)/len(snake.hunting_hours) #assumption
        if self.rng.random() < probability_of_encounter:
            snake.expend_energy(self.snake_energy_cost)
            if self.rng.random() < snake.strike_success_probability:
                mouse_energy = self.rng.randrange(20,30)
                snake.consume(mouse_energy)
            else:
                snake.missed_opportunity_cost+=1

    def krat_move(self, krat,moving_krat_list,return_home=False):
        if return_home== True:
            new_cell = krat.return_home()
        else:
            new_cell = krat.organism_movement()
        if new_cell != self:
            krat.expend_energy(self.krat_energy_cost)
            moving_krat = (new_cell,krat,self)
            self.landscape.krat_move_pool.append(moving_krat)
            moving_krat_list.append(krat)

    def snake_move(self,snake,moving_snake_list):
        # think of snake movement
        #if self.sim.time_of_day == snake.hunting_hours[-1]+1:
        #    new_cell = snake.return_home()
        new_cell = snake.organism_movement()
        if new_cell != self:
            snake.expend_energy(self.snake_energy_cost)
            snake.missed_opportunity_cost = 0
            moving_snake = (new_cell,snake,self)
            self.landscape.snake_move_pool.append(moving_snake)
            moving_snake_list.append(snake)

    def owl_move(self,owl,moving_owl_list):
        # think of snake movement
        #if self.sim.time_of_day == snake.hunting_hours[-1]+1:
        #    new_cell = snake.return_home()
        new_cell = owl.organism_movement()
        if new_cell != self:
            moving_owl = (new_cell,owl,self)
            self.landscape.owl_move_pool.append(moving_owl)
            moving_owl_list.append(owl)             

    def krat_grave(self):
        self.krats = [ krat for krat in self.krats if krat.alive == True ]

    def snake_grave(self):
        self.snakes = [ snake for snake in self.snakes if snake.alive == True ]

    def newborn_krats(self):
        if len(self.krat_incubation_list) > 0:
            #print('time{},krats{}'.format(self.sim.time_of_day,len(self.krat_incubation_list)))
            for baby_krat in self.krat_incubation_list:
                krat = Krat(sim = self.sim,
                    initial_energy = baby_krat["energy"],
                    energy_deviation = baby_krat["energy_deviation"],
                    move_range = baby_krat["move_range"],
                    home_cell = self,
                    foraging_rate = baby_krat["foraging_rate"],
                    krat_max_litter_size = baby_krat["krat_max_litter_size"],
                    krat_litter_frequency = baby_krat["krat_litter_frequency"],
                    open_preference_weight = baby_krat["open_preference_weight"],
                    bush_preference_weight = baby_krat["bush_preference_weight"],
                    foraging_hours = baby_krat["foraging_hours"])
                self.add_krat(krat)
                krat.current_cell = self # krat.current_cell_id = self.cell_id
        self.krat_incubation_list = []

    def newborn_snakes(self):
        if len(self.snake_incubation_list) > 0:
            for baby_snake in self.snake_incubation_list:
                snake = Snake(sim = self.sim,
                    initial_energy = baby_snake["energy"],
                    energy_deviation = baby_snake["energy_deviation"],
                    move_range = baby_snake["move_range"],
                    home_cell = self,
                    strike_success_probability = baby_snake["strike_success_probability"],
                    snake_max_litter_size = baby_snake["snake_max_litter_size"],
                    snake_litter_frequency = baby_snake["snake_litter_frequency"],
                    open_preference_weight = baby_snake["open_preference_weight"],
                    bush_preference_weight = baby_snake["bush_preference_weight"],
                    hunting_hours = baby_snake["hunting_hours"])
                self.add_snake(snake)
                snake.current_cell = self
        self.snake_incubation_list = []

    def krat_predation_by_snake(self,snake):
        # stand in value and move to config file V
        probability_of_krat_encounter = len(self.krats)/(len(self.krats)+1)*self.sim.time_step #1 krat has a 1/2 chance in interacting with a snake
        if self.rng.random() < probability_of_krat_encounter:
            snake.expend_energy(self.snake_energy_cost)
            krat = self.select_krat()
            if self.rng.random() < snake.strike_success_probability:
                snake.consume(krat.energy)
                self.pop_krat(self.krats.index(krat))
            else:
                krat.register_predation_event()
                snake.missed_opportunity_cost+=1

    def krat_predation_by_owl(self,owl):
        # stand in value and move to config file V
        probability_of_krat_encounter = len(self.krats)/(len(self.krats)+1)*self.sim.time_step #1 krat has a 1/2 chance in interacting with a snake
        if self.rng.random() < probability_of_krat_encounter:
            krat = self.select_krat()
            if self.rng.random() < owl.strike_success_probability:
                self.pop_krat(self.krats.index(krat))
            else:
                krat.register_predation_event()

    def predation_cycle_snake(self,snake):
        snake.hunting_period()
        snake.expend_energy(self.snake_energy_cost) 
        if snake.hunting:
            self.other_critter_predation(snake)
            self.krat_predation_by_snake(snake)

    def predation_cycle_owl(self,owl):
        owl.hunting_period() 
        if owl.hunting and self.habitat_type == '[<MicrohabitatType.OPEN: 1>]':
            self.krat_predation_by_owl(owl)

    def foraging_rat(self,krat):
        krat.foraging_period()
        krat.expend_energy(self.krat_energy_cost)
        if krat.foraging and krat.alive:
            krat_energy_gain = krat.energy_gain(self.cell_energy_pool)
            if self.cell_energy_pool > 0:
                krat.forage(krat_energy_gain)
                self.cell_forage(krat_energy_gain)

    def krat_activity_pulse_behavior(self):
        """ Krat function, this is the general behavior of either moving or foraging of the krat for one activity pulse."""

        moving_krats = []
        for krat in self.krats:
            if self.sim.time_of_day in krat.foraging_hours and krat.alive:
                krat.reproduction(self.krat_incubation_list)
                projected_energy_gain = krat.energy_gain(self.cell_energy_pool)
                proj_krat_energy_state = krat.homeostasis_delta_calculator(
                                                                            energy_gain=projected_energy_gain, 
                                                                            cost_to_move=self.krat_energy_cost, 
                                                                            predation_cost=krat.predation_counter, 
                                                                            missed_opportunity_cost=1, #assumption
                                                                            competition_cost=(len(self.krats)-1),
                                                                            basal_energy_cost=self.krat_energy_cost)
                if proj_krat_energy_state >= 0:
                    self.foraging_rat(krat)
                    df = [krat.krat_id, self.sim.time, proj_krat_energy_state, 1, 0]
                else:
                    self.krat_move(krat,moving_krat_list = moving_krats)
                    df = [krat.krat_id, self.sim.time, proj_krat_energy_state, 0, 1]
                self.sim.krat_energy_calc_report.append(df)
            elif self.sim.time_of_day == krat.foraging_hours[-1]+1:
                self.krat_move(krat,moving_krat_list = moving_krats,return_home=True)
        self.krats = [krat for krat in self.krats if krat not in moving_krats and krat.alive]     

    def snake_activity_pulse_behavior(self):
        """ snake function, this is the general behavior of either moving or hunting of the krat for one activity pulse."""
        moving_snakes = []
        for snake in self.snakes:
            if self.sim.time_of_day in snake.hunting_hours and snake.alive:
                snake.reproduction(self.snake_incubation_list)
                projected_energy_gain = 60/len(snake.hunting_hours) #expected energy gain assumption
                proj_snake_energy_state = snake.homeostasis_delta_calculator(
                                                                            energy_gain=projected_energy_gain, 
                                                                            cost_to_move=self.snake_energy_cost, #assumption costs twice as much for a snake to move because big and ineffecient
                                                                            predation_cost=snake.predation_counter, 
                                                                            missed_opportunity_cost=snake.missed_opportunity_cost, #assumption
                                                                            competition_cost=len(self.snakes)-1, #assumption
                                                                            basal_energy_cost=self.snake_energy_cost)
                if proj_snake_energy_state >= 0:
                    self.predation_cycle_snake(snake)
                    df = [snake.snake_id, self.sim.time, proj_snake_energy_state, 1, 0]
                else:
                    self.snake_move(snake, moving_snake_list=moving_snakes)
                    df = [self.sim.time,proj_snake_energy_state,0,1]
                self.sim.snake_energy_calc_report.append(df)
        self.snakes = [snake for snake in self.snakes if snake not in moving_snakes and snake.alive]

    def owl_activity_pulse_behavior(self):
        #self.snake_grave()
        moving_owls = []
        for owl in self.owls:
            self.predation_cycle_owl(owl)
            self.owl_move(owl, moving_owl_list=moving_owls)
        self.owls = [owl for owl in self.owls if owl not in moving_owls]

    def cell_grass_reproduction(self):
        if self.sim.day_of_year in range(122,183) and self.sim.time_of_day == 6:
            self.cell_energy_pool += self.rng.randrange(2,4)




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
        self.owl_move_pool = []
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

    def initialize_snake_pop(self,initial_snake_pop,snake_initial_energy,energy_deviation,snake_litter_frequency,snake_max_litter_size,strike_success_probability,move_range,open_preference_weight, bush_preference_weight):
        isp = initial_snake_pop
        while isp > 0:
            cell = self.select_random_cell()
            snake = Snake(sim = sim,
                         initial_energy = snake_initial_energy,
                         energy_deviation = energy_deviation,
                         home_cell = cell,
                         snake_litter_frequency = snake_litter_frequency,
                         snake_max_litter_size = snake_max_litter_size,
                         strike_success_probability = strike_success_probability,
                         move_range = move_range,
                         open_preference_weight = open_preference_weight,
                         bush_preference_weight = bush_preference_weight)
            cell.add_snake(snake)
            snake.current_cell=cell
            isp = isp-1

    def initialize_krat_pop(self,initial_krat_pop,initial_energy,energy_deviation,krat_litter_frequency,krat_max_litter_size,foraging_rate, move_range, open_preference_weight, bush_preference_weight):
        ikp = initial_krat_pop
        while ikp > 0:
            cell = self.select_random_cell()
            krat = Krat(sim = sim,
                        initial_energy = initial_energy,
                        energy_deviation = energy_deviation,
                        move_range = move_range,
                        home_cell= cell,
                        krat_max_litter_size = krat_max_litter_size,
                        krat_litter_frequency = krat_litter_frequency,
                        foraging_rate = foraging_rate,
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight)
            cell.add_krat(krat)
            krat.current_cell=cell
            ikp = ikp-1

    def initialize_owl_pop(self,initial_owl_pop,move_range,strike_success_probability, open_preference_weight, bush_preference_weight):
        iop = initial_owl_pop
        while iop > 0:
            cell = self.select_random_cell()
            owl = Owl(sim = sim,
                        move_range = move_range,
                        strike_success_probability = strike_success_probability,
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight)
            cell.add_owl(owl)
            owl.current_cell=cell
            iop = iop-1

    def relocate_krats(self):
        for i, krat in enumerate(self.krat_move_pool):
            new_cell = krat[0]
            krat_object = krat[1]
            new_cell.add_krat(krat_object)
            krat_object.current_cell = new_cell
        self.krat_move_pool = []

    def relocate_snakes(self):
        for j, snake in enumerate(self.snake_move_pool):
            new_cell = snake[0]
            snake_object = snake[1]
            new_cell.add_snake(snake_object)
            snake_object.current_cell = new_cell 
        self.snake_move_pool = []

    def relocate_owls(self):
        for j, snake in enumerate(self.owl_move_pool):
            new_cell = owl[0]
            owl_object = owl[1]
            new_cell.add_owl(owl_object)
            owl_object.current_cell = new_cell 
        self.owl_move_pool = []

    def landscape_stats(self,cell):
        if self.sim.time_of_day in [0,6,12]: #specify in documentation
            cell_krat_energy = sum([krat.energy for krat in cell.krats])
            cell_krat_movement_history = sum([krat.number_of_movements for krat in cell.krats])
            cell_snake_energy = sum([snake.energy for snake in cell.snakes])
            cell_snake_movement_history = sum([snake.number_of_movements for snake in cell.snakes])
            data = [sim.time,sim.time_of_day,cell.cell_id,cell.habitat_type,cell.cell_energy_pool,len(cell.krats),cell_krat_energy,cell_krat_movement_history,len(cell.snakes),cell_snake_energy,cell_snake_movement_history ]
            sim.report.append(data)

    def landscape_dynamics(self):
        for cell_width in self.cells:
            for cell in cell_width:
                cell.cell_over_populated()
                self.landscape_stats(cell)
                cell.krat_activity_pulse_behavior()
                cell.snake_activity_pulse_behavior()
                cell.owl_activity_pulse_behavior()
                cell.newborn_krats()
                cell.newborn_snakes()
                cell.cell_grass_reproduction()
        self.relocate_krats()
        self.relocate_snakes()
        #print(len(self.krat_move_pool))


class Sim(object):
    #compiles landscape and designates parameters to the landscape. 
    def __init__(self,file_path,rng = None):
        self.file_path = file_path
        self.report = []
        self.krat_energy_calc_report = []
        self.snake_energy_calc_report = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.time = 0
        self.time_of_day = 0
        self.day_of_year = 0

    def probability_time_step_adjustment(self,probability_success,time_step,number_of_successes):
        p = probability_success
        q = 1-probability_success
        cn = math.factorial(int(time_step))/(math.factorial(int(time_step - number_of_successes))*math.factorial(int(number_of_successes)))
        prob = cn*p**(number_of_successes)*q**(time_step - number_of_successes)
        return prob

    def configure(self, config_d):
        self.time_step = int(config_d["time_step"])
        self.time_steps_in_a_day = int(24/self.time_step)
        self.end_time = config_d["days_of_sim"]*self.time_steps_in_a_day
        #self.energy_dependence_movement = config_d["energy_dependence_movement"]
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"]
                )
        self.landscape.build(
                cell_energy_pool = config_d["cell_energy_pool"],
                krat_energy_cost = config_d["krat_energy_cost"]*self.time_step ,
                snake_energy_cost = config_d["snake_energy_cost"]*self.time_step )
        self.landscape.initialize_snake_pop(
                initial_snake_pop=config_d["initial_snake_pop"],
                snake_initial_energy=config_d["snake_initial_energy"],
                energy_deviation = config_d["snake_energy_deviation"],
                snake_max_litter_size = config_d["snake_max_litter_size"],
                snake_litter_frequency = config_d["snake_litter_frequency"],
                strike_success_probability = config_d["strike_success_probability"],
                move_range = config_d["snake_move_range"],
                open_preference_weight = config_d["snake_open_preference_weight"],
                bush_preference_weight = config_d["snake_bush_preference_weight"]
                )
        self.landscape.initialize_krat_pop(
                initial_krat_pop=config_d["initial_krat_pop"],
                initial_energy=config_d["krat_initial_energy"],
                energy_deviation = config_d["krat_energy_deviation"],
                krat_max_litter_size = config_d["krat_max_litter_size"],
                krat_litter_frequency = config_d["krat_litter_frequency"],
                foraging_rate = float(config_d["krat_energy_gain"]*self.time_step),
                move_range = config_d["krat_move_range"],
                open_preference_weight = config_d["krat_open_preference_weight"],
                bush_preference_weight = config_d["krat_bush_preference_weight"]
                )
        self.landscape.initialize_owl_pop(
                initial_owl_pop=config_d["initial_owl_pop"],
                move_range = config_d["owl_move_range"],
                strike_success_probability = config_d["owl_catch_success"],
                open_preference_weight = config_d["owl_open_preference_weight"],
                bush_preference_weight = config_d["owl_bush_preference_weight"]
                )

    def read_configuration_file(self):
        with open(self.file_path) as f:
            config_d = json.load(f)
        sim1 = config_d['sim'][0]
        self.configure(sim1)

    def hour_tick(self):
        if self.time_of_day >= (24-self.time_step):
            self.time_of_day = 0
            self.day_of_year += 1
            if (self.day_of_year+self.time_step) == 366:
                self.day_of_year = 0
        else:
            self.time_of_day += self.time_step

    def day_tick(self):
        print('time{}, day {}'.format(self.time_of_day,self.day_of_year))
        if (self.time_of_day+self.time_step) == 24:
            self.day_of_year += 1
        if (self.day_of_year+self.time_step) == 366:
            self.day_of_year = 0

    def main(self):
        start = round(time.time())
        self.read_configuration_file()
        for i in range(0,self.end_time,self.time_step):
            self.landscape.landscape_dynamics()
            self.hour_tick()
            self.time += self.time_step
        self.report_writer(array = self.report,file_name = 'Cell_stats_sim_1.csv')
        self.report_writer(array = self.krat_energy_calc_report,file_name = 'krat_energy.csv')
        self.report_writer(array = self.snake_energy_calc_report,file_name = 'snake_energy.csv')
        time_elapsed = round(time.time()) - start
        print(time_elapsed)

    def test(self):
        self.read_configuration_file()
        cells = self.landscape.cells
        for cell_width in cells:
            for cell in cell_width:
                cell_id = '{},{}'.format(cell.cell_id[0],cell.cell_id[1])
                print(cell_id)
        

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



