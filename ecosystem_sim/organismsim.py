#!/usr/bin/python
class Organism(object):
    def __init__(self,sim, energy_counter):
        self.sim = sim
        self.energy_counter = energy_counter
        self.alive = True
        self.rng = self.sim.rng

    def consume(self,energy_gain):
        if energy_gain < 0:
            RaiseValueError('gains should be positive integers')
        if self.current_cell.cell_energy_pool > 0:
            self.energy_counter += energy_gain

    def get_energy_counter(self):
        return self.energy_counter

    def expend_energy(self,energy_cost):
        if energy_cost < 0:
            RaiseValueError('Costs should be positive integers')
        self.energy_counter -= energy_cost

    def natural_death(self):
        if self.energy_counter == 0:
            self.alive = False

    def time_of_day(self,time_of_day):
        if time_of_day >= 0 and time_of_day < 24:
            pass
        else:
            RaiseValueError('Not an appropriate time of day')

    def current_cell(self,cell):
        self.current_cell = cell
        self.current_microhabitat = cell.habitat_type 


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
