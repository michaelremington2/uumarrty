#!/usr/bin/python
import math

class Organism(object):
    def __init__(self,sim, energy_counter):
        self.sim = sim
        self.energy_counter = energy_counter
        self.max_energy = energy_counter
        self.alive = True
        self.hungry = True
        self.rng = self.sim.rng

    def get_energy_counter(self):
        return self.energy_counter

    def expend_energy(self,energy_cost,energy_weight = 1):
        self.natural_death()
        if self.alive == True:
            if energy_cost < 0:
                raise ValueError('Costs should be positive integers')
            self.energy_counter -= energy_cost*energy_weight

    def set_hungry(self):
        if self.energy_counter < self.max_energy/2:
            self.hungry =  True
        elif self.energy_counter > self.max_energy*1.5:
            self.hungry = False
        else:
            pass

    def natural_death(self):
        if round(self.energy_counter) <= 0:
            self.alive = False

    def current_cell(self,cell_id):
        self.current_cell_id = cell_id

    def organism_movement(self):
        self.move.move_options(self.current_cell_id)
        new_cell_id = self.move.new_cell(self.current_cell_id)
        return new_cell_id


class Snake(Organism):
    def __init__(self,sim, energy_counter,strike_success_probability,snake_max_litter_size,snake_litter_frequency,hunting_hours = None):
        super().__init__(sim,energy_counter)
        self.sim = sim
        self.energy_counter = energy_counter
        self._strike_success_probability = strike_success_probability
        self.snake_max_litter_size = snake_max_litter_size
        self.snake_litter_frequency = snake_litter_frequency*self.sim.time_step
        self.hunting = False
        self.hunting_hours = self.hunting_period_gen(hunting_hours)
        self.rng = self.sim.rng
        self.sex = self.rng.choice(['F','M'])
        self.move = Movement(sim = self.sim, move_range = 1)

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
            hunting_hours = [0,1,2,3,4,5,18,19,20,21,22,23]
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
            self.energy_counter += energy_gain

    def reproduction(self,cell_incubation_list):
        if self.rng.random() < self.snake_litter_frequency and self.sex == 'F' and self.sim.time_of_day == 6:
            litter_size = self.rng.randrange(0,self.snake_max_litter_size)
            for i in range(litter_size+1):
                snake_stats = {"energy_counter": self.energy_counter,
                              "strike_success_probability": self.strike_success_probability,
                              "snake_max_litter_size": self.snake_max_litter_size,
                              "snake_litter_frequency": self.snake_litter_frequency,
                              "hunting_hours": self.hunting_hours}
                cell_incubation_list.append(snake_stats)


class Krat(Organism):
    def __init__(self,sim,energy_counter,home_cell_id,foraging_rate,krat_max_litter_size,krat_litter_frequency,foraging_hours = None):
        super().__init__(sim,energy_counter)
        self.sim = sim
        self.energy_counter = energy_counter
        self.krat_max_litter_size = krat_max_litter_size
        self.krat_litter_frequency = krat_litter_frequency
        self.home_cell_id = home_cell_id
        self.foraging = False
        self.foraging_hours = self.foraging_period_gen(foraging_hours)
        self.foraging_rate = foraging_rate
        self.rng = self.sim.rng
        self.sex = self.rng.choice(['F','M'])
        self.move = Movement(sim = self.sim, move_range = 2)

    def foraging_period_gen(self,foraging_hours):
        if foraging_hours == None:
            foraging_hours = [0,1,2,3,4,5,18,19,20,21,22,23]
        return foraging_hours

    def foraging_period(self):
        self.set_hungry()
        if self.sim.time_of_day in self.foraging_hours and self.hungry == True:
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
        if self.alive == True:
            if self.foraging_rate*cell_energy_pool % 1 != 0:
                energy_gain = self.energy_calculator(cell_energy_pool)
            else:
                energy_gain = self.foraging_rate*cell_energy_pool
            return energy_gain

    def forage(self,energy_gain):
        if self.alive == True:
            self.energy_counter += energy_gain

    def reproduction(self,cell_incubation_list):
        random_prob = self.rng.random()
        if (random_prob < self.krat_litter_frequency) and self.sex == 'F':
            #print('prob {}, krat_freq {}, sex {}'.format(random_prob,self.krat_litter_frequency,self.sex))
            litter_size = self.rng.randrange(0,self.krat_max_litter_size)
            for i in range(litter_size+1):
                krat_stats = {"energy_counter": self.energy_counter,
                              "foraging_rate": self.foraging_rate,
                              "krat_max_litter_size": self.krat_max_litter_size,
                              "krat_litter_frequency": self.krat_litter_frequency,
                              "foraging_hours":self.foraging_hours}
                cell_incubation_list.append(krat_stats)




class Movement(object):
    def __init__(self,move_range,sim):
        self.column_boundary = sim.landscape.cells_x_columns - 1
        self.row_boundary = sim.landscape.cells_y_rows - 1
        self.move_range = move_range
        self.rng = sim.rng

    def move_options(self,current_cell):
        self.move_coordinates = []
        self.current_cell = current_cell
        for x in range(-self.move_range,self.move_range+1):
            for y in range(-self.move_range,self.move_range+1):
                #print('{},{}'.format(x,y))
                row_coord = self.current_cell[0] + y
                column_coord = self.current_cell[1] + x
                if row_coord >= 0 and row_coord <= self.row_boundary and column_coord >= 0 and column_coord <= self.column_boundary:
                    new_id = (row_coord,column_coord)
                    self.move_coordinates.append(new_id)
        if len(self.move_coordinates) == 0:
            print(self.current_cell)
            print(self.row_boundary)
            print(self.column_boundary)
            raise ValueError('No move options')

    def move_probability_base_vector(self):
        base_probability_vector = []
        for i in self.move_coordinates:
            probability = 1/len(self.move_coordinates)
            coord_prob = (i,probability)
            base_probability_vector.append(coord_prob)
        return base_probability_vector

    def gen_probability_vector(self,weight = 1):
        base_probability_vector = self.move_probability_base_vector()
        temp_probability_vector = []
        for i in base_probability_vector:
            cell_id = i[0]
            probability = i[1]
            if cell_id == self.current_cell:
                enhanced_prob = probability*weight
                temp_probability_vector.append(enhanced_prob)
            else:
                temp_probability_vector.append(probability)
        return temp_probability_vector

    def normalize_probability_vector(self,weight = 1):
        temp_probability_vector = self.gen_probability_vector(weight = weight)
        denom = sum(temp_probability_vector)
        if denom != 1:
            self.probability_vector = []
            for i in temp_probability_vector:
                probability = i/denom
                self.probability_vector.append(probability)
        else:
            self.probability_vector = temp_probability_vector


    def new_cell(self,current_cell,weight = 1):
        self.move_options(current_cell)
        self.normalize_probability_vector(weight = weight)
        #print(self.move_coordinates)
        #print(self.probability_vector)
        new_cell = self.rng.choices(self.move_coordinates,self.probability_vector,k=1)
        return new_cell[0]


if __name__ ==  "__main__":
    pass



