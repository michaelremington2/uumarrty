#!/usr/bin/python
from enum import Enum,auto
import random
from json import load
from uumarrty import organismsim as org
from itertools import chain

class Microhabitat(object):
    '''
    Object that describes the type and ecology of the microhabitat in the cell.
    Args:
        name -- The name and class of the microhabitat.
    Attributes:'''
    def __init__(self,name):
        self.name = name




class Cell(object):
    '''
    This object represents a sub space of the landscape object that is a container for organisms to interact in.
    The user will have to keep in mind the abstract size of these interaction landscapes when setting up simulation variables.
    Args:
        sim -- the simulation object with base parameters such as a random number generator and a time parameter. (sim object)
        habitat_type -- this is a label from an enumerated habitat object. (enum object)
        cell_id -- a tuple of the postion of the cell on the landscape in the y direction (rows) and the landscape in the x direction (columns). (tuple with 2 elements)
    Attributes:
        preys -- a list that holds prey objects. (list)
        predators -- a list that holds sake objects. (list)
        landscape -- the landscape object the cell operates in.
        rng -- a random number operator object.
    '''
    def __init__(self, sim, habitat_type,cell_id,prey_competition=False):
        self.sim = sim
        self.prey_in_cell = []
        self.predators_in_cell = []
        #self.owls = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.cell_id = cell_id
        self.prey_competition = prey_competition     
        self.rng = self.sim.rng

    def __hash__(self):
        return id(self)

    def add_prey(self, prey):
        '''Add a prey to the population of this cells preys'''
        self.prey_in_cell.append(prey)

    def add_predator(self, predator):
        '''Add a predator to the population of this cells predators'''
        self.predators_in_cell.append(predator)

    def add_owl(self,owl):
        '''adds an owl object to the landscape.'''
        self.owls.append(owl)

    def select_prey(self,prey_index = None):
        '''returns a random prey object if no specific index is provided.'''
        if prey_index == None:
            prey_index = self.rng.randint(0,len(self.prey_in_cell)-1)
        prey = self.prey_in_cell[prey_index]
        return prey

    def select_predator(self,predator_index = None):
        '''returns a random predator object if no specific index is provided.'''
        if predator_index == None:
            predator_index = self.rng.randint(0,len(self.predator)-1)
        predator = self.predators_in_cell[predator_index]
        return predator

    def pop_prey(self,prey_index):
        '''Selects a prey at random from population and removes it and returns the object '''
        return self.prey_in_cell.pop(prey_index)

    def pop_predator(self,predator_index):
        '''Selects a predator at random from population and removes it and returns the object '''
        return self.predators_in_cell.pop(predator_index)

    def clean_prey_list(self):
        '''creates a fresh list for the attribute preys'''
        self.prey_in_cell = []

    def clean_predator_list(self):
        '''creates a fresh list for the attribute predators'''
        self.predators_in_cell = []

    def cell_over_populated(self):
        '''test that makes sure cells don't become overpopulated and break sim'''
        if len(self.prey_in_cell) > self.sim.initial_prey_pop:
            raise ValueError("preys mating too much")
        if len(self.predators_in_cell) > self.sim.initial_predator_pop:
            raise ValueError("predators mating too much")

    def prey_move(self, prey,moving_prey_list,return_home=False):
        '''runs the prey movement algorithm and moves the prey from the cell to a temp list in the landscape. 
        Optional can designate the prey to return to designated nest cell tied to the prey object.'''
        if return_home == True:
            new_cell = prey.return_home()
        else:
            new_cell = prey.organism_movement()
        if new_cell != self:
            moving_prey = (new_cell,prey,self)
            self.landscape.prey_move_pool.append(moving_prey)
            moving_prey_list.append(prey)

    def predator_move(self,predator,moving_predator_list):
        '''runs the predator movement algorithm and moves the prey from the cell to a temp list in the landscape. '''
        new_cell = predator.organism_movement()
        if new_cell != self:
            moving_predator = (new_cell,predator,self)
            self.landscape.predator_move_pool.append(moving_predator)
            moving_predator_list.append(predator)

    # def owl_move(self,owl,moving_owl_list):
    #     '''runs the owl movement algorithm and moves the prey from the cell to a temp list in the landscape. '''
    #     new_cell = owl.organism_movement()
    #     if new_cell != self:
    #         moving_owl = (new_cell,owl,self)
    #         self.landscape.owl_move_pool.append(moving_owl)
    #         moving_owl_list.append(owl)             

    def prey_predation_by_predator(self,predator):
        '''determines whether or not the predator that was passed into the function successfully kills and obtains payoff of a prey that shares the cell with it.'''
        live_preys = [prey for prey in self.prey_in_cell if prey.alive] 
        ss = predator.calc_strike_success_probability(self) ### Will need to fix
        energy_cost = predator.energy_cost
        if len(live_preys) > 0 and self.rng.random() < ss:
            prey_index = self.rng.randint(0,len(live_preys)-1)
            prey = self.select_prey(prey_index = prey_index)
            prey.alive = False
            energy_gain = predator.energy_gain_per_prey              
        else:
            energy_gain = 0
        energy_delta = (energy_gain - energy_cost)
        predator.energy_score += energy_delta

    # def prey_predation_by_owl(self,owl):
    #     '''determines whether or not the owl that was passed into the function successfully kills and obtains payoff of a prey that shares the cell with it.'''
    #     live_preys = [prey for prey in self.prey_in_cell if prey.alive] 
    #     if len(live_preys) > 0 and self.rng.random() < owl.strike_success_probability and self.habitat_type[0].name == 'OPEN':
    #         prey_index = self.rng.randint(0,len(live_preys)-1)
    #         prey = self.select_prey(prey_index = prey_index)
    #         prey.alive = False

    def foraging_prey(self,prey):
        '''Provides prey with appropriate pay off for foraging in the cell.'''
        if self.prey_competition:
            prey_energy_gain = prey.calc_energy_gain(self)/len(self.prey_in_cell)
        else:
            prey_energy_gain = prey.calc_energy_gain(self)
        prey_energy_cost = prey.calc_energy_cost()
        energy_delta = (prey_energy_gain - prey_energy_cost)
        prey.energy_score += energy_delta

    def prey_activity_pulse_behavior(self):
        """ prey function, this is the general behavior of either moving or foraging of the prey for one activity pulse."""
        moving_preys = []
        for prey in self.prey_in_cell:
            if (self.sim.cycle % self.sim.data_sample_frequency) == 0 and prey.alive:
                prey.generate_prey_stats()
            self.foraging_prey(prey)
            if self.sim.cycle % prey.movement_frequency == 0 and self.sim.cycle != 0 and prey.alive:
                self.prey_move(prey,moving_prey_list = moving_preys)           
        self.prey_in_cell = [prey for prey in self.prey_in_cell if prey not in moving_preys and prey.alive]     

    def predator_activity_pulse_behavior(self):
        """ predator function, this is the general behavior of either moving or hunting of the prey for one activity pulse."""
        moving_predators = []
        for predator in self.predators_in_cell:
            predator.predator_death()
            if (self.sim.cycle % self.sim.data_sample_frequency) == 0:
                predator.generate_predator_stats()
            self.prey_predation_by_predator(predator)
            if self.sim.cycle % predator.movement_frequency == 0 and self.sim.cycle != 0: 
                self.predator_move(predator, moving_predator_list=moving_predators)            
        self.predators_in_cell = [predator for predator in self.predators_in_cell if predator not in moving_predators and predator.alive]

    # def owl_activity_pulse_behavior(self):
    #     moving_owls = []
    #     for owl in self.owls:
    #         self.prey_predation_by_owl(owl)
    #         self.owl_move(owl, moving_owl_list=moving_owls)
    #     self.owls = [owl for owl in self.owls if owl not in moving_owls]


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
        prey_move_pool -- a temporary list that holds preys that need to be relocated to different cells in the landscape.
        predator_move_pool -- a temporary list that holds predators that need to be relocated to different cells in the landscape.
        owl_move_pool = -- a temporary list that holds owls that need to be relocated to different cells in the landscape.
        total_prey_list -- a list of the prey objects used for analysis and reproduction.
        total_predator_list -- a list of the predator objects used for analysis and reproduction.
        total_owl_list -- a list of the owl objects used for analysis and reproduction.
        '''
    class MicrohabitatType(Enum):
        OPEN = auto()
        BUSH = auto()

    def __init__(self,sim,size_x,size_y,microhabitat_proportions,microhabitat_labels,_output_landscape=False,_output_landscape_file_path=None):
        self.sim = sim
        self.size_x = size_x
        self.size_y = size_y
        self.cells = None
        # cell_list
        self.cells_x_columns = int(round(self.size_x))
        self.cells_y_rows = int(round(self.size_y))
        self.microhabitat_proportions = microhabitat_proportions
        self.microhabitat_labels = microhabitat_labels
        self.prey_move_pool = []
        self.predator_move_pool = []
        self.owl_move_pool = []
        self.total_prey_list = [] 
        self.total_predator_list = []
        self.total_owl_list = []
        self.rng = self.sim.rng
        self._output_landscape = _output_landscape
        if _output_landscape:
            self._output_landscape_file_path = _output_landscape_file_path
            with open(self._output_landscape_file_path, "w") as my_empty_csv:
                pass

    def make_microhabitat_dict(self):
        '''Makes a dictionary with all the microhabitat type labels with empty lists associated with them to append the cells to.'''
        self.cell_mh_dict = {}
        for mh_type in self.microhabitat_labels:
            self.cell_mh_dict[mh_type] = []

    def build(self):
        '''Populates the attribute cells with an x by y array'''
        self.cells = []
        self.make_microhabitat_dict()
        for yidx in range(self.cells_y_rows):
            temp_x = []
            for xidx in range(self.cells_x_columns):
                cell_id = (yidx,xidx)
                cell = Cell(
                    sim = self.sim,
                    habitat_type = self.select_random_cell_type(),
                    cell_id = cell_id,
                    prey_competition = self.sim.prey_competition)
                self.cell_mh_dict[cell.habitat_type.name].append(cell)
                if self._output_landscape:
                    self._output_landscape_row_append(cell)
                temp_x.append(cell)
            self.cells.append(temp_x)


    def _output_landscape_row_append(self,cell):
        '''This function generates a csv that has the information on every cell that generates the lanscape.'''
        from csv import writer
        cell_id = cell.cell_id 
        cell_microhabitat_type = cell.habitat_type.name  
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

    def initialize_predator_pop_discrete_preference(
            self, organism_label,
            death_probability, strike_success_probability_bush,
            strike_success_probability_open, energy_gain_per_prey,
            energy_cost, move_range,
            movement_frequency, predator_genotype_frequencies):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        isp = self.sim.predator_parameters[organism_label]["initial_pop"]
        for key, freq in predator_genotype_frequencies.items():
            pop = round(isp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                bush_preference_weight = float(key)
                open_preference_weight = (1-float(key))
                predator = org.Predator(sim = self.sim,
                            organism_label = organism_label,
                            strike_success_probability_bush = strike_success_probability_bush,
                            strike_success_probability_open = strike_success_probability_open,
                            death_probability = death_probability,
                            energy_gain_per_prey = energy_gain_per_prey,
                            energy_cost = energy_cost,
                            move_range = move_range,
                            movement_frequency = movement_frequency,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight
                            )
                cell.add_predator(predator)
                predator.current_cell=cell
                #predator.generate_predator_stats()
                pop = pop-1

    def initialize_predator_pop_continuous_preference(
            self, organism_label, death_probability,
            strike_success_probability_bush, strike_success_probability_open,
            energy_gain_per_prey,energy_cost, move_range,
            movement_frequency):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        isp = self.sim.predator_parameters[organism_label]["initial_pop"]
        while isp > 0:
            cell = self.select_random_cell()
            bush_preference_weight = self.rng.uniform(0, 1)
            open_preference_weight = (1-float(bush_preference_weight))
            predator = org.Predator(sim = self.sim,
                        organism_label = organism_label,
                        strike_success_probability_bush = strike_success_probability_bush,
                        strike_success_probability_open = strike_success_probability_open,
                        death_probability = death_probability,
                        energy_gain_per_prey = energy_gain_per_prey,
                        energy_cost = energy_cost,
                        move_range = move_range,
                        movement_frequency = movement_frequency,
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight
                        )
            cell.add_predator(predator)
            predator.current_cell=cell
            #predator.generate_predator_stats()
            isp = isp-1

    def initialize_prey_pop_discrete_preference(
            self, org_label,
            energy_gain_bush, energy_gain_open, energy_cost, 
            movement_frequency, prey_genotype_frequencies,move_range=None):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        ikp = self.sim.prey_parameters[organism_label]["initial_pop"]
        for key, freq in prey_genotype_frequencies.items():
            pop = round(ikp*freq)
            while pop > 0:
                cell = self.select_random_cell()
                bush_preference_weight = float(key)
                open_preference_weight = (1-float(key))
                cell = self.select_random_cell()
                prey = org.Prey(sim = self.sim,
                            org_label = org_label,
                            energy_gain_dict=energy_gain_dict,
                            energy_cost = energy_cost,
                            move_range = move_range,
                            movement_frequency = movement_frequency,
                            home_cell = cell,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight)
                cell.add_prey(prey)
                prey.current_cell=cell
                #prey.generate_prey_stats()
                pop = pop-1

    def initialize_prey_pop_continuous_preference(
        self, organism_label,
        energy_gain_dict,energy_cost,
        move_range,movement_frequency):
        '''Just used to first initalize populations of kangaroo rats.
            This is a reproduction algorithm based on the calculated next generation phenotype frequency.'''
        ikp = self.sim.prey_parameters[organism_label]["initial_pop"]
        while ikp > 0:
            cell = self.select_random_cell()
            bush_preference_weight = self.rng.uniform(0, 1)
            open_preference_weight = (1-float(bush_preference_weight))
            cell = self.select_random_cell()
            prey = org.Prey(sim = self.sim,
                        energy_gain_dict=energy_gain_dict,
                        energy_cost = energy_cost,
                        move_range = move_range,
                        movement_frequency = movement_frequency,
                        home_cell= cell,
                        open_preference_weight = open_preference_weight,
                        bush_preference_weight = bush_preference_weight)
            cell.add_prey(prey)
            prey.current_cell=cell
                #prey.generate_prey_stats()
            ikp = ikp-1

    # def initialize_owl_pop(
    #         self, initial_owl_pop,
    #         move_range, strike_success_probability,
    #         open_preference_weight, bush_preference_weight):
    #     iop = initial_owl_pop
    #     while iop > 0:
    #         cell = self.select_random_cell()
    #         owl = org.Predator(sim = self.sim,
    #                     move_range = move_range,
    #                     strike_success_probability = strike_success_probability,
    #                     open_preference_weight = open_preference_weight,
    #                     bush_preference_weight = bush_preference_weight)
    #         cell.add_owl(owl)
    #         owl.current_cell=cell
    #         iop = iop-1

    def relocate_preys(self):
        for i, prey in enumerate(self.prey_move_pool):
            new_cell = prey[0]
            prey_object = prey[1]
            new_cell.add_prey(prey_object)
            prey_object.current_cell = new_cell
        self.prey_move_pool = []

    def relocate_predators(self):
        for j, predator in enumerate(self.predator_move_pool):
            new_cell = predator[0]
            predator_object = predator[1]
            new_cell.add_predator(predator_object)
            predator_object.current_cell = new_cell 
        self.predator_move_pool = []

    # def relocate_owls(self):
    #     for j, owl in enumerate(self.owl_move_pool):
    #         new_cell = owl[0]
    #         owl_object = owl[1]
    #         new_cell.add_owl(owl_object)
    #         owl_object.current_cell = new_cell 
    #     self.owl_move_pool = []

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
        #predators and preys
        if (self.sim.cycle % self.sim.prey_reproduction_freq) == 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.predator_reproduction_freq) == 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_prey_list, cell_org_list= cell.preys) #prey reproduction
                    cell.clean_prey_list()
                    self.populate_total_org_list(total_org_list = self.total_predator_list, cell_org_list= cell.predators) #predator reproduction
                    cell.clean_predator_list()
        #Just preys
        elif (self.sim.cycle % self.sim.prey_reproduction_freq) == 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.predator_reproduction_freq) != 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_prey_list, cell_org_list= cell.preys) #prey reproduction
                    cell.clean_prey_list()
        #just predators
        elif (self.sim.cycle % self.sim.prey_reproduction_freq) != 0 and self.sim.cycle != 0 and (self.sim.cycle % self.sim.predator_reproduction_freq) == 0:
            for cell_width in self.cells:
                for cell in cell_width:
                    self.populate_total_org_list(total_org_list = self.total_predator_list, cell_org_list= cell.predators) #predator reproduction
                    cell.clean_predator_list()

    def prey_reproduction(self):
        '''Generates the new generaton of preys from information from the old generation and a calculation of how well agents in the previous generation
        associated with certain habitat preference genotypes preformed.'''
        if len(self.total_prey_list) > 0:
            ikp = self.sim.initial_prey_pop
            parent_prey_pop = self.total_prey_list
            parent_prey_payoffs = [prey.energy_score for prey in parent_prey_pop]
            self.total_prey_list = []
            while ikp > 0:
                cell = self.select_random_cell()
                parent = self.rng.choices(parent_prey_pop, weights=parent_prey_payoffs, k = 1)
                parent = parent[0]
                bush_preference_weight = self.preference_mutation_calc(bush_pref_weight = parent.bush_preference_weight, mutation_probability= self.sim.prey_mutation_probability, mutation_std = self.sim.prey_mutation_std)
                open_preference_weight = (1-float(bush_preference_weight))
                cell = self.select_random_cell()
                prey = org.Prey(sim = self.sim,
                            energy_gain_dict=parent.energy_gain_dict,
                            energy_cost = parent.energy_cost,
                            move_range = parent.move_range,
                            movement_frequency = parent.movement_frequency,
                            home_cell= cell,
                            open_preference_weight = open_preference_weight,
                            bush_preference_weight = bush_preference_weight)
                cell.add_prey(prey)
                prey.current_cell=cell
                ikp = ikp-1
            self.sim.prey_generation += 1


    def predator_reproduction(self):
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
