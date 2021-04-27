#!/usr/bin/python
from enum import Enum,auto
import random
import json
from xomar import organismsim as org
from itertools import chain
import math
import time
import csv
#look up contact rates based on spatial scale and tempor
#brownian motion 

class Cell(object):
    '''
    This object represents a sub space of the landscape object that is a container for organisms to interact in.
    The user will have to keep in mind the abstract size of these interaction landscapes when setting up simulation variables.
    Args:
        sim -- the simulation object with base parameters such as a random number generator and a time parameter. (sim object)
        habitat_type -- this is a label from an enumerated habitat object. (enum object)
        cell_id -- a tuple of the postion of the cell on the landscape in the y direction (rows) and the landscape in the x direction (columns). (tuple with 2 elements)
    Attributes:
        krats -- a list that holds krat objects. (list)
        snakes -- a list that holds sake objects. (list)
        landscape -- the landscape object the cell operates in.
        rng -- a random number operator object.
    '''
    def __init__(self, sim, habitat_type,cell_id,prey_competition=False):
        self.sim = sim
        self.krats = []
        self.snakes = []
        self.owls = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.cell_id = cell_id
        self.prey_competition = prey_competition     
        self.rng = self.sim.rng

    def __hash__(self):
        return id(self)

    def add_krat(self, krat):
        '''Add a krat to the population of this cells krats'''
        self.krats.append(krat)

    def add_snake(self, snake):
        '''Add a snake to the population of this cells snakes'''
        self.snakes.append(snake)

    def add_owl(self,owl):
        '''adds an owl object to the landscape.'''
        self.owls.append(owl)

    def select_krat(self,krat_index = None):
        '''returns a random krat object if no specific index is provided.'''
        if krat_index == None:
            krat_index = self.rng.randint(0,len(self.krats)-1)
        krat = self.krats[krat_index]
        return krat

    def select_snake(self,snake_index = None):
        '''returns a random snake object if no specific index is provided.'''
        if snake_index == None:
            snake_index = self.rng.randint(0,len(self.snake)-1)
        snake = self.snakes[snake_index]
        return snake

    def pop_krat(self,krat_index):
        '''Selects a krat at random from population and removes it and returns the object '''
        return self.krats.pop(krat_index)

    def pop_snake(self,snake_index):
        '''Selects a snake at random from population and removes it and returns the object '''
        return self.snakes.pop(snake_index)

    def clean_krat_list(self):
        '''creates a fresh list for the attribute krats'''
        self.krats = []

    def clean_snake_list(self):
        '''creates a fresh list for the attribute snakes'''
        self.snakes = []

    def cell_over_populated(self):
        '''test that makes sure cells don't become overpopulated and break sim'''
        if len(self.krats) > self.sim.initial_krat_pop:
            raise ValueError("Krats mating too much")
        if len(self.snakes) > self.sim.initial_snake_pop:
            raise ValueError("snakes mating too much")

    def krat_move(self, krat,moving_krat_list,return_home=False):
        '''runs the krat movement algorithm and moves the krat from the cell to a temp list in the landscape. 
        Optional can designate the krat to return to designated nest cell tied to the krat object.'''
        if return_home== True:
            new_cell = krat.return_home()
        else:
            new_cell = krat.organism_movement()
        if new_cell != self:
            moving_krat = (new_cell,krat,self)
            self.landscape.krat_move_pool.append(moving_krat)
            moving_krat_list.append(krat)

    def snake_move(self,snake,moving_snake_list):
        '''runs the snake movement algorithm and moves the krat from the cell to a temp list in the landscape. '''
        new_cell = snake.organism_movement()
        if new_cell != self:
            moving_snake = (new_cell,snake,self)
            self.landscape.snake_move_pool.append(moving_snake)
            moving_snake_list.append(snake)

    def owl_move(self,owl,moving_owl_list):
        '''runs the owl movement algorithm and moves the krat from the cell to a temp list in the landscape. '''
        new_cell = owl.organism_movement()
        if new_cell != self:
            moving_owl = (new_cell,owl,self)
            self.landscape.owl_move_pool.append(moving_owl)
            moving_owl_list.append(owl)             

    def krat_predation_by_snake(self,snake):
        '''determines whether or not the snake that was passed into the function successfully kills and obtains payoff of a krat that shares the cell with it.'''
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
        '''determines whether or not the owl that was passed into the function successfully kills and obtains payoff of a krat that shares the cell with it.'''
        live_krats = [krat for krat in self.krats if krat.alive] 
        if len(live_krats) > 0 and self.rng.random() < owl.strike_success_probability and self.habitat_type[0].name == 'OPEN':
            krat_index = self.rng.randint(0,len(live_krats)-1)
            krat = self.select_krat(krat_index = krat_index)
            krat.alive = False

    def foraging_rat(self,krat):
        '''Provides krat with appropriate pay off for foraging in the cell.'''
        if self.prey_competition:
            krat_energy_gain = krat.calc_energy_gain(self)/len(self.krats)
        else:
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
            if (self.sim.cycle % self.sim.krat_data_sample_frequency) == 0:
                krat.generate_krat_stats()
            self.foraging_rat(krat)
            if self.sim.cycle % krat.movement_frequency == 0 and self.sim.cycle != 0:
                self.krat_move(krat,moving_krat_list = moving_krats)           
        self.krats = [krat for krat in self.krats if krat not in moving_krats and krat.alive]     

    def snake_activity_pulse_behavior(self):
        """ snake function, this is the general behavior of either moving or hunting of the krat for one activity pulse."""
        moving_snakes = []
        for snake in self.snakes:
            if (self.sim.cycle % self.sim.snake_data_sample_frequency) == 0:
                snake.generate_snake_stats()
            self.krat_predation_by_snake(snake)
            if self.sim.cycle % snake.movement_frequency == 0 and self.sim.cycle != 0: 
                self.snake_move(snake, moving_snake_list=moving_snakes)      
            snake.snake_death()      
        self.snakes = [snake for snake in self.snakes if snake not in moving_snakes and snake.alive]

    def owl_activity_pulse_behavior(self):
        moving_owls = []
        for owl in self.owls:
            self.krat_predation_by_owl(owl)
            self.owl_move(owl, moving_owl_list=moving_owls)
        self.owls = [owl for owl in self.owls if owl not in moving_owls]


class Landscape(object):
    '''Landscape is an object that is composed of Cells are 10m x 10m that range across the x and the y of the landscape.
    landscapes is responsible for generating cells.
    Args:
        sim -- the simulation object with base parameters such as a random number generator and a time parameter. (sim object)
        size_x -- number of columns the cell array will have to represent space in the x direction.
        size_y -- number of rows the cell array will have to represent space in the y direction.
        microhabitat_open_bush_proportions -- this is the ratio of cells that will be populated with one type of  microhabitat vs another.
    Attributes:
        cells -- a list of cell objects that populate the landscape.
        cells_x_columns -- the length of the cells array in the x direction (columns). (int)
        cells_y_rows -- the length of the cells array in the y direction (rows). (int)
        krat_move_pool -- a temporary list that holds krats that need to be relocated to different cells in the landscape.
        snake_move_pool -- a temporary list that holds snakes that need to be relocated to different cells in the landscape.
        owl_move_pool = -- a temporary list that holds owls that need to be relocated to different cells in the landscape.
        total_krat_list -- a list of the krat objects used for analysis and reproduction.
        total_snake_list -- a list of the snake objects used for analysis and reproduction.
        total_owl_list -- a list of the owl objects used for analysis and reproduction.
        '''
    class MicrohabitatType(Enum):
        OPEN = auto()
        BUSH = auto()

    def __init__(self,sim,size_x,size_y,microhabitat_open_bush_proportions):
        self.sim = sim
        self.size_x = size_x
        self.size_y = size_y
        self.cells = None
        # cell_list
        self.cells_x_columns = int(round(self.size_x))
        self.cells_y_rows = int(round(self.size_y))
        self.microhabitat_open_bush_proportions = microhabitat_open_bush_proportions
        self.krat_move_pool = []
        self.snake_move_pool = []
        self.owl_move_pool = []
        self.total_krat_list = [] 
        self.total_snake_list = []
        self.total_owl_list = []
        self.rng = self.sim.rng

    def build(self):
        '''Populates the attribute cells with an x by y array'''
        self.cells = []
        for yidx in range(self.cells_y_rows):
            temp_x = []
            for xidx in range(self.cells_x_columns):
                cell_id = (yidx,xidx)
                cell = Cell(
                    sim = self.sim,
                    habitat_type = self.select_random_cell_type(),
                    cell_id = cell_id,
                    prey_competition = self.sim.prey_competition)
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

    def initialize_snake_pop_discrete_preference(
            self, 
            death_probability, strike_success_probability_bush,
            strike_success_probability_open, energy_gain_per_krat,
            energy_cost, move_range,
            movement_frequency, move_preference,
            snake_genotype_frequencies, memory_length_cycles):
        isp = self.sim.initial_snake_pop
        for key, freq in snake_genotype_frequencies.items():
            pop = round(isp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                bush_preference_weight = float(key)
                open_preference_weight = (1-float(key))
                snake = org.Snake(sim = self.sim,
                            strike_success_probability_bush = strike_success_probability_bush,
                            strike_success_probability_open = strike_success_probability_open,
                            death_probability = death_probability,
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

    def initialize_snake_pop_continuous_preference(
            self, death_probability,
            strike_success_probability_bush, strike_success_probability_open,
            energy_gain_per_krat,energy_cost, move_range,
            movement_frequency, move_preference,
            memory_length_cycles):
        isp = self.sim.initial_snake_pop
        while isp > 0:
            cell = self.select_random_cell()
            bush_preference_weight = self.rng.uniform(0, 1)
            open_preference_weight = (1-float(bush_preference_weight))
            snake = org.Snake(sim = self.sim,
                        strike_success_probability_bush = strike_success_probability_bush,
                        strike_success_probability_open = strike_success_probability_open,
                        death_probability = death_probability,
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
            isp = isp-1

    def initialize_krat_pop_discrete_preference(
            self, 
            energy_gain_bush, energy_gain_open,
            energy_cost, move_range,
            movement_frequency, move_preference,
            krat_genotype_frequencies, memory_length_cycles):
        ikp = self.sim.initial_krat_pop
        for key, freq in krat_genotype_frequencies.items():
            pop = round(ikp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                bush_preference_weight = float(key)
                open_preference_weight = (1-float(key))
                cell = self.select_random_cell()
                krat = org.Krat(sim = self.sim,
                            energy_gain_bush = energy_gain_bush, #from bouskila
                            energy_gain_open = energy_gain_open, #from bouskila
                            energy_cost = energy_cost,
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

    def initialize_krat_pop_continuous_preference(
        self, 
        energy_gain_bush, energy_gain_open,
        energy_cost, move_range,
        movement_frequency, move_preference,
        memory_length_cycles):
        ikp = self.sim.initial_krat_pop
        while ikp > 0:
            cell = self.select_random_cell()
            bush_preference_weight = self.rng.uniform(0, 1)
            open_preference_weight = (1-float(bush_preference_weight))
            cell = self.select_random_cell()
            krat = org.Krat(sim = self.sim,
                        energy_gain_bush = energy_gain_bush, #from bouskila
                        energy_gain_open = energy_gain_open, #from bouskila
                        energy_cost = energy_cost,
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
            ikp = ikp-1

    def initialize_owl_pop(
            self, initial_owl_pop,
            move_range, strike_success_probability,
            open_preference_weight, bush_preference_weight):
        iop = initial_owl_pop
        while iop > 0:
            cell = self.select_random_cell()
            owl = org.Owl(sim = self.sim,
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
        for j, owl in enumerate(self.owl_move_pool):
            new_cell = owl[0]
            owl_object = owl[1]
            new_cell.add_owl(owl_object)
            owl_object.current_cell = new_cell 
        self.owl_move_pool = []

    def populate_total_org_list(self,total_org_list, cell_org_list):
        for org in cell_org_list:
            total_org_list.append(org)

    def genotype_sum_to_one_test(self, bush_pref, open_pref):
        '''Test to make sure the organisms preferences sum to 1 because they should represent probabilities.'''
        if round((bush_pref+open_pref),2) != 1:
            raise ValueError('Genotype of bush {}, open {} does not sum to 1'.format(bush_pref,open_pref))

    def no_mixed_habitat_preference_mutation_calc(self,bush_pref_weight,mutation_probabiliy):
        if bush_pref_weight > 1:
            bush_pref_weight = 1.0
        elif bush_pref_weight < 0:
            bush_pref_weight = 0.0
        new_bush_preference = bush_pref_weight
        if self.rng.random() < mutation_probabiliy:
            if abs(1.0 - bush_pref_weight) < 1e-6:
                new_bush_preference = 0
            else:
                new_bush_preference = 1
        return new_bush_preference

    def mixed_habitat_preference_mutation_calc(self,bush_pref_weight,mutation_std):
        new_bush_preference = self.rng.gauss(bush_pref_weight, mutation_std)
        if new_bush_preference > 1:
            new_bush_preference = 1
        elif new_bush_preference < 0:
            new_bush_preference = 0
        return new_bush_preference


    def preference_mutation_calc(self,bush_pref_weight, mutation_probabiliy, mutation_std):
        '''Checks if the mutation probability is met and if it is, randomly increases or decreases the bush preference value to be used for the next generation.''' 
        if self.sim.mixed_individuals:
            new_bush_preference = self.mixed_habitat_preference_mutation_calc(bush_pref_weight = bush_pref_weight, mutation_std = mutation_std)
        else:
            new_bush_preference = self.no_mixed_habitat_preference_mutation_calc(bush_pref_weight = bush_pref_weight,mutation_probabiliy = mutation_probabiliy)
        return new_bush_preference

    def next_gen_rep_dist_prep(self, total_org_list, mutation_probabiliy, mutation_std):
        '''returns a dictionary that has the bush preferences as the key and the relative weighted payoff as the values. 
        This relative weighted pay off is the sum of payoff associated with the bush preference of interest, divided by
        the total populations payoff accumulated over the generation. Works for any organism.'''
        new_gen_genotype = {}
        for org in total_org_list:
            self.genotype_sum_to_one_test(bush_pref = org.bush_preference_weight, open_pref = org.open_preference_weight)
            bush_pref_key = self.preference_mutation_calc(bush_pref_weight = org.bush_preference_weight, mutation_probabiliy = mutation_probabiliy, mutation_std = mutation_std)
            if org.energy_score < 0:
                payoff = 0
            else:
                payoff = org.energy_score
            if bush_pref_key not in new_gen_genotype:
                new_gen_genotype[bush_pref_key] = []
                new_gen_genotype[bush_pref_key].append(payoff)
            else:
                new_gen_genotype[bush_pref_key].append(payoff)
        population_payoff_sum = sum(list(chain(*new_gen_genotype.values())))
        if population_payoff_sum > 0:
            geno_dict = {key: sum(value)/population_payoff_sum for (key,value) in new_gen_genotype.items()}
        else:
            geno_dict = {}
        return geno_dict


    def iter_through_cells_reproduction(self):
        #Snakes and Krats
        if (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.snake_reproduction_freq) == 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_krat_list, cell_org_list= cell.krats) #Krat reproduction
                    cell.clean_krat_list()
                    self.populate_total_org_list(total_org_list = self.total_snake_list, cell_org_list= cell.snakes) #snake reproduction
                    cell.clean_snake_list()
        #Just Krats
        elif (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.snake_reproduction_freq) != 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_krat_list, cell_org_list= cell.krats) #Krat reproduction
                    cell.clean_krat_list()
        #just Snakes
        elif (self.sim.cycle % self.sim.krat_reproduction_freq) != 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.snake_reproduction_freq) == 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_snake_list, cell_org_list= cell.snakes) #snake reproduction
                    cell.clean_snake_list()

    def krat_reproduction(self):
        '''Generates the new generaton of krats from information from the old generation and a calculation of how well agents in the previous generation
        associated with certain habitat preference genotypes preformed.'''
        if len(self.total_krat_list) > 0:
            next_gen_dist = self.next_gen_rep_dist_prep(total_org_list = self.total_krat_list,
                                                        mutation_probabiliy = self.sim.krat_mutation_probability,
                                                        mutation_std = self.sim.krat_mutation_std)
            move_range = self.total_krat_list[0].move_range
            movement_frequency = self.total_krat_list[0].movement_frequency
            energy_gain_bush = self.total_krat_list[0].energy_gain_bush
            energy_gain_open = self.total_krat_list[0].energy_gain_open 
            energy_cost = self.total_krat_list[0].energy_cost
            move_preference = self.total_krat_list[0].move_preference
            if move_preference:
                memory_length_cycles = self.total_krat_list[0].memory_length_cycles
            else:
                memory_length_cycles = None
            self.total_krat_list = []
            self.initialize_krat_pop_discrete_preference(
                move_range = move_range,
                movement_frequency = movement_frequency,
                energy_gain_bush = energy_gain_bush, #from bouskila
                energy_gain_open = energy_gain_open, #from bouskila
                energy_cost = energy_cost,
                move_preference = move_preference,
                memory_length_cycles = memory_length_cycles,
                krat_genotype_frequencies = next_gen_dist
                )

    def snake_reproduction(self):
        '''Generates the new generaton of snakes from information from the old generation and a calculation of how well agents in the previous generation
        associated with certain habitat preference genotypes preformed.'''
        if len(self.total_snake_list) > 0:
            next_gen_dist = self.next_gen_rep_dist_prep(total_org_list = self.total_snake_list,
                                                        mutation_probabiliy = self.sim.snake_mutation_probability,
                                                        mutation_std = self.sim.snake_mutation_std)
            move_range = self.total_snake_list[0].move_range
            strike_success_probability_bush = self.total_snake_list[0].strike_success_probability_bush
            strike_success_probability_open = self.total_snake_list[0].strike_success_probability_open
            death_probability = self.total_snake_list[0].death_probability
            energy_gain_per_krat = self.total_snake_list[0].energy_gain_per_krat
            energy_cost = self.total_snake_list[0].energy_cost
            movement_frequency = self.total_snake_list[0].movement_frequency
            move_preference = self.total_snake_list[0].move_preference
            if move_preference:
                memory_length_cycles = self.total_snake_list[0].memory_length_cycles
            else:
                memory_length_cycles = None
            self.total_snake_list = []
            self.initialize_snake_pop_discrete_preference(
                    strike_success_probability_bush = strike_success_probability_bush,
                    strike_success_probability_open = strike_success_probability_open,
                    death_probability = death_probability,
                    energy_gain_per_krat = energy_gain_per_krat,
                    energy_cost = energy_cost,
                    move_range = move_range,
                    movement_frequency = movement_frequency,
                    move_preference = move_preference,
                    memory_length_cycles = memory_length_cycles,
                    snake_genotype_frequencies = next_gen_dist
                    )

    def iter_through_cells_activity(self):
        '''Iterates through all the cells in the landscape and runs krat, snake, and owl acivity. Predators move before krats. Which species moves first
        depends on the proportion of the species to other predators in the cell and is used as a probability check. .'''
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
                cell.krat_activity_pulse_behavior()



    def landscape_dynamics(self):
        '''Main function for the landscape, runs all of the appropriate functions for a cycle such as the relocation, activity, and reproduction algorithms
        for all organisms.'''
        self.total_krats = 0
        self.total_snakes = 0
        self.total_owls = 0
        self.iter_through_cells_activity()
        self.relocate_krats()
        self.relocate_snakes()
        self.relocate_owls()
        self.iter_through_cells_reproduction()
        if (self.sim.cycle % self.sim.krat_reproduction_freq) == 0 and self.sim.cycle != 0:
            self.krat_reproduction()
        if (self.sim.cycle % self.sim.snake_reproduction_freq) == 0 and self.sim.cycle != 0:
            self.snake_reproduction()



class Sim(object):
    '''
    loads the initial conditions, initializes the landscape and organism populations, and runs the sim for the appropraite amount of cycles.
    Once the sim concludes two csvs are generated with krat and snake information.
    Args:
        initial_conditions_file_path -- file path for a json file with all the appropriate initial conditions of interest for the simulation.
        rng -- random number generator object. (default is none)
    Attributes:
        snake_info -- an array with info on every snake object per cycle.
        krat_info -- an array with info on every krat object per cycle.
        cycle -- a genral time unit. Starts at zero and the simulation runs until the cycle reaches end time. (int)
        end_time -- the length of the simulation in cycles. (int)
        initial_krat_pop -- the number of krats in the population. This is a constant interager. (int)
        initial_snake_pop -- the number of snake in the population. This is a constant interager. (int)
        krat_reproduction_freq -- the length in cycles until the new generation of krats is formed.
        snake_reproduction_freq -- the length in cycles until the new generation of snakes is formed.
        krat_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for krats. (int)
        snake_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for snakes. (int)
        krat_mutation_probability -- a probabilty less than one that the bush preference of an individual krat offspring accrues a mutation to it's bush preference.
        snake_mutation_probability -- a probabilty less than one that the bush preference of an individual snake offspring accrues a mutation to it's bush preference.

    '''
    def __init__(self,initial_conditions_file_path, krat_tsv_output_file_path, snake_tsv_output_file_path,rng=None):
        self.initial_conditions_file_path = initial_conditions_file_path
        self.snake_info = []
        self.krat_info = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.krat_file_path = krat_tsv_output_file_path
        self.snake_file_path = snake_tsv_output_file_path
        self.cycle = 0
        

    def genotype_freq_test(self,genotype_freq_dict):
        if sum(genotype_freq_dict.values()) != 1:
            raise Exception("Genotype frequencies do not sum to 1.")

    def config_sim_species_attributes(self,config_d):
        self.mixed_individuals = config_d["mixed_preference_individuals"]
        self.prey_competition = config_d["prey_competition"]
        self.end_time = config_d["cycles_of_sim"]
        self.initial_krat_pop = config_d["initial_krat_pop"]
        self.initial_snake_pop = config_d["initial_snake_pop"]
        self.krat_reproduction_freq = config_d["krat_reproduction_freq_per_x_cycles"]
        self.snake_reproduction_freq = config_d["snake_reproduction_freq_per_x_cycles"]
        self.krat_mutation_std = config_d["krat_mutation_std"]
        self.snake_mutation_std = config_d["snake_mutation_std"]
        self.krat_mutation_probability = config_d["krat_mutation_probability"]
        self.snake_mutation_probability = config_d["snake_mutation_probability"]
        self.krat_data_sample_frequency = config_d["krat_data_sample_freq"]
        self.snake_data_sample_frequency = config_d["snake_data_sample_freq"]

    def initialize_snake_pop(self,config_d):
        if self.mixed_individuals:
            self.landscape.initialize_snake_pop_continuous_preference(
                strike_success_probability_bush = config_d["snake_strike_success_probability_bush"],
                strike_success_probability_open = config_d["snake_strike_success_probability_open"],
                death_probability = config_d["snake_death_probability"],
                energy_gain_per_krat = config_d["snake_energy_gain"],
                energy_cost = config_d["snake_energy_cost"],
                move_range = config_d["snake_move_range"],
                movement_frequency = config_d["snake_movement_frequency_per_x_cycles"],
                move_preference =config_d["move_preference_algorithm"],
                memory_length_cycles = config_d["memory_length_snake"],
            )
        else:
            snake_genotype_frequencies = {1:(1/2), 0:(1/2)}
            self.landscape.initialize_snake_pop_discrete_preference(
                strike_success_probability_bush = config_d["snake_strike_success_probability_bush"],
                strike_success_probability_open = config_d["snake_strike_success_probability_open"],
                death_probability = config_d["snake_death_probability"],
                energy_gain_per_krat = config_d["snake_energy_gain"],
                energy_cost = config_d["snake_energy_cost"],
                move_range = config_d["snake_move_range"],
                movement_frequency = config_d["snake_movement_frequency_per_x_cycles"],
                move_preference =config_d["move_preference_algorithm"],
                memory_length_cycles = config_d["memory_length_snake"],
                snake_genotype_frequencies = snake_genotype_frequencies
            )

    def initialize_krat_pop(self,config_d):
        if self.mixed_individuals:
                self.landscape.initialize_krat_pop_continuous_preference(
                move_range = config_d["krat_move_range"],
                movement_frequency = config_d["krat_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["krat_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["krat_energy_gain_open"], #from bouskila
                energy_cost=config_d["krat_energy_cost"],
                move_preference =config_d["move_preference_algorithm"],
                memory_length_cycles = config_d["memory_length_krat"],
                )
        else:
            krat_genotype_frequencies = {1:(1/2), 0:(1/2)}
            self.landscape.initialize_krat_pop_discrete_preference(
                move_range = config_d["krat_move_range"],
                movement_frequency = config_d["krat_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["krat_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["krat_energy_gain_open"], #from bouskila
                energy_cost=config_d["krat_energy_cost"],
                move_preference =config_d["move_preference_algorithm"],
                memory_length_cycles = config_d["memory_length_krat"],
                krat_genotype_frequencies = krat_genotype_frequencies
                )




    def configure(self, config_d):
        self.config_sim_species_attributes(config_d = config_d)
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"]
                )
        self.landscape.build()
        self.initialize_snake_pop(config_d = config_d)
        self.initialize_krat_pop(config_d = config_d)
        self.landscape.initialize_owl_pop(
                initial_owl_pop=config_d["initial_owl_pop"],
                move_range = config_d["owl_move_range"],
                strike_success_probability = config_d["owl_catch_success"],
                open_preference_weight = 1,
                bush_preference_weight = 0
                )

    def round_down(self,x, a):
        return round(math.floor(x / a) * a,2)

    def read_configuration_file(self):
        with open(self.initial_conditions_file_path) as f:
            config_d = json.load(f)
        self.configure(config_d)

    def main(self):
        start = round(time.time())
        self.read_configuration_file()
        for i in range(0,self.end_time,1):
            self.landscape.landscape_dynamics()
            self.cycle += 1
        self.report_writer(array = self.krat_info,file_name = self.krat_file_path )
        self.report_writer(array = self.snake_info,file_name = self.snake_file_path )
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
            tsv_output = csv.writer(file, delimiter='\t')
            tsv_output.writerow(array)


if __name__ ==  "__main__":
    #sim = Sim(initial_conditions_file_path = 'data.txt', krat_tsv_output_file_path = 'krat_energy.tsv', snake_tsv_output_file_path = 'snake_energy.tsv')
    #sim.main()
    print('test')



