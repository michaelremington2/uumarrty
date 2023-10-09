#!/usr/bin/python
from enum import Enum,auto
import random
from json import load
from uumarrty import organismsim as org
from uumarrty import cell as cl
from itertools import chain
import time
import csv
import uuid
import os

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

    def __init__(self,sim,size_x,size_y,microhabitat_open_bush_proportions,_output_landscape=False,_output_landscape_file_path=None):
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
        self._output_landscape = _output_landscape
        if _output_landscape:
            self._output_landscape_file_path = _output_landscape_file_path
            with open(self._output_landscape_file_path, "w") as my_empty_csv:
                pass

    def build(self):
        '''Populates the attribute cells with an x by y array'''
        self.cells = []
        self.cell_mh_dict = {'BUSH':[],'OPEN':[]}
        for yidx in range(self.cells_y_rows):
            temp_x = []
            for xidx in range(self.cells_x_columns):
                cell_id = (yidx,xidx)
                cell = cl.Cell(
                    sim = self.sim,
                    habitat_type = self.select_random_cell_type(),
                    cell_id = cell_id,
                    prey_competition = self.sim.prey_competition)
                self.cell_mh_dict[cell.habitat_type[0].name].append(cell)
                if self._output_landscape:
                    self._output_landscape_row_append(cell)
                temp_x.append(cell)
            self.cells.append(temp_x)


    def _output_landscape_row_append(self,cell):
        '''This function generates a csv that has the information on every cell that generates the lanscape.'''
        from csv import writer
        cell_id = cell.cell_id 
        cell_microhabitat_type = cell.habitat_type[0].name  
        fields=[cell_id, cell_microhabitat_type]
        with open(self._output_landscape_file_path, 'a') as f:
            writer = writer(f)
            writer.writerow(fields)

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
            movement_frequency, snake_genotype_frequencies):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
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
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight
                            )
                cell.add_snake(snake)
                snake.current_cell=cell
                #snake.generate_snake_stats()
                pop = pop-1

    def initialize_snake_pop_continuous_preference(
            self, death_probability,
            strike_success_probability_bush, strike_success_probability_open,
            energy_gain_per_krat,energy_cost, move_range,
            movement_frequency):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
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
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight
                        )
            cell.add_snake(snake)
            snake.current_cell=cell
            #snake.generate_snake_stats()
            isp = isp-1

    def initialize_krat_pop_discrete_preference(
            self, 
            energy_gain_bush, energy_gain_open,
            energy_cost, move_range,
            movement_frequency, krat_genotype_frequencies):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
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
                            home_cell = cell,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight)
                cell.add_krat(krat)
                krat.current_cell=cell
                #krat.generate_krat_stats()
                pop = pop-1

    def initialize_krat_pop_continuous_preference(
        self, 
        energy_gain_bush, energy_gain_open,
        energy_cost, move_range,
        movement_frequency):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
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
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight)
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

    def no_mixed_habitat_preference_mutation_calc(self,bush_pref_weight,mutation_probability):
        if bush_pref_weight > 1:
            bush_pref_weight = 1.0
        elif bush_pref_weight < 0:
            bush_pref_weight = 0.0
        new_bush_preference = bush_pref_weight
        if self.rng.random() < mutation_probability:
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


    def preference_mutation_calc(self,bush_pref_weight, mutation_probability, mutation_std):
        '''Checks if the mutation probability is met and if it is, randomly increases or decreases the bush preference value to be used for the next generation.''' 
        if self.sim.mixed_individuals:
            new_bush_preference = self.mixed_habitat_preference_mutation_calc(bush_pref_weight = bush_pref_weight, mutation_std = mutation_std)
        else:
            new_bush_preference = self.no_mixed_habitat_preference_mutation_calc(bush_pref_weight = bush_pref_weight,mutation_probability = mutation_probability)
        return new_bush_preference

    def next_gen_rep_dist_prep(self, total_org_list, mutation_probability, mutation_std): # Spelling error
        '''returns a dictionary that has the bush preferences as the key and the relative weighted payoff as the values. 
        This relative weighted pay off is the sum of payoff associated with the bush preference of interest, divided by
        the total populations payoff accumulated over the generation. Works for any organism.'''
        new_gen_genotype = {}
        for org in total_org_list:
            self.genotype_sum_to_one_test(bush_pref = org.bush_preference_weight, open_pref = org.open_preference_weight)
            bush_pref_key = self.preference_mutation_calc(bush_pref_weight = org.bush_preference_weight, mutation_probability= mutation_probability, mutation_std = mutation_std)
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
            ikp = self.sim.initial_krat_pop
            parent_krat_pop = self.total_krat_list
            parent_krat_payoffs = [krat.energy_score for krat in parent_krat_pop]
            self.total_krat_list = []
            while ikp > 0:
                cell = self.select_random_cell()
                parent = self.rng.choices(parent_krat_pop, weights=parent_krat_payoffs, k = 1)
                parent = parent[0]
                bush_preference_weight = self.preference_mutation_calc(bush_pref_weight = parent.bush_preference_weight, mutation_probability= self.sim.krat_mutation_probability, mutation_std = self.sim.krat_mutation_std)
                open_preference_weight = (1-float(bush_preference_weight))
                cell = self.select_random_cell()
                krat = org.Krat(sim = self.sim,
                            energy_gain_bush = parent.energy_gain_bush, #from bouskila
                            energy_gain_open = parent.energy_gain_open, #from bouskila
                            energy_cost = parent.energy_cost,
                            move_range = parent.move_range,
                            movement_frequency = parent.movement_frequency,
                            home_cell= cell,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight)
                cell.add_krat(krat)
                krat.current_cell=cell
                ikp = ikp-1
            self.sim.krat_generation += 1
        else:
            raise ValueError('krat pop extinct')

    def snake_reproduction(self):
        '''Generates the new generaton of snakes from information from the old generation and a calculation of how well agents in the previous generation
        associated with certain habitat preference genotypes preformed.'''
        if len(self.total_snake_list) > 0:
            isp = self.sim.initial_snake_pop
            parent_snake_pop = self.total_snake_list
            parent_snake_payoffs = [snake.energy_score for snake in parent_snake_pop]
            self.total_snake_list = []
            while isp > 0:
                cell = self.select_random_cell()
                parent = self.rng.choices(parent_snake_pop, weights=parent_snake_payoffs, k = 1)
                parent = parent[0]
                bush_preference_weight = self.preference_mutation_calc(bush_pref_weight = parent.bush_preference_weight, mutation_probability = self.sim.snake_mutation_probability, mutation_std = self.sim.snake_mutation_std)
                open_preference_weight = (1-float(bush_preference_weight))
                cell = self.select_random_cell()
                snake = org.Snake(sim = self.sim,
                            strike_success_probability_bush = parent.strike_success_probability_bush,
                            strike_success_probability_open = parent.strike_success_probability_open,
                            death_probability = parent.death_probability,
                            energy_gain_per_krat = parent.energy_gain_per_krat,
                            energy_cost = parent.energy_cost,
                            move_range = parent.move_range,
                            movement_frequency = parent.movement_frequency,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight
                            )
                cell.add_snake(snake)
                snake.current_cell=cell
                isp = isp-1
            self.sim.snake_generation += 1
        else:
            raise ValueError('snake pop extinct')

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