#!/usr/bin/python
from enum import Enum,auto
import random
from json import load
from uumarrty import organismsim as org
from itertools import chain
import time
import csv
import uuid
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
        prey_items -- a list that holds prey_item objects. (list)
        predator_items -- a list that holds sake objects. (list)
        landscape -- the landscape object the cell operates in.
        rng -- a random number operator object.
    '''
    def __init__(self, sim, habitat_type,cell_id,prey_competition=False):
        self.sim = sim
        self.prey_items = []
        self.predator_items = []
        self.owls = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.cell_id = cell_id
        self.prey_competition = prey_competition     
        self.rng = self.sim.rng

    def __hash__(self):
        return id(self)

    def add_prey_item(self, prey_item):
        '''Add a prey_item to the population of this cells prey_items'''
        self.prey_items.append(prey_item)

    def add_predator_item(self, predator_item):
        '''Add a predator_item to the population of this cells predator_items'''
        self.predator_items.append(predator_item)

    def add_owl(self,owl):
        '''adds an owl object to the landscape.'''
        self.owls.append(owl)

    def select_prey_item(self,prey_item_index = None):
        '''returns a random prey_item object if no specific index is provided.'''
        if prey_item_index == None:
            prey_item_index = self.rng.randint(0,len(self.prey_items)-1)
        prey_item = self.prey_items[prey_item_index]
        return prey_item

    def select_predator_item(self,predator_item_index = None):
        '''returns a random predator_item object if no specific index is provided.'''
        if predator_item_index == None:
            predator_item_index = self.rng.randint(0,len(self.predator_item)-1)
        predator_item = self.predator_items[predator_item_index]
        return predator_item

    def pop_prey_item(self,prey_item_index):
        '''Selects a prey_item at random from population and removes it and returns the object '''
        return self.prey_items.pop(prey_item_index)

    def pop_predator_item(self,predator_item_index):
        '''Selects a predator_item at random from population and removes it and returns the object '''
        return self.predator_items.pop(predator_item_index)

    def clean_prey_item_list(self):
        '''creates a fresh list for the attribute prey_items'''
        self.prey_items = []

    def clean_predator_item_list(self):
        '''creates a fresh list for the attribute predator_items'''
        self.predator_items = []

    def cell_over_populated(self):
        '''test that makes sure cells don't become overpopulated and break sim'''
        if len(self.prey_items) > self.sim.initial_prey_item_pop:
            raise ValueError("prey_items mating too much")
        if len(self.predator_items) > self.sim.initial_predator_item_pop:
            raise ValueError("predator_items mating too much")

    def prey_item_move(self, prey_item,moving_prey_item_list,return_home=False):
        '''runs the prey_item movement algorithm and moves the prey_item from the cell to a temp list in the landscape. 
        Optional can designate the prey_item to return to designated nest cell tied to the prey_item object.'''
        if return_home== True:
            new_cell = prey_item.return_home()
        else:
            new_cell = prey_item.organism_movement()
        if new_cell != self:
            moving_prey_item = (new_cell,prey_item,self)
            self.landscape.prey_item_move_pool.append(moving_prey_item)
            moving_prey_item_list.append(prey_item)

    def predator_item_move(self,predator_item,moving_predator_item_list):
        '''runs the predator_item movement algorithm and moves the prey_item from the cell to a temp list in the landscape. '''
        new_cell = predator_item.organism_movement()
        if new_cell != self:
            moving_predator_item = (new_cell,predator_item,self)
            self.landscape.predator_item_move_pool.append(moving_predator_item)
            moving_predator_item_list.append(predator_item)

    def owl_move(self,owl,moving_owl_list):
        '''runs the owl movement algorithm and moves the prey_item from the cell to a temp list in the landscape. '''
        new_cell = owl.organism_movement()
        if new_cell != self:
            moving_owl = (new_cell,owl,self)
            self.landscape.owl_move_pool.append(moving_owl)
            moving_owl_list.append(owl)             

    def prey_item_predation_by_predator_item(self,predator_item):
        '''determines whether or not the predator_item that was passed into the function successfully kills and obtains payoff of a prey_item that shares the cell with it.'''
        live_prey_items = [prey_item for prey_item in self.prey_items if prey_item.alive] 
        ss = predator_item.calc_strike_success_probability(self)
        energy_cost = predator_item.energy_cost
        if len(live_prey_items) > 0 and self.rng.random() < ss:
            prey_item_index = self.rng.randint(0,len(live_prey_items)-1)
            prey_item = self.select_prey_item(prey_item_index = prey_item_index)
            prey_item.alive = False
            energy_gain = predator_item.energy_gain_per_prey_item              
        else:
            energy_gain = 0
        energy_delta = (energy_gain - energy_cost)
        predator_item.energy_score += energy_delta

    def prey_item_predation_by_owl(self,owl):
        '''determines whether or not the owl that was passed into the function successfully kills and obtains payoff of a prey_item that shares the cell with it.'''
        live_prey_items = [prey_item for prey_item in self.prey_items if prey_item.alive] 
        if len(live_prey_items) > 0 and self.rng.random() < owl.strike_success_probability and self.habitat_type[0].name == 'OPEN':
            prey_item_index = self.rng.randint(0,len(live_prey_items)-1)
            prey_item = self.select_prey_item(prey_item_index = prey_item_index)
            prey_item.alive = False

    def foraging_rat(self,prey_item):
        '''Provides prey_item with appropriate pay off for foraging in the cell.'''
        if self.prey_competition:
            prey_item_energy_gain = prey_item.calc_energy_gain(self)/len(self.prey_items)
        else:
            prey_item_energy_gain = prey_item.calc_energy_gain(self)
        prey_item_energy_cost = prey_item.calc_energy_cost()
        energy_delta = (prey_item_energy_gain - prey_item_energy_cost)
        prey_item.energy_score += energy_delta

    def prey_item_activity_pulse_behavior(self):
        """ prey_item function, this is the general behavior of either moving or foraging of the prey_item for one activity pulse."""
        moving_prey_items = []
        for prey_item in self.prey_items:
            if (self.sim.cycle % self.sim.data_sample_frequency) == 0 and prey_item.alive:
                prey_item.generate_prey_item_stats()
            self.foraging_rat(prey_item)
            if self.sim.cycle % prey_item.movement_frequency == 0 and self.sim.cycle != 0 and prey_item.alive:
                self.prey_item_move(prey_item,moving_prey_item_list = moving_prey_items)           
        self.prey_items = [prey_item for prey_item in self.prey_items if prey_item not in moving_prey_items and prey_item.alive]     

    def predator_item_activity_pulse_behavior(self):
        """ predator_item function, this is the general behavior of either moving or hunting of the prey_item for one activity pulse."""
        moving_predator_items = []
        for predator_item in self.predator_items:
            predator_item.predator_item_death()
            if (self.sim.cycle % self.sim.data_sample_frequency) == 0:
                predator_item.generate_predator_item_stats()
            self.prey_item_predation_by_predator_item(predator_item)
            if self.sim.cycle % predator_item.movement_frequency == 0 and self.sim.cycle != 0: 
                self.predator_item_move(predator_item, moving_predator_item_list=moving_predator_items)            
        self.predator_items = [predator_item for predator_item in self.predator_items if predator_item not in moving_predator_items and predator_item.alive]

    def owl_activity_pulse_behavior(self):
        moving_owls = []
        for owl in self.owls:
            self.prey_item_predation_by_owl(owl)
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
        prey_item_move_pool -- a temporary list that holds prey_items that need to be relocated to different cells in the landscape.
        predator_item_move_pool -- a temporary list that holds predator_items that need to be relocated to different cells in the landscape.
        owl_move_pool = -- a temporary list that holds owls that need to be relocated to different cells in the landscape.
        total_prey_item_list -- a list of the prey_item objects used for analysis and reproduction.
        total_predator_item_list -- a list of the predator_item objects used for analysis and reproduction.
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
        self.prey_item_move_pool = []
        self.predator_item_move_pool = []
        self.owl_move_pool = []
        self.total_prey_item_list = [] 
        self.total_predator_item_list = []
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
                cell = Cell(
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

    def initialize_predator_item_pop_discrete_preference(
            self, 
            death_probability, strike_success_probability_bush,
            strike_success_probability_open, energy_gain_per_prey_item,
            energy_cost, move_range,
            movement_frequency, predator_item_genotype_frequencies):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        isp = self.sim.initial_predator_item_pop
        for key, freq in predator_item_genotype_frequencies.items():
            pop = round(isp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                bush_preference_weight = float(key)
                open_preference_weight = (1-float(key))
                predator_item = org.Predator(sim = self.sim,
                            strike_success_probability_bush = strike_success_probability_bush,
                            strike_success_probability_open = strike_success_probability_open,
                            death_probability = death_probability,
                            energy_gain_per_prey_item = energy_gain_per_prey_item,
                            energy_cost = energy_cost,
                            move_range = move_range,
                            movement_frequency = movement_frequency,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight
                            )
                cell.add_predator_item(predator_item)
                predator_item.current_cell=cell
                #predator_item.generate_predator_item_stats()
                pop = pop-1

    def initialize_predator_item_pop_continuous_preference(
            self, death_probability,
            strike_success_probability_bush, strike_success_probability_open,
            energy_gain_per_prey_item,energy_cost, move_range,
            movement_frequency):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        isp = self.sim.initial_predator_item_pop
        while isp > 0:
            cell = self.select_random_cell()
            bush_preference_weight = self.rng.uniform(0, 1)
            open_preference_weight = (1-float(bush_preference_weight))
            predator_item = org.Predator(sim = self.sim,
                        strike_success_probability_bush = strike_success_probability_bush,
                        strike_success_probability_open = strike_success_probability_open,
                        death_probability = death_probability,
                        energy_gain_per_prey_item = energy_gain_per_prey_item,
                        energy_cost = energy_cost,
                        move_range = move_range,
                        movement_frequency = movement_frequency,
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight
                        )
            cell.add_predator_item(predator_item)
            predator_item.current_cell=cell
            #predator_item.generate_predator_item_stats()
            isp = isp-1

    def initialize_prey_item_pop_discrete_preference(
            self, 
            energy_gain_bush, energy_gain_open,
            energy_cost, move_range,
            movement_frequency, prey_item_genotype_frequencies):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        ikp = self.sim.initial_prey_item_pop
        for key, freq in prey_item_genotype_frequencies.items():
            pop = round(ikp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                bush_preference_weight = float(key)
                open_preference_weight = (1-float(key))
                cell = self.select_random_cell()
                prey_item = org.Prey(sim = self.sim,
                            energy_gain_bush = energy_gain_bush, #from bouskila
                            energy_gain_open = energy_gain_open, #from bouskila
                            energy_cost = energy_cost,
                            move_range = move_range,
                            movement_frequency = movement_frequency,
                            home_cell = cell,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight)
                cell.add_prey_item(prey_item)
                prey_item.current_cell=cell
                #prey_item.generate_prey_item_stats()
                pop = pop-1

    def initialize_prey_item_pop_continuous_preference(
        self, 
        energy_gain_bush, energy_gain_open,
        energy_cost, move_range,
        movement_frequency):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        ikp = self.sim.initial_prey_item_pop
        while ikp > 0:
            cell = self.select_random_cell()
            bush_preference_weight = self.rng.uniform(0, 1)
            open_preference_weight = (1-float(bush_preference_weight))
            cell = self.select_random_cell()
            prey_item = org.Prey(sim = self.sim,
                        energy_gain_bush = energy_gain_bush, #from bouskila
                        energy_gain_open = energy_gain_open, #from bouskila
                        energy_cost = energy_cost,
                        move_range = move_range,
                        movement_frequency = movement_frequency,
                        home_cell= cell,
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight)
            cell.add_prey_item(prey_item)
            prey_item.current_cell=cell
                #prey_item.generate_prey_item_stats()
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

    def relocate_prey_items(self):
        for i, prey_item in enumerate(self.prey_item_move_pool):
            new_cell = prey_item[0]
            prey_item_object = prey_item[1]
            new_cell.add_prey_item(prey_item_object)
            prey_item_object.current_cell = new_cell
        self.prey_item_move_pool = []

    def relocate_predator_items(self):
        for j, predator_item in enumerate(self.Predator_item_move_pool):
            new_cell = predator_item[0]
            predator_item_object = predator_item[1]
            new_cell.add_predator_item(predator_item_object)
            predator_item_object.current_cell = new_cell 
        self.predator_item_move_pool = []

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


    # 200
    # 150
    # bush 1000 payoff
    # open 300
    # (1000/1300)*200 bush
    # (300/1300)*200 open


    def iter_through_cells_reproduction(self):
        #predator_items and prey_items
        if (self.sim.cycle % self.sim.prey_item_reproduction_freq) == 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.predator_item_reproduction_freq) == 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_prey_item_list, cell_org_list= cell.prey_items) #prey_item reproduction
                    cell.clean_prey_item_list()
                    self.populate_total_org_list(total_org_list = self.total_predator_item_list, cell_org_list= cell.predator_items) #predator_item reproduction
                    cell.clean_predator_item_list()
        #Just prey_items
        elif (self.sim.cycle % self.sim.prey_item_reproduction_freq) == 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.predator_item_reproduction_freq) != 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_prey_item_list, cell_org_list= cell.prey_items) #prey_item reproduction
                    cell.clean_prey_item_list()
        #just predator_items
        elif (self.sim.cycle % self.sim.prey_item_reproduction_freq) != 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.predator_item_reproduction_freq) == 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_predator_item_list, cell_org_list= cell.predator_items) #predator_item reproduction
                    cell.clean_predator_item_list()

    def prey_item_reproduction(self):
        '''Generates the new generaton of prey_items from information from the old generation and a calculation of how well agents in the previous generation
        associated with certain habitat preference genotypes preformed.'''
        if len(self.total_prey_item_list) > 0:
            ikp = self.sim.initial_prey_item_pop
            parent_prey_item_pop = self.total_prey_item_list
            parent_prey_item_payoffs = [prey_item.energy_score for prey_item in parent_prey_item_pop]
            self.total_prey_item_list = []
            while ikp > 0:
                cell = self.select_random_cell()
                parent = self.rng.choices(parent_prey_item_pop, weights=parent_prey_item_payoffs, k = 1)
                parent = parent[0]
                bush_preference_weight = self.preference_mutation_calc(bush_pref_weight = parent.bush_preference_weight, mutation_probability= self.sim.prey_item_mutation_probability, mutation_std = self.sim.prey_item_mutation_std)
                open_preference_weight = (1-float(bush_preference_weight))
                cell = self.select_random_cell()
                prey_item = org.Prey(sim = self.sim,
                            energy_gain_bush = parent.energy_gain_bush, #from bouskila
                            energy_gain_open = parent.energy_gain_open, #from bouskila
                            energy_cost = parent.energy_cost,
                            move_range = parent.move_range,
                            movement_frequency = parent.movement_frequency,
                            home_cell= cell,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight)
                cell.add_prey_item(prey_item)
                prey_item.current_cell=cell
                ikp = ikp-1
            self.sim.prey_item_generation += 1

    def predator_item_reproduction(self):
        '''Generates the new generaton of predator_items from information from the old generation and a calculation of how well agents in the previous generation
        associated with certain habitat preference genotypes preformed.'''
        if len(self.total_predator_item_list) > 0:
            isp = self.sim.initial_predator_item_pop
            parent_predator_item_pop = self.total_predator_item_list
            parent_predator_item_payoffs = [predator_item.energy_score for predator_item in parent_predator_item_pop]
            self.total_predator_item_list = []
            while isp > 0:
                cell = self.select_random_cell()
                parent = self.rng.choices(parent_predator_item_pop, weights=parent_predator_item_payoffs, k = 1)
                parent = parent[0]
                bush_preference_weight = self.preference_mutation_calc(bush_pref_weight = parent.bush_preference_weight, mutation_probability = self.sim.predator_item_mutation_probability, mutation_std = self.sim.predator_item_mutation_std)
                open_preference_weight = (1-float(bush_preference_weight))
                cell = self.select_random_cell()
                predator_item = org.Predator(sim = self.sim,
                            strike_success_probability_bush = parent.strike_success_probability_bush,
                            strike_success_probability_open = parent.strike_success_probability_open,
                            death_probability = parent.death_probability,
                            energy_gain_per_prey_item = parent.energy_gain_per_prey_item,
                            energy_cost = parent.energy_cost,
                            move_range = parent.move_range,
                            movement_frequency = parent.movement_frequency,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight
                            )
                cell.add_predator_item(predator_item)
                predator_item.current_cell=cell
                isp = isp-1
            self.sim.predator_item_generation += 1

    def iter_through_cells_activity(self):
        '''Iterates through all the cells in the landscape and runs prey_item, predator_item, and owl acivity. Predators move before prey_items. Which species moves first
        depends on the proportion of the species to other predators in the cell and is used as a probability check. .'''
        for cell_width in self.cells:
            for cell in cell_width:
                self.total_prey_items += len(cell.prey_items)
                self.total_predator_items += len(cell.predator_items)
                self.total_owls += len(cell.owls)
                cell.cell_over_populated()
                preds = len(cell.predator_items) + len(cell.owls)
                if preds > 0:
                    owl_move_first_probability = len(cell.owls)/preds
                    if owl_move_first_probability < self.rng.random() and owl_move_first_probability > 0:
                        cell.owl_activity_pulse_behavior()
                        cell.predator_item_activity_pulse_behavior()
                    else:
                        cell.predator_item_activity_pulse_behavior()
                        cell.owl_activity_pulse_behavior()
                cell.prey_item_activity_pulse_behavior()



    def landscape_dynamics(self):
        '''Main function for the landscape, runs all of the appropriate functions for a cycle such as the relocation, activity, and reproduction algorithms
        for all organisms.'''
        self.total_prey_items = 0
        self.total_predator_items = 0
        self.total_owls = 0
        self.iter_through_cells_activity()
        self.relocate_prey_items()
        self.relocate_predator_items()
        self.relocate_owls()
        self.iter_through_cells_reproduction()
        if (self.sim.cycle % self.sim.prey_item_reproduction_freq) == 0 and self.sim.cycle != 0:
            self.prey_item_reproduction()
        if (self.sim.cycle % self.sim.predator_item_reproduction_freq) == 0 and self.sim.cycle != 0:
            self.predator_item_reproduction()



class Sim(object):
    '''
    loads the initial conditions, initializes the landscape and organism populations, and runs the sim for the appropraite amount of cycles.
    Once the sim concludes two csvs are generated with prey_item and predator_item information.
    Args:
        initial_conditions_file_path -- file path for a json file with all the appropriate initial conditions of interest for the simulation.
        rng -- random number generator object. (default is none)
    Attributes:
        predator_item_info -- an array with info on every predator_item object per cycle.
        prey_item_info -- an array with info on every prey_item object per cycle.
        cycle -- a genral time unit. Starts at zero and the simulation runs until the cycle reaches end time. (int)
        end_time -- the length of the simulation in cycles. (int)
        initial_prey_item_pop -- the number of prey_items in the population. This is a constant integer. (int)
        initial_predator_item_pop -- the number of predator_item in the population. This is a constant integer. (int)
        prey_item_reproduction_freq -- the length in cycles until the new generation of prey_items is formed.
        predator_item_reproduction_freq -- the length in cycles until the new generation of predator_items is formed.
        prey_item_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for prey_items. (int)
        predator_item_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for predator_items. (int)
        prey_item_mutation_probability -- a probabilty less than one that the bush preference of an individual prey_item offspring accrues a mutation to it's bush preference.
        predator_item_mutation_probability -- a probabilty less than one that the bush preference of an individual predator_item offspring accrues a mutation to it's bush preference.

    '''
    def __init__(self,initial_conditions_file_path, prey_item_csv_output_file_path, predator_item_csv_output_file_path, parameters_csv_output_file_path, rng=None,seed=None,burn_in = None,_output_landscape=False,_output_landscape_file_path=None,sim_info_output_file=None):
        self.sim_id = uuid.uuid4().hex
        self.initial_conditions_file_path = initial_conditions_file_path
        #self.predator_item_info = []
        #self.prey_item_info = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.prey_item_file_path = prey_item_csv_output_file_path
        self.predator_item_file_path = predator_item_csv_output_file_path
        self.sim_parameters_and_totals = parameters_csv_output_file_path
        self.cycle = 0
        self.prey_item_generation = 0
        self.predator_item_generation = 0
        if seed is not None:
            self.rng.seed(seed)
        if burn_in is not None:
            self.burn_in = burn_in       
        else:
            self.burn_in = 0
        if sim_info_output_file is not None:
            self.sim_info_output_file = sim_info_output_file
        self._output_landscape = _output_landscape
        self._output_landscape_file_path = _output_landscape_file_path
        

    def genotype_freq_test(self,genotype_freq_dict):
        if sum(genotype_freq_dict.values()) != 1:
            raise Exception("Genotype frequencies do not sum to 1.")

    def exception_bool_values(self, mixed_preference, prey_competition):
        test_vals = {'mixed_preference': mixed_preference,
                    'prey_competition' : prey_competition}
        for key, val in test_vals.items():
            if not type(val) is bool:
                raise TypeError("{} check should be a boolean (True or False).".format(key))

    def exception_int_values(
                        self, end_time, initial_prey_item_pop, initial_predator_item_pop,
                        prey_item_reproduction_freq, predator_item_reproduction_freq, energy_gain_per_prey_item,
                        predator_item_energy_cost, predator_item_move_range, predator_item_movement_frequency,
                        prey_item_move_range, prey_item_movement_frequency, prey_item_energy_gain_bush,
                        prey_item_energy_gain_open, prey_item_energy_cost, owl_move_range,
                        landscape_size_x, landscape_size_y, initial_owl_pop
                        ):
        test_vals = {'end_time': end_time,
                    'initial_prey_item_pop' : initial_prey_item_pop,
                    'initial_predator_item_pop' : initial_predator_item_pop,
                    'prey_item_reproduction_freq' : prey_item_reproduction_freq,
                    'predator_item_reproduction_freq' : predator_item_reproduction_freq,
                    'energy_gain_per_prey_item' : energy_gain_per_prey_item,
                    'predator_item_energy_cost' : predator_item_energy_cost,
                    'predator_item_movement_frequency' : predator_item_movement_frequency,
                    'prey_item_move_range' : prey_item_move_range,
                    'prey_item_movement_frequency' : prey_item_movement_frequency,
                    'prey_item_energy_gain_bush' : prey_item_energy_gain_bush,
                    'prey_item_energy_gain_open' : prey_item_energy_gain_open,
                    'prey_item_energy_cost' : prey_item_energy_cost,
                    'landscape_size_x' : landscape_size_x,
                    'landscape_size_y' : landscape_size_y,
                    'initial_owl_pop' : initial_owl_pop,
                    'owl_move_range' : owl_move_range}
        for key, val in test_vals.items():
            if not type(val) is int:
                raise TypeError("{} value should be an integer".format(key))

    def exception_float_or_int_values(
                        self, prey_item_mutation_std, predator_item_mutation_std,
                        prey_item_mutation_probability, predator_item_mutation_probability, predator_item_strike_success_probability_bush,
                        strike_success_probability_open, predator_item_death_probability,  owl_strike_success_probability 
                        ):
        test_vals = {'prey_item_mutation_std': prey_item_mutation_std,
                    'predator_item_mutation_std' : predator_item_mutation_std,
                    'prey_item_mutation_probability' : prey_item_mutation_probability,
                    'predator_item_mutation_probability' : predator_item_mutation_probability,
                    'predator_item_strike_success_probability_bush' : predator_item_strike_success_probability_bush,
                    'strike_success_probability_open' : strike_success_probability_open,
                    'predator_item_death_probability' : predator_item_death_probability,
                    'owl_strike_success_probability ' : owl_strike_success_probability}
        for key, val in test_vals.items():
            if type(val) not in [int,float]:
                raise TypeError("{} value should be a number".format(key))
            if 0 > val > 1:
                raise Exception("{} value should be between 0 and 1".format(key))

    def run_config_checks(self,config_d):
        self.exception_bool_values(mixed_preference=config_d["mixed_preference_individuals"], prey_competition=config_d["prey_competition"])
        self.exception_int_values(
                        end_time = config_d["cycles_of_sim"], initial_prey_item_pop=config_d["initial_prey_item_pop"], initial_predator_item_pop=config_d["initial_predator_item_pop"],
                        prey_item_reproduction_freq=config_d["prey_item_reproduction_freq_per_x_cycles"], predator_item_reproduction_freq=config_d["predator_item_reproduction_freq_per_x_cycles"], energy_gain_per_prey_item=config_d["predator_item_energy_gain"],
                        predator_item_energy_cost=config_d["predator_item_energy_cost"], predator_item_move_range=config_d["predator_item_move_range"], predator_item_movement_frequency=config_d["predator_item_movement_frequency_per_x_cycles"],
                        prey_item_move_range=config_d["prey_item_move_range"], prey_item_movement_frequency=config_d["prey_item_movement_frequency_per_x_cycles"], prey_item_energy_gain_bush=config_d["prey_item_energy_gain_bush"],
                        prey_item_energy_gain_open=config_d["prey_item_energy_gain_open"], prey_item_energy_cost=config_d["prey_item_energy_cost"], owl_move_range=config_d["owl_move_range"],
                        landscape_size_x=config_d["landscape_size_x"], landscape_size_y=config_d["landscape_size_y"], initial_owl_pop=config_d["initial_owl_pop"]
                        )
        self.exception_float_or_int_values(
                        prey_item_mutation_std=config_d["prey_item_mutation_std"], predator_item_mutation_std=config_d["predator_item_mutation_std"],
                        prey_item_mutation_probability=config_d["prey_item_mutation_probability"], predator_item_mutation_probability=config_d["predator_item_mutation_probability"], predator_item_strike_success_probability_bush=config_d["predator_item_strike_success_probability_bush"],
                        strike_success_probability_open=config_d["predator_item_strike_success_probability_open"], predator_item_death_probability=config_d["predator_item_death_probability"],  owl_strike_success_probability=config_d["owl_catch_success"]
                        )

    def config_sim_species_attributes_and_sim_paramaters(self,config_d):
        self.mixed_individuals = config_d["mixed_preference_individuals"]
        self.prey_competition = config_d["prey_competition"]
        self.end_time = config_d["cycles_of_sim"]
        self.initial_prey_item_pop = config_d["initial_prey_item_pop"]
        self.initial_predator_item_pop = config_d["initial_predator_item_pop"]
        self.prey_item_reproduction_freq = config_d["prey_item_reproduction_freq_per_x_cycles"]
        self.predator_item_reproduction_freq = config_d["predator_item_reproduction_freq_per_x_cycles"]
        self.prey_item_mutation_std = config_d["prey_item_mutation_std"]
        self.predator_item_mutation_std = config_d["predator_item_mutation_std"]
        self.prey_item_mutation_probability = config_d["prey_item_mutation_probability"]
        self.predator_item_mutation_probability = config_d["predator_item_mutation_probability"]
        self.data_sample_frequency = config_d["data_sample_freq"]


    def initialize_predator_item_pop(self,config_d):
        if self.mixed_individuals:
            self.landscape.initialize_predator_item_pop_continuous_preference(
                strike_success_probability_bush = config_d["predator_item_strike_success_probability_bush"],
                strike_success_probability_open = config_d["predator_item_strike_success_probability_open"],
                death_probability = config_d["predator_item_death_probability"],
                energy_gain_per_prey_item = config_d["predator_item_energy_gain"],
                energy_cost = config_d["predator_item_energy_cost"],
                move_range = config_d["predator_item_move_range"],
                movement_frequency = config_d["predator_item_movement_frequency_per_x_cycles"],
            )
        else:
            predator_item_genotype_frequencies = {1:(1/2), 0:(1/2)}
            self.landscape.initialize_predator_item_pop_discrete_preference(
                strike_success_probability_bush = config_d["predator_item_strike_success_probability_bush"],
                strike_success_probability_open = config_d["predator_item_strike_success_probability_open"],
                death_probability = config_d["predator_item_death_probability"],
                energy_gain_per_prey_item = config_d["predator_item_energy_gain"],
                energy_cost = config_d["predator_item_energy_cost"],
                move_range = config_d["predator_item_move_range"],
                movement_frequency = config_d["predator_item_movement_frequency_per_x_cycles"],
                predator_item_genotype_frequencies = predator_item_genotype_frequencies
            )

    def initialize_prey_item_pop(self,config_d):
        if self.mixed_individuals:
                self.landscape.initialize_prey_item_pop_continuous_preference(
                move_range = config_d["prey_item_move_range"],
                movement_frequency = config_d["prey_item_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["prey_item_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["prey_item_energy_gain_open"], #from bouskila
                energy_cost=config_d["prey_item_energy_cost"],
                )
        else:
            prey_item_genotype_frequencies = {1:(1/2), 0:(1/2)}
            self.landscape.initialize_prey_item_pop_discrete_preference(
                move_range = config_d["prey_item_move_range"],
                movement_frequency = config_d["prey_item_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["prey_item_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["prey_item_energy_gain_open"], #from bouskila
                energy_cost=config_d["prey_item_energy_cost"],
                prey_item_genotype_frequencies = prey_item_genotype_frequencies
                )

    def configure(self, config_d):
        self.config_sim_species_attributes_and_sim_paramaters(config_d = config_d)
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"],
                _output_landscape = self._output_landscape,
                _output_landscape_file_path = self._output_landscape_file_path
                )
        self.landscape.build()
        self.initialize_predator_item_pop(config_d = config_d)
        self.initialize_prey_item_pop(config_d = config_d)
        self.landscape.initialize_owl_pop(
                initial_owl_pop=config_d["initial_owl_pop"],
                move_range = config_d["owl_move_range"],
                strike_success_probability = config_d["owl_catch_success"],
                open_preference_weight = 1,
                bush_preference_weight = 0
                )

    def read_configuration_file(self):
        with open(self.initial_conditions_file_path) as f:
            self.config_d = load(f)
        self.run_config_checks(config_d = self.config_d)
        self.configure(self.config_d)

    def test(self):
        self.read_configuration_file()
        cells = self.landscape.cells
        for cell_width in cells:
            for cell in cell_width:
                cell_id = '{},{}'.format(cell.cell_id[0],cell.cell_id[1])
                print(cell_id)
        

    def make_csv(self,file_name):
        with open(file_name, 'w', newline='\n') as file:
            pass

    def append_data(self,file_name,data_row):
        with open(file_name, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data_row)

    def sim_info(self, line):
        if self.sim_info_output_file is not None:
            with open(self.sim_info_output_file, 'a') as file:
                file.write(line)

    def sim_stats_per_cycle(self, config_d):
        if self.cycle == 0:
            data_row = []
            data_row.append("sim_id")
            data_row.append("cycle")
            for keys, vals in config_d.items():
                data_row.append(keys)
            self.append_data(file_name = self.sim_parameters_and_totals, data_row = data_row)
        elif self.cycle >= self.burn_in and (self.cycle % self.data_sample_frequency) == 0:
            data_row = []
            data_row.append(self.sim_id)
            data_row.append(self.cycle)
            for keys, vals in config_d.items():
                data_row.append(vals)
            self.append_data(file_name = self.sim_parameters_and_totals, data_row = data_row)

    def main(self):
        start = round(time.time())
        start_local_time = time.localtime()
        start_info = 'Sim start time {}:{} {}/{}/{}, Data config {}\n'.format(start_local_time.tm_hour,
                                                                               start_local_time.tm_min,
                                                                               start_local_time.tm_year,
                                                                               start_local_time.tm_mon, 
                                                                               start_local_time.tm_mday, 
                                                                               self.initial_conditions_file_path)
        data_info ='{}, {} \n'.format(self.prey_item_file_path,self.predator_item_file_path )
        self.sim_info(line = data_info)
        self.sim_info(line = start_info)
        self.make_csv(file_name = self.prey_item_file_path )
        self.make_csv(file_name = self.predator_item_file_path )
        self.make_csv(file_name = self.sim_parameters_and_totals)
        self.read_configuration_file()
        for i in range(0,self.end_time,1):
            self.sim_stats_per_cycle(self.config_d)
            self.landscape.landscape_dynamics()
            self.cycle += 1
        time_elapsed = round(time.time()) - start
        end_local_time = time.localtime()
        end_info = 'Sim end time {}:{} {}/{}/{}, time elapsed {}\n'.format(end_local_time.tm_hour,
                                                                           end_local_time.tm_min,
                                                                           end_local_time.tm_year,
                                                                           end_local_time.tm_mon, 
                                                                           end_local_time.tm_mday,
                                                                           time_elapsed)
        self.sim_info(line = end_info)



if __name__ ==  "__main__":
    pass
    #sim = Sim(initial_conditions_file_path = 'data.txt', prey_item_tsv_output_file_path = 'prey_item_energy.tsv', predator_item_tsv_output_file_path = 'predator_item_energy.tsv')
    #sim.main()
    #print('test')



