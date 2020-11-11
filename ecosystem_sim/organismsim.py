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
    def __init__(self,sim,home_cell=None,initial_energy=0,energy_deviation=0, move_range=1, open_preference_weight=1, bush_preference_weight=1):
        self.sim = sim
        self.landscape =self.sim.landscape
        self.initial_energy = initial_energy
        self.energy = initial_energy
        self.energy_deviation = energy_deviation
        self.max_energy = initial_energy+self.energy_deviation #Assumption
        self.hunger_level = initial_energy-self.energy_deviation #Assumption
        self.alive = True
        self.hungry = True
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

    def natural_death(self): #check_if_natural_death
        '''If the energy counter falls below zero, this function sets the alive attribute to false signifying it is dead.'''
        if round(self.energy) <= 0:
            self.alive = False

    def expend_energy(self, energy_cost, energy_weight=1):
        '''
        Sets the object to dead if there is not enough energy in the object.If alive,
        deducts the energy cost* the energy weight from the classes energy_counter attribute.

        Args:
            energy_cost -- base constant to deduct from energy_counter (int/ float)
            energy_weight -- multiplier coefficent for the energy_cost factor.(optional set to 1 in no args passed.)

        Raises:
            ValueError: if energy_cost is less than zero
        '''
        self.natural_death()
        if self.alive == True:
            if energy_cost < 0:
                raise ValueError('Costs should be positive integers')
            self.energy -= energy_cost*energy_weight

    def set_hungry(self):
        '''Controls hunger parameter true are false based on the energy counter and max_energy.'''
        if self.energy < self.hunger_level:
            self.hungry =  True
        elif self.energy > self.max_energy:
            self.hungry = False


    def register_predation_event(self):
        self.predation_counter += 1

    def reset_predation_history(self):
        self.predation_counter = 0

    def homeostasis_delta_calculator(self, energy_gain, cost_to_move, predation_cost, missed_opportunity_cost, competition_cost,basal_energy_cost):
        #E(H) = C (net gain) + RI (risk of injury) + P(risk of predation) + I(interaction with predators) + MOC(missed_opportunity_cost) enbar 2014
        # H = EC + PC + MOC +ioc (interference cost) bouskila 1995
        e = energy_gain+cost_to_move-predation_cost-missed_opportunity_cost-competition_cost-basal_energy_cost
        return e

    def calc_cell_destination_suitability(self, cell,number_of_move_options, bush_preference_weight=1, open_preference_weight=1):
        if number_of_move_options <= 0:
            raise ValueError('No Move Options')
        else:
            base_destination_probability = 1/number_of_move_options
        if bush_preference_weight != 1 and cell.habitat_type == '[<MicrohabitatType.BUSH: 2>]':
            destination_probability = base_destination_probability*bush_preference_weight
        elif open_preference_weight != 1 and cell.habitat_type == '[<MicrohabitatType.OPEN: 1>]':
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
                self.reset_predation_history()
                self.number_of_movements += 1
        return new_cell

    def return_home(self):
        return self.home_cell


class Snake(Organism):
    def __init__(self,sim, initial_energy,energy_deviation,move_range,home_cell,strike_success_probability,snake_max_litter_size,snake_litter_frequency, open_preference_weight=1, bush_preference_weight=1,hunting_hours = None):
        super().__init__(sim,home_cell,initial_energy, energy_deviation, move_range)
        self.sim = sim 
        self.initial_energy= initial_energy
        self.energy = initial_energy
        self._strike_success_probability = strike_success_probability
        self.snake_max_litter_size = snake_max_litter_size
        self.snake_litter_frequency = snake_litter_frequency*self.sim.time_step
        self.home_cell = home_cell
        self.hunting = False
        self.hunting_hours = self.hunting_period_gen(hunting_hours)
        self.rng = self.sim.rng
        self.sex = self.rng.choice(['F','M'])
        self.move_range = move_range
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        self.snake_id = id(self)

    @property
    def strike_success_probability(self):
        return self._strike_success_probability
    #@strike_success_probability.setter
    # def strike_success_probability(self, camofloage_coeffiecent):
    #     new_ss = self._strike_success_probability + camofloage_coeffiecent
    #     if new_ss >= 1:
    #         statment = 'Strike success probability ({}) is greater than 1. camofloage_coeffiecent should range between .01 to .05'.format(new_ss)
    #         RaiseValueError(statment)
    #     elif new_ss < 0:
    #         statment = 'camofloage_coeffiecent should not be negative {}'.format(camofloage_coeffiecent)
    #         RaiseValueError(statment)
    #     self._strike_success_probability = new_ss
    # @strike_success_probability.deleter
    # def strike_success_probability(self):
    #     self._strike_success_probability = None

    def hunting_period_gen(self,hunting_hours):
        if hunting_hours == None:
            hunting_hours = [18,19,20,21,22,23,0,1,2,3,4,5]
        return hunting_hours

    def hunting_period(self):
        self.set_hungry()
        if self.sim.time_of_day in self.hunting_hours and self.hungry == True:
            self.hunting = True
        else:
            self.hunting = False

    def consume(self,energy_gain):
        if energy_gain < 0:
            raise ValueError('gains should be positive integers')
        else:
            self.energy += energy_gain

    def reproduction(self,cell_incubation_list):
        if self.rng.random() < self.snake_litter_frequency and self.sex == 'F' and self.sim.time_of_day == 5 and self.energy >= self.initial_energy:
            litter_size = self.rng.randrange(0,self.snake_max_litter_size)
            for i in range(litter_size+1):
                snake_stats = {"energy": self.initial_energy,
                               "energy_deviation": self.energy_deviation,
                               "move_range": self.move_range,
                               "strike_success_probability": self.strike_success_probability,
                               "snake_max_litter_size": self.snake_max_litter_size,
                               "snake_litter_frequency": self.snake_litter_frequency,
                               "open_preference_weight":self.open_preference_weight,
                               "bush_preference_weight":self.bush_preference_weight,
                               "hunting_hours": self.hunting_hours}
                cell_incubation_list.append(snake_stats)

class Krat(Organism):
    def __init__(self,sim,initial_energy,energy_deviation,move_range,home_cell,foraging_rate,krat_max_litter_size,krat_litter_frequency, open_preference_weight=None, bush_preference_weight=None,foraging_hours = None):
        super().__init__(sim,home_cell,initial_energy,energy_deviation,move_range)
        self.sim = sim
        self.initial_energy = initial_energy
        self.energy= initial_energy
        self.krat_max_litter_size = krat_max_litter_size
        self.krat_litter_frequency = krat_litter_frequency
        self.home_cell = home_cell
        self.foraging = False
        self.foraging_hours = self.foraging_period_gen(foraging_hours)
        self.foraging_rate = foraging_rate
        self.rng = self.sim.rng
        self.sex = self.rng.choice(['F','M'])
        self.move_range = move_range
        self.open_preference_weight = open_preference_weight
        self.bush_preference_weight = bush_preference_weight
        self.krat_id = id(self)

    def foraging_period_gen(self,foraging_hours):
        if foraging_hours == None:
            foraging_hours = [18,19,20,21,22,23,0,1,2,3,4,5]
        return foraging_hours

    def foraging_period(self):
        self.set_hungry()
        if self.sim.time_of_day in self.foraging_hours and self.hungry:
            self.foraging = True
        else:
            self.foraging = False

    def energy_calculator(self,cell_energy_pool):
        '''Function takes partial seeds / energy left over from the foraging rate and uses this as a probability
        to whether or not the krat gets an extra unit or not.'''
        base_gain = math.floor(self.foraging_rate*cell_energy_pool)
        extra_energy_probability = float((self.foraging_rate*cell_energy_pool))- base_gain
        if extra_energy_probability > 1:
            raise ValueError('Probability is too high.')
        energy_probability_vector = [(1-extra_energy_probability),extra_energy_probability]
        extra_energy = self.rng.choices([0,1],energy_probability_vector, k = 1)
        energy_gain = extra_energy[0]+base_gain
        return energy_gain

    def energy_gain(self,cell_energy_pool):
        if self.alive:
            if self.foraging_rate*cell_energy_pool % 1 != 0:
                energy_gain = self.energy_calculator(cell_energy_pool)
            else:
                energy_gain = self.foraging_rate*cell_energy_pool
            return energy_gain

    def forage(self,energy_gain):
        if self.alive:
            self.energy += energy_gain

    def reproduction(self,cell_incubation_list):
        random_prob = self.rng.random()
        if (random_prob < self.krat_litter_frequency) and self.sex == 'F' and self.energy >= self.initial_energy and self.sim.time_of_day == 5:
            #print('prob {}, krat_freq {}, sex {}'.format(random_prob,self.krat_litter_frequency,self.sex))
            litter_size = self.rng.randrange(0,self.krat_max_litter_size)
            for i in range(litter_size+1):
                krat_stats = {"energy":self.initial_energy,
                              "energy_deviation":self.energy_deviation,
                              "move_range":self.move_range,
                              "foraging_rate":self.foraging_rate,
                              "krat_max_litter_size":self.krat_max_litter_size,
                              "krat_litter_frequency":self.krat_litter_frequency,
                              "open_preference_weight":self.open_preference_weight,
                              "bush_preference_weight":self.bush_preference_weight,
                              "foraging_hours":self.foraging_hours}
                cell_incubation_list.append(krat_stats)


class Owl(Organism):
    def __init__(self,sim, move_range,strike_success_probability,home_cell =None, initial_energy=0, energy_deviation=0, open_preference_weight=1, bush_preference_weight=1, hunting_hours=None):
        super().__init__(sim,home_cell,initial_energy, energy_deviation, move_range)
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



