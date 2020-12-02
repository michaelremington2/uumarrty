#!/usr/bin/python
import math
#doxygen
#sphyinxdocumentation format
class Organism(object):
    '''
    The base class that any tyoe of vertabrate organism can use to set up the object that represents the individual.

    Args:
        sim -- the simulation object with base parameters such as a random number generator and a time parameter.
        energy counter -- The base energy stat that dictates the state of the organismand dictates feeding tendancies. This can be an int or a float.

    Attributes:
        max_energy -- initial energy counter.
        alive -- if true the object is alive, if false the object is dead (boolean initial set to True).
        hungry -- if true the object will forage or consume at appropriate times if false the organisms energy state is to high to eat (boolean initial set to True).
        rng -- random number generator in the sim.
    '''
    def __init__(self,sim,home_cell=None, move_range=1, open_preference_weight=1, bush_preference_weight=1):
        self.sim = sim
        self.landscape =self.sim.landscape
        self.energy_score = 0
        self.alive = True
        self.predation_counter = 0
        self.missed_opportunity_cost = 0
        self.home_cell = home_cell
        self.current_cell = home_cell
        self.rng = self.sim.rng
        self.move_range = move_range
        self.column_boundary = self.sim.landscape.cells_x_columns - 1
        self.row_boundary = self.sim.landscape.cells_y_rows - 1
        self.number_of_movements = 0
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight

    def __hash__(self):
        return id(self)

    def register_predation_event(self):
        self.predation_counter += 1

    def reset_predation_history(self):
        self.predation_counter = 0

    def calc_cell_destination_suitability(self, cell,number_of_move_options, bush_preference_weight=1, open_preference_weight=1):
        if number_of_move_options <= 0:
            raise ValueError('No Move Options')
        else:
            base_destination_probability = 1/number_of_move_options
        if bush_preference_weight != 1 and cell.habitat_type[0].name == 'BUSH':
            destination_probability = base_destination_probability*bush_preference_weight
        elif open_preference_weight != 1 and cell.habitat_type[0].name == 'OPEN':
            destination_probability = base_destination_probability*open_preference_weight
        else:
            destination_probability = base_destination_probability
        return destination_probability

    def normalize_destination_cell_probabilities(self, destination_cell_probabilities):
        denom = sum(destination_cell_probabilities.values())
        if denom != 1:
            for i, prob in destination_cell_probabilities.items():
                norm_probability = prob/denom
                destination_cell_probabilities[i] == norm_probability
        return destination_cell_probabilities

    def calc_destination_cell_probabilities(self, bush_preference_weight=1, open_preference_weight=1): #calc move coordinates
        destination_cell_probabilities = {}
        move_options = []
        for x in range(-self.move_range,self.move_range+1):
            for y in range(-self.move_range,self.move_range+1):
                #print('{},{}'.format(x,y))
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
            p = self.calc_cell_destination_suitability(cell=i, number_of_move_options=number_of_move_options, bush_preference_weight=bush_preference_weight, open_preference_weight=open_preference_weight)
            destination_cell_probabilities[destination_cell] = p
        if len(destination_cell_probabilities) == 0:
            print(self.current_cell.cell_id)
            print(self.row_boundary)
            print(self.column_boundary)
            raise ValueError('No move options')
        destination_cell_probabilities = self.normalize_destination_cell_probabilities(destination_cell_probabilities)
        return destination_cell_probabilities

    def pick_new_cell(self, bush_preference_weight=1, open_preference_weight=1):
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
        return self.home_cell


class Snake(Organism):
    def __init__(self,sim, move_range,strike_success_probability_bush,strike_success_probability_open,energy_gain_per_krat,energy_cost,home_cell=None, open_preference_weight=1, bush_preference_weight=1,hunting_hours = None):
        super().__init__(sim,home_cell, move_range)
        self.sim = sim 
        self.energy_score = 0
        self.energy_gain_per_krat = energy_gain_per_krat
        self.energy_cost = energy_cost
        self.strike_success_probability_bush = strike_success_probability_bush
        self.strike_success_probability_open = strike_success_probability_open
        self.home_cell = home_cell
        self.hunting = False
        self.hunting_hours = self.hunting_period_gen(hunting_hours)
        self.rng = self.sim.rng
        self.sex = self.rng.choice(['F','M'])
        self.move_range = move_range
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        self.snake_id = id(self)

    def hunting_period_gen(self,hunting_hours):
        if hunting_hours == None:
            hunting_hours = [18,19,20,21,22,23,0,1,2,3,4,5]
        return hunting_hours

    def hunting_period(self):
        if self.sim.time_of_day in self.hunting_hours:
            self.hunting = True
        else:
            self.hunting = False

    def calc_strike_success_probability(self,cell):
        if cell.habitat_type[0].name == 'BUSH':
            ss = self.strike_success_probability_bush
        elif cell.habitat_type[0].name == 'OPEN':
            ss = self.strike_success_probability_open
        return ss

class Krat(Organism):
    def __init__(self,sim,energy_gain_open,energy_gain_bush,energy_cost,death_cost,move_range,home_cell,open_preference_weight=None,bush_preference_weight=None,foraging_hours = None):
        super().__init__(sim,home_cell,move_range)
        self.sim = sim
        self.home_cell = home_cell
        self.foraging = False
        self.alive = True
        self.foraging_hours = self.foraging_period_gen(foraging_hours)
        self.energy_gain_bush = energy_gain_bush
        self.energy_gain_open = energy_gain_open
        self.energy_cost = energy_cost
        self.death_cost = death_cost
        self.rng = self.sim.rng
        self.sex = self.rng.choice(['F','M'])
        self.move_range = move_range
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        self.preference_vector = {}
        self.krat_id = id(self)

    def foraging_period_gen(self,foraging_hours):
        if foraging_hours == None:
            foraging_hours = [18,19,20,21,22,23,0,1,2,3,4,5]
        return foraging_hours

    def foraging_period(self):
        if self.sim.time_of_day in self.foraging_hours:
            self.foraging = True
        else:
            self.foraging = False

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
        if self.alive:
            cost = self.energy_cost
        else:
            cost = self.energy_cost + self.death_cost
        self.alive = True
        return cost


class Owl(Organism):
    def __init__(self,sim, move_range,strike_success_probability,home_cell=None,open_preference_weight=1,bush_preference_weight=1,hunting_hours=None):
        super().__init__(sim,home_cell,move_range)
        self.sim = sim 
        self.strike_success_probability = strike_success_probability
        self.hunting = False
        self.hunting_hours = self.hunting_period_gen(hunting_hours)
        self.rng = self.sim.rng
        self.move_range = move_range
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight

    def hunting_period_gen(self,hunting_hours):
        if hunting_hours == None:
            hunting_hours = [18,19,20,21,22,23,0,1,2,3,4,5]
        return hunting_hours

    def hunting_period(self):
        if self.sim.time_of_day in self.hunting_hours:
            self.hunting = True
        else:
            self.hunting = False





if __name__ ==  "__main__":
    pass



