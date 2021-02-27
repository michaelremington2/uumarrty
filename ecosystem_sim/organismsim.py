#!/usr/bin/python
import math
import statistics as stats
#doxygen
#sphyinxdocumentation format
class Organism(object):
    '''
    The base class that any type of vertabrate organism can use to set up the object that represents the individual.

    Args:
        sim -- the simulation object with base parameters such as a random number generator and a time parameter. (sim object)
        move_range -- the distance the organism can move from it's current cell. Orgs can move (N,E,W,S,NW,NE,SE,SW). (default 1)
        home_cell -- cell the organism is born in or has a nest. (tuple of x,y)
        move_preference -- an algorithm for weighting cells that previously provided the organism with increased payoff. This currently isn't working so set to false.
        open_preference_weight -- a weight that either increases or decreases prference to the open habitat. (default 1)
        bush_preference_weight -- a weight that either increases or decreases prference to the bush habitat. (default 1)
        memory_length_cycles -- this is the number of cycles the organism will have memory of its payoff values for. This goes into the move preference algorithm that isn't currently working. (bool)

    Attributes:
        alive -- if true the object is alive, if false the object is dead (bool).
        landscape -- the landscape object the organism opperates on. (class object)
        energy_score -- a rolling sum of the payoffs the organism is accruing throughout its life cycle. (int)
        column_boundary -- this is the boundary of the landscape in the x direction. (int)
        row_boundary -- this is the boundary of the landscape in the y direction. (int)
        number_of_movements -- a rolling count of the number of movements an organism makes when it moves outside of its current cell. (int)
        rng -- random number generator in the sim. (random object)
        microhabitat_energy_log -- 
    '''
    def __init__(self,sim,home_cell=None, move_range=1,move_preference=False, open_preference_weight=1, bush_preference_weight=1,memory_length_cycles=0):
        self.sim = sim
        self.landscape = self.sim.landscape
        self.energy_score = 0
        self.alive = True
        self.predation_counter = 0
        self.home_cell = home_cell
        self.current_cell = home_cell
        self.rng = self.sim.rng
        self.move_range = move_range
        self.column_boundary = self.sim.landscape.cells_x_columns - 1
        self.row_boundary = self.sim.landscape.cells_y_rows - 1
        self.number_of_movements = 0
        self.move_preference = move_preference
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        if self.move_preference:
            self.memory_length_cycles = memory_length_cycles
            self.microhabitat_energy_log = {'BUSH': [None]*self.memory_length_cycles, 'OPEN':[None]*self.memory_length_cycles}
            self.bush_preference_log_counter = 0
            self.open_preference_log_counter = 0

    def __hash__(self):
        return id(self)

    def register_predation_event(self):
        '''Adds one predation event to the rolling count if the predation event is unsuccessful.'''
        self.predation_counter += 1

    def reset_predation_history(self):
        '''resets the attribute predation_counter to zero.'''
        self.predation_counter = 0

    def log_microhabitat_energy_delta_preference(self,microhabitat_type,energy_delta):
        '''logs the payoff for  particular habitat type and stores it into the appropriate microhabitat preference log. This is used in the energy preference algorithm and currently doesn't work.'''
        if microhabitat_type == 'BUSH':
            self.microhabitat_energy_log['BUSH'][self.bush_preference_log_counter] = energy_delta
            if self.bush_preference_log_counter == self.memory_length_cycles-1:
                self.bush_preference_log_counter = 0
            else:
                self.bush_preference_log_counter += 1
        elif microhabitat_type == 'OPEN':
            self.microhabitat_energy_log['OPEN'][self.open_preference_log_counter] = energy_delta
            if self.open_preference_log_counter == self.memory_length_cycles-1:
                self.open_preference_log_counter = 0
            else:
                self.open_preference_log_counter += 1
        else:
            raise ValueError('Enter Valid Microhabitat Name')

    def normalize_energy_delta_preferences(self,energy_delta_set):
        '''Apart of the move preference algorithm. this normalizes the set of energy deltas and returns an interger of the preference weight.'''
        min_energy = min(energy_delta_set)
        max_energy = max(energy_delta_set)
        if (max_energy-min_energy) == 0:
            norm_weight = float(1)
        else:
            temp_set = []
            for i in energy_delta_set:
                val = float((i-min_energy))/float((max_energy - min_energy))
                temp_set.append(val)
            norm_weight = sum(temp_set)
        return norm_weight

    def gen_new_microhabitat_preferences(self):
        '''Apart of the move preference algorithm. Redefines microhabitat preferences once the energy logs are fully populated. This alg is not currently working.'''
        if None not in self.microhabitat_energy_log['BUSH']:
            self.bush_preference_weight= self.normalize_energy_delta_preferences(self.microhabitat_energy_log['BUSH'])
        if None not in self.microhabitat_energy_log['OPEN']:
            self.open_preference_weight= self.normalize_energy_delta_preferences(self.microhabitat_energy_log['OPEN'])

    def calc_cell_destination_suitability(self, cell,number_of_move_options):
        '''Calculates the probability an organism will move to a particular cell. The base probabilty is the number cells the organism can move to and it is multiplied by the organisms affinity to the microhabitat.'''
        if self.move_preference:
            self.gen_new_microhabitat_preferences()
        if number_of_move_options <= 0:
            raise ValueError('No Move Options')
        else:
            base_destination_probability = 1/number_of_move_options
        if cell.habitat_type[0].name == 'BUSH':
            destination_probability = base_destination_probability*self.bush_preference_weight
        elif cell.habitat_type[0].name == 'OPEN':
            destination_probability = base_destination_probability*self.open_preference_weight
        else:
            destination_probability = base_destination_probability
        return destination_probability

    def normalize_destination_cell_probabilities(self, destination_cell_probabilities):
        '''Returns a normalized probability list of all the potential destination cells.'''
        denom = sum(destination_cell_probabilities.values())
        #print('denom {}'.format(denom))
        for i, prob in destination_cell_probabilities.items():
            if denom == 0:
                destination_cell_probabilities[i] = 0
            else:
                norm_probability = prob/denom
                #print('current prob {}, normal prob {}'.format(prob,norm_probability))
                #print('pre')
                #print(destination_cell_probabilities[i])
                destination_cell_probabilities[i] = norm_probability
               # print('post')
                #print(destination_cell_probabilities[i])
        return destination_cell_probabilities

    def calibrate_move_distance_with_boundaries(self,current_coord_x,current_coord_y, move_distance,x_boundary,y_boundary):
        '''Function to make sure organsim only moves within boundaries. Only used in movement algorithm.'''
        if (current_coord_x + move_distance) > x_boundary:
            move_dist_x_right = x_boundary - current_coord_x
        else:
            move_dist_x_right = move_distance

        if (current_coord_x - move_distance) < 0:
            move_dist_x_left = current_coord_x
        else:
            move_dist_x_left = move_distance

        if (current_coord_y + move_distance) > y_boundary:
            move_dist_y_down = y_boundary - current_coord_y
        else:
            move_dist_y_down = move_distance

        if (current_coord_y - move_distance) < 0:
            move_dist_y_up = current_coord_x
        else:
            move_dist_y_up = move_distance
        return [move_dist_x_right,move_dist_x_left,move_dist_y_down,move_dist_y_up]


    def calc_destination_cell_probabilities(self, bush_preference_weight, open_preference_weight): #calc move coordinates
        '''This is the main function in the movement algorithm that generates a noralimized destination cell probability vector.'''
        destination_cell_probabilities = {}
        move_options = []
        calibrated_move_dists = self.calibrate_move_distance_with_boundaries(current_coord_x=self.current_cell.cell_id[1],
                                                                            current_coord_y=self.current_cell.cell_id[0],
                                                                            move_distance=self.move_range,
                                                                            x_boundary=self.column_boundary,
                                                                            y_boundary=self.row_boundary)
        move_options.append(self.current_cell)
        for x in range(-calibrated_move_dists[1],calibrated_move_dists[0]+1):
            for y in range(-calibrated_move_dists[3],calibrated_move_dists[2]+1):
                row_coord = self.current_cell.cell_id[0] + y
                column_coord = self.current_cell.cell_id[1] + x
                if row_coord >= 0 and row_coord <= self.row_boundary and column_coord >= 0 and column_coord <= self.column_boundary:
                    new_id = (row_coord,column_coord)
                    if new_id == self.current_cell.cell_id:
                        continue
                    else:
                        destination_cell = self.sim.landscape.select_cell(new_id)
                        move_options.append(destination_cell)
        for i in move_options:
            number_of_move_options = len(move_options)
            p = self.calc_cell_destination_suitability(cell=i, number_of_move_options=number_of_move_options)
            destination_cell_probabilities[i] = p
        if len(destination_cell_probabilities) == 0:
            print(self.current_cell.cell_id)
            print(self.row_boundary)
            print(self.column_boundary)
            raise ValueError('No move options')
        norm_destination_cell_probabilities = self.normalize_destination_cell_probabilities(destination_cell_probabilities)
        return norm_destination_cell_probabilities

    def pick_new_cell(self, bush_preference_weight=1, open_preference_weight=1):
        '''Picks a destination cell from the probability vector.'''
        destination_cell_probabilities = self.calc_destination_cell_probabilities( bush_preference_weight=bush_preference_weight, open_preference_weight=open_preference_weight)
        new_cell = self.rng.choices(list(destination_cell_probabilities.keys()),list(destination_cell_probabilities.values()),k=1)
        return new_cell[0]

    def organism_movement(self):
        '''Runs movement algorithm and returns the new cell id for the object to move to.'''
        new_cell = self.pick_new_cell(bush_preference_weight=self.bush_preference_weight, open_preference_weight=self.open_preference_weight)
        if new_cell != self.current_cell:
                self.number_of_movements += 1
        return new_cell

    def return_home(self):
        '''Returns the home cell to be used in an algorithm for movment if the org needs to return to nest.'''
        return self.home_cell

    def populate_microhabitat_energy_log(self,microhabitat_type,delta_energy_score):
        '''Used in preference algorithm. Populates the dictionary of the microhabitat preference log.'''
        label = microhabitat_type
        self.microhabitat_energy_log[label] += delta_energy_score


class Snake(Organism):
    def __init__(self,sim, move_range,movement_frequency,strike_success_probability_bush,strike_success_probability_open,energy_gain_per_krat,energy_cost,death_probability,home_cell=None,move_preference=False, open_preference_weight=1, bush_preference_weight=1,memory_length_cycles=0):
        super().__init__(sim,home_cell, move_range,move_preference,memory_length_cycles)
        self.sim = sim 
        self.energy_score = 0
        self.energy_gain_per_krat = energy_gain_per_krat
        self.death_probability = death_probability
        self.energy_cost = energy_cost
        self.strike_success_probability_bush = strike_success_probability_bush
        self.strike_success_probability_open = strike_success_probability_open
        self.home_cell = home_cell
        self.rng = self.sim.rng
        self.move_range = move_range
        self.movement_frequency = movement_frequency
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        if self.move_preference:
            self.memory_length_cycles = memory_length_cycles
            self.microhabitat_energy_log = {'BUSH': [None]*self.memory_length_cycles, 'OPEN':[None]*self.memory_length_cycles}
            self.bush_preference_log_counter = 0
            self.open_preference_log_counter = 0
        self.org_id = id(self)

    def calc_strike_success_probability(self,cell):
        if cell.habitat_type[0].name == 'BUSH':
            ss = self.strike_success_probability_bush
        elif cell.habitat_type[0].name == 'OPEN':
            ss = self.strike_success_probability_open
        return ss

    def generate_snake_stats(self):
        row = [self.org_id,
                self.sim.cycle,
                self.open_preference_weight,
                self.bush_preference_weight,
                self.energy_score,
                self.number_of_movements, 
                self.current_cell.cell_id,
                self.current_cell.habitat_type[0].name,
                len(self.current_cell.krats),
                len(self.current_cell.owls)]
        self.sim.snake_info.append(row)

    def snake_death(self):
        if self.rng.random() < self.death_probability:
            self.alive = False

class Krat(Organism):
    def __init__(self,sim,energy_gain_open,energy_gain_bush,energy_cost,death_cost,move_range,movement_frequency,home_cell,move_preference=False, open_preference_weight=1, bush_preference_weight=1,memory_length_cycles=0,foraging_hours = None):
        super().__init__(sim,home_cell,move_range,move_preference,memory_length_cycles)
        self.sim = sim
        self.home_cell = home_cell
        self.alive = True
        self.energy_gain_bush = energy_gain_bush
        self.energy_gain_open = energy_gain_open
        self.energy_cost = energy_cost
        self.death_cost = death_cost
        self.rng = self.sim.rng
        self.move_range = move_range
        self.movement_frequency = movement_frequency
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        if self.move_preference:
            self.memory_length_cycles = memory_length_cycles
            self.microhabitat_energy_log = {'BUSH': [None]*self.memory_length_cycles, 'OPEN':[None]*self.memory_length_cycles}
            self.bush_preference_log_counter = 0
            self.open_preference_log_counter = 0
        self.org_id = id(self)

    def calc_energy_gain(self,cell):
        if self.alive:
            if cell.habitat_type[0].name == 'BUSH':
                energy_gain = self.energy_gain_bush
            elif cell.habitat_type[0].name == 'OPEN':
                energy_gain = self.energy_gain_open
            else:
                #print(isinstance(self.sim.landscape.MicrohabitatType.OPEN, cell.habitat_type))
                raise ValueError('no habitat_type called')
        else:
            energy_gain = 0
        return energy_gain

    def calc_energy_cost(self):
        cost = self.energy_cost
        return cost

    def generate_krat_stats(self):
        row = [self.org_id,
                self.sim.cycle,
                self.open_preference_weight,
                self.bush_preference_weight,
                self.energy_score,
                self.number_of_movements, 
                self.current_cell.cell_id,
                self.current_cell.habitat_type[0].name,
                len(self.current_cell.snakes),
                len(self.current_cell.owls)]
        self.sim.krat_info.append(row)


class Owl(Organism):
    def __init__(self,sim, move_range,strike_success_probability,home_cell=None,open_preference_weight=1,bush_preference_weight=0):
        super().__init__(sim,home_cell,move_range)
        self.sim = sim 
        self.strike_success_probability = strike_success_probability
        self.rng = self.sim.rng
        self.move_range = move_range
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        self.org_id = id(self)

    def owl_loc(self):
        print('id {},cycle {}, current cell {}'.format(self.org_id, self.sim.cycle,self.current_cell.cell_id))


if __name__ ==  "__main__":
    pass



