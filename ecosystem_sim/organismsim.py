#!/usr/bin/python
class Organism(object):
    def __init__(self,sim, energy_counter):
        self.sim = sim
        self.energy_counter = energy_counter
        self.alive = True
        self.rng = self.sim.rng
        self.move = Movement(self.sim)

    def consume(self,energy_gain):
        if energy_gain < 0:
            raise ValueError('gains should be positive integers')
        if self.current_cell.cell_energy_pool > 0:
            self.energy_counter += energy_gain

    def get_energy_counter(self):
        return self.energy_counter

    def expend_energy(self,energy_cost):
        if energy_cost < 0:
            raise ValueError('Costs should be positive integers')
        self.energy_counter -= energy_cost
        self.natural_death

    def natural_death(self):
        if self.energy_counter == 0:
            self.alive = False

    def time_of_day(self,time_of_day):
        if time_of_day >= 0 and time_of_day < 24:
            pass
        else:
            raise ValueError('Not an appropriate time of day')

    def current_cell(self,cell):
        self.current_cell = cell
        self.current_microhabitat = cell.habitat_type 

    def organism_movement(self):
        self.move.move_options(self.current_cell.cell_id)
        new_cell_id = self.move.new_cell(self.current_cell.cell_id)
        return new_cell_id




class Snake(Organism):
    def __init__(self,sim, energy_counter,strike_success_probability,hunting_hours = None):
        super().__init__(sim,energy_counter)
        self.sim = sim
        self.energy_counter = energy_counter
        self._strike_success_probability = strike_success_probability
        self.hunting = False
        self.hunting_hours = self.hunting_period_gen(hunting_hours)
        self.rng = self.sim.rng

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
            hunting_hours = [0,1,2,3,4,5,20,21,22,23]
        return hunting_hours

    def hunting_period(self):
        if self.sim.time_of_day in self.hunting_hours:
            self.hunting = True
        else:
            self.hunting = False


class Krat(Organism):
    def __init__(self,sim,energy_counter,home_cell_id,foraging_hours = None):
        super().__init__(sim,energy_counter)
        self.sim = sim
        self.energy_counter = energy_counter
        self.home_cell_id = home_cell_id
        self.foraging = False
        self.foraging_hours = self.foraging_period_gen(foraging_hours)
        self.rng = self.sim.rng

    def foraging_period_gen(self,foraging_hours):
        if foraging_hours == None:
            foraging_hours = [0,1,2,3,4,5,20,21,22,23]
        return foraging_hours

    def foraging_period(self):
        if self.sim.time_of_day in self.foraging_hours:
            self.foraging = True
        else:
            self.foraging = False

class Movement(object):
    def __init__(self,sim):
        self.column_boundary = sim.landscape.cells_x_columns - 1
        self.row_boundary = sim.landscape.cells_y_rows - 1
        self.rng = sim.rng

    def move_options(self,current_cell):
        self.move_coordinates = []
        for x in [-1,0,1]:
            for y in [-1,0,1]:
                #print('{},{}'.format(x,y))
                row_coord = current_cell[0] + y
                column_coord = current_cell[1] + x
                if row_coord >= 0 and row_coord <= self.row_boundary and column_coord >= 0 and column_coord <= self.column_boundary:
                    new_id = (row_coord,column_coord)
                    self.move_coordinates.append(new_id)
        if len(self.move_coordinates) == 0:
            print(current_cell)
            print(self.row_boundary)
            print(self.column_boundary)
            raise ValueError('No move options')

    def move_probability_base_vector(self):
        self.probability_vector = []
        for i in range(len(self.move_coordinates)):
            probability = 1/len(self.move_coordinates)
            self.probability_vector.append(probability)

    #def weighted_probability_vector(self,enhancment_coeffiecent):
        #self.weighted_probability_vector = []
        #for i in self.probability_vector:


    def new_cell(self,current_cell):
        self.move_options(current_cell)
        self.move_probability_base_vector()
        new_cell = self.rng.choices(self.move_coordinates,self.probability_vector,k=1)
        return new_cell[0]


if __name__ ==  "__main__":
    pass

