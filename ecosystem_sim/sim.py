#!/usr/bin/python
from enum import Enum,auto
import random
import numpy as np
import matplotlib.pyplot as plt
import json
from organismsim import Krat
from organismsim import Snake
from organismsim import Owl
from itertools import chain
import math
import time
#look up contact rates based on spatial scale and tempor
#brownian motion 

class Cell(object):
    def __init__(self, sim, habitat_type,cell_id):
        #cell represents the microhabitat and governs shorter geospatial interactions
        # Order: open, bush
        self.sim = sim
        self.krats = []
        self.snakes = []
        self.owls = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.cell_id = cell_id     
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

    def clean_krat_list(self):
        self.krats = []

    def clean_snake_list(self):
        self.snakes = []

    def cell_over_populated(self):
        if len(self.krats) > self.sim.initial_krat_pop:
            raise ValueError("Krats mating too much")
        if len(self.snakes) > self.sim.initial_snake_pop:
            raise ValueError("snakes mating too much")

    def krat_move(self, krat,moving_krat_list,return_home=False):
        if return_home== True:
            new_cell = krat.return_home()
        else:
            new_cell = krat.organism_movement()
        if new_cell != self:
            moving_krat = (new_cell,krat,self)
            self.landscape.krat_move_pool.append(moving_krat)
            moving_krat_list.append(krat)

    def snake_move(self,snake,moving_snake_list):
        new_cell = snake.organism_movement()
        if new_cell != self:
            moving_snake = (new_cell,snake,self)
            self.landscape.snake_move_pool.append(moving_snake)
            moving_snake_list.append(snake)

    def owl_move(self,owl,moving_owl_list):
        new_cell = owl.organism_movement()
        if new_cell != self:
            moving_owl = (new_cell,owl,self)
            self.landscape.owl_move_pool.append(moving_owl)
            moving_owl_list.append(owl)             

    def krat_predation_by_snake(self,snake):
        live_krats = [krat for krat in self.krats if krat.alive] 
        ss = snake.calc_strike_success_probability(self)
        energy_cost = snake.energy_cost
        if len(live_krats) > 0 and self.rng.random() < ss:
            krat_index = self.rng.randint(0,len(live_krats)-1)
            krat = self.select_krat(krat_index = krat_index)
            krat.alive = False
            energy_gain = snake.energy_gain_per_krat              
        else:
            energy_gain = 0
        energy_delta = (energy_gain - energy_cost)
        snake.energy_score += energy_delta
        if snake.move_preference:
            snake.log_microhabitat_energy_delta_preference(snake.current_cell.habitat_type[0].name, snake.energy_score)

    def krat_predation_by_owl(self,owl):
        # stand in value and move to config file V
        live_krats = [krat for krat in self.krats if krat.alive] 
        if len(live_krats) > 0 and self.rng.random() < owl.strike_success_probability and self.habitat_type[0].name == 'OPEN':
            krat_index = self.rng.randint(0,len(live_krats)-1)
            krat = self.select_krat(krat_index = krat_index)
            krat.alive = False

    def foraging_rat(self,krat):
        krat_energy_gain = krat.calc_energy_gain(self)
        krat_energy_cost = krat.calc_energy_cost()
        energy_delta = (krat_energy_gain - krat_energy_cost)
        krat.energy_score += energy_delta
        if krat.move_preference:
            krat.log_microhabitat_energy_delta_preference(self.habitat_type[0].name, energy_delta)

    def krat_activity_pulse_behavior(self):
        """ Krat function, this is the general behavior of either moving or foraging of the krat for one activity pulse."""
        moving_krats = []
        for krat in self.krats:
            krat.generate_krat_stats()
            self.foraging_rat(krat)
            if self.sim.cycle % krat.movement_frequency == 0 and self.sim.cycle != 0:
                self.krat_move(krat,moving_krat_list = moving_krats)           
        self.krats = [krat for krat in self.krats if krat not in moving_krats and krat.alive]     

    def snake_activity_pulse_behavior(self):
        """ snake function, this is the general behavior of either moving or hunting of the krat for one activity pulse."""
        moving_snakes = []
        for snake in self.snakes:
            snake.generate_snake_stats()
            self.krat_predation_by_snake(snake)
            if self.sim.cycle % snake.movement_frequency == 0 and self.sim.cycle != 0: #BUILT IN ASSUMPTION NEED TO CODE INTO CONFIG
                self.snake_move(snake, moving_snake_list=moving_snakes)            
        self.snakes = [snake for snake in self.snakes if snake not in moving_snakes and snake.alive]

    def owl_activity_pulse_behavior(self):
        moving_owls = []
        for owl in self.owls:
            self.krat_predation_by_owl(owl)
            self.owl_move(owl, moving_owl_list=moving_owls)
        self.owls = [owl for owl in self.owls if owl not in moving_owls]


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
        # cell_list
        self.cells_x_columns = int(round(self.size_x/10))
        self.cells_y_rows = int(round(self.size_y/10))
        self.microhabitat_open_bush_proportions = microhabitat_open_bush_proportions
        self.krat_move_pool = []
        self.snake_move_pool = []
        self.owl_move_pool = []
        self.rng = self.sim.rng

    def build(self):
        self.cells = []
        for yidx in range(self.cells_y_rows):
            temp_x = []
            for xidx in range(self.cells_x_columns):
                cell_id = (yidx,xidx)
                cell = Cell(
                    sim = self.sim,
                    habitat_type = self.select_random_cell_type(),
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

    def initialize_snake_pop(self,initial_snake_pop,strike_success_probability_bush,strike_success_probability_open,energy_gain_per_krat,energy_cost,move_range,movement_frequency,move_preference,snake_genotype_frequencies, memory_length_cycles):
        isp = self.sim.initial_snake_pop
        for key, freq in snake_genotype_frequencies.items():
            pop = round(isp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                open_preference_weight, bush_preference_weight = key
                snake = Snake(sim = sim,
                            strike_success_probability_bush = strike_success_probability_bush,
                            strike_success_probability_open = strike_success_probability_open,
                            energy_gain_per_krat = energy_gain_per_krat,
                            energy_cost = energy_cost,
                            move_range = move_range,
                            movement_frequency = movement_frequency,
                            move_preference = move_preference,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight,
                            memory_length_cycles = memory_length_cycles 
                            )
                cell.add_snake(snake)
                snake.current_cell=cell
                #snake.generate_snake_stats()
                pop = pop-1

    def initialize_krat_pop(self,initial_krat_pop,energy_gain_bush,energy_gain_open,energy_cost, death_cost, move_range,movement_frequency, move_preference, krat_genotype_frequencies, memory_length_cycles):
        ikp = self.sim.initial_krat_pop
        for key, freq in krat_genotype_frequencies.items():
            pop = round(ikp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                open_preference_weight, bush_preference_weight = key
                cell = self.select_random_cell()
                krat = Krat(sim = sim,
                            energy_gain_bush = energy_gain_bush, #from bouskila
                            energy_gain_open = energy_gain_open, #from bouskila
                            energy_cost = energy_cost,
                            death_cost = death_cost,
                            move_range = move_range,
                            movement_frequency = movement_frequency,
                            home_cell= cell,
                            move_preference = move_preference,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight,
                            memory_length_cycles = memory_length_cycles )
                cell.add_krat(krat)
                krat.current_cell=cell
                #krat.generate_krat_stats()
                pop = pop-1

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
        if (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0:
            continue
        else:
            for i, krat in enumerate(self.krat_move_pool):
                new_cell = krat[0]
                krat_object = krat[1]
                new_cell.add_krat(krat_object)
                krat_object.current_cell = new_cell
        self.krat_move_pool = []

    def relocate_snakes(self):
        if (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0:
            continue
        else:
            for j, snake in enumerate(self.snake_move_pool):
                new_cell = snake[0]
                snake_object = snake[1]
                new_cell.add_snake(snake_object)
                snake_object.current_cell = new_cell 
        self.snake_move_pool = []

    def relocate_owls(self):
        for j, owl in enumerate(self.owl_move_pool):
            new_cell = owl[0]
            owl_object = owl[1]
            new_cell.add_owl(owl_object)
            owl_object.current_cell = new_cell 
        self.owl_move_pool = []

    def populate_krat_population_fitness_data(self,total_org_list, cell_org_list):
        for org in cell_org_list:
            total_org_list.append(org)

    def next_gen_krat_rep_dist_prep(self, total_org_list):
        #if (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0:
        new_gen_genotype = {}
        for org in total_org_list:
            genotype = (org.bush_preference_weight,krat.open_preference_weight)
            payoff = krat.energy_score
            if key not in dict1:
                new_gen_genotype[genotype] = []
                new_gen_genotype[genotype].append(payoff)
            else:
                new_gen_genotype[genotype].append(payoff)
        geno_dict = {key: sum(value)/sum(list(chain(*new_gen_genotype.values()))) for (key,value) in seq_dict.items()}
        return geno_dict
 
            # parent_list_krat = self.rng.choices(krat,weights = fitness,k=num_krat_babies)
            # for parent in parent_list_krat:
            #     for cell_width in self.cells:
            #         for cell in cell_width:
            #             if parent in cell.krats:
            #                 baby_krat = Krat(sim = self.sim,
            #                                 energy_gain_bush = parent.energy_gain_bush, #from bouskila
            #                                 energy_gain_open = parent.energy_gain_open, #from bouskila
            #                                 energy_cost = parent.energy_cost,
            #                                 death_cost = parent.death_cost,
            #                                 move_range = parent.move_range,
            #                                 movement_frequency = parent.movement_frequency,
            #                                 home_cell= cell,
            #                                 move_preference = parent.move_preference,
            #                                 open_preference_weight = parent.open_preference_weight,
            #                                 bush_preference_weight = parent.bush_preference_weight)
            #                 cell.add_krat(baby_krat)

    def iter_through_cells(self):
        for cell_width in self.cells:
            for cell in cell_width:
                self.total_krats += len(cell.krats)
                self.total_snakes += len(cell.snakes)
                self.total_owls += len(cell.owls)
                cell.cell_over_populated()
                preds = len(cell.snakes) + len(cell.owls)
                if preds > 0:
                    owl_move_first_probability = len(cell.owls)/preds
                    if owl_move_first_probability < self.rng.random() and owl_move_first_probability > 0:
                        cell.owl_activity_pulse_behavior()
                        cell.snake_activity_pulse_behavior()
                    else:
                        cell.snake_activity_pulse_behavior()
                        cell.owl_activity_pulse_behavior()
                if (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0:
                    self.populate_krat_population_fitness_data(total_org_list = self.total_krat_list, cell_org_list= cell.krats) #payoff
                    cell.clean_krat_list()
                cell.krat_activity_pulse_behavior()

    def landscape_dynamics(self):
        self.total_krats = 0
        self.total_snakes = 0
        self.total_owls = 0
        self.iter_through_cells()
        self.relocate_krats()
        self.relocate_snakes()
        self.krat_reproduction()


class Sim(object):
    #compiles landscape and designates parameters to the landscape. 
    def __init__(self,initial_conditions_file_path,rng = None):
        self.initial_conditions_file_path = initial_conditions_file_path
        self.snake_info = []
        self.krat_info = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.cycle = 0
        

    def genotype_freq_test(self,genotype_freq_dict):
        if sum(genotype_freq_dict.values()) != 1:
            raise Exception("Genotype frequencies do not sum to 1.")


    def configure(self, config_d):
        self.genotype_freq_test(config_d["krat_pop_genotype_freq"])
        self.genotype_freq_test(config_d["snake_pop_genotype_freq"])
        self.end_time = config_d["cycles_of_sim"]
        self.initial_krat_pop = config_d["initial_krat_pop"]
        self.initial_snake_pop = config_d["initial_snake_pop"]
        self.krat_reproduction_freq = config_d["krat_reproduction_freq_per_x_cycles"]
        #self.energy_dependence_movement = config_d["energy_dependence_movement"]
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"]
                )
        self.landscape.build()
        self.landscape.initialize_snake_pop(
                initial_snake_pop=config_d["initial_snake_pop"],
                strike_success_probability_bush = config_d["snake_strike_success_probability_bush"],
                strike_success_probability_open = config_d["snake_strike_success_probability_open"],
                energy_gain_per_krat = config_d["snake_energy_gain"],
                energy_cost = config_d["snake_energy_cost"],
                move_range = config_d["snake_move_range"],
                movement_frequency = config_d["snake_movement_frequency_per_x_cycles"],
                move_preference =config_d["move_preference_algorithm"],
                memory_length_cycles = config_d["memory_length_snake"],
                snake_genotype_frequencies = config_d["snake_pop_genotype_freq"]
                )
        self.landscape.initialize_krat_pop(
                initial_krat_pop=config_d["initial_krat_pop"],
                move_range = config_d["krat_move_range"],
                movement_frequency = config_d["krat_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["krat_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["krat_energy_gain_open"], #from bouskila
                energy_cost=config_d["krat_energy_cost"],
                death_cost=config_d["krat_cost_of_death"],
                move_preference =config_d["move_preference_algorithm"],
                memory_length_cycles = config_d["memory_length_krat"],
                krat_genotype_frequencies = config_d["krat_pop_genotype_freq"]
                )
        self.landscape.initialize_owl_pop(
                initial_owl_pop=config_d["initial_owl_pop"],
                move_range = config_d["owl_move_range"],
                strike_success_probability = config_d["owl_catch_success"],
                open_preference_weight = 1,
                bush_preference_weight = 0
                )

    def read_configuration_file(self):
        with open(self.initial_conditions_file_path) as f:
            config_d = json.load(f)
        sim1 = config_d['sim'][0]
        self.configure(sim1)

    def analyze_and_plot_org_fitness(self,org_data):
        open_pref_x = []
        bush_pref_x = []
        mixed_pref_x = []
        open_pref_fit = []
        bush_pref_fit = []
        mixed_pref_fit = []
        for row in org_data:
            if row[3] == 1:
                #bush
                bush_pref_x.append(row[1])
                bush_pref_fit.append(row[4])
            elif row[3] == 0:
                #open
                open_pref_x.append(row[1])
                open_pref_fit.append(row[4])
            else:
                mixed_pref_x.append(row[1])
                mixed_pref_fit.append(row[4])
        data = ((open_pref_x, open_pref_fit), (bush_pref_x,bush_pref_fit), (mixed_pref_x,mixed_pref_fit))
        colors = ("red", "green", "blue")
        groups = ("open", "bush", "mixed")

        # Create plot
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

        for data, color, group in zip(data, colors, groups):
            x, y = data
            ax.scatter(x, y, alpha=0.8, c=color, edgecolors='none', s=30, label=group)

        plt.title('Matplot scatter plot')
        plt.legend(loc=2)
        plt.show()


    def main(self):
        start = round(time.time())
        self.read_configuration_file()
        for i in range(0,self.end_time,1):
            self.landscape.landscape_dynamics()
            self.cycle += 1
        self.report_writer(array = self.krat_info,file_name = 'krat_energy.csv')
        self.report_writer(array = self.snake_info,file_name = 'snake_energy.csv')
        time_elapsed = round(time.time()) - start
        print(time_elapsed)
        #self.analyze_and_plot_org_fitness(org_data = self.snake_info)

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



