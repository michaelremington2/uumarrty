class Organism(object):
    def __init__(self,energy_counter,rng):
        self.energy_counter = energy_counter
        self.landscape = landscape
        self.alive = True
        self.rng = landscape.rng

    def consume(self,energy_gain):
        if energy_cost < 0:
            RaiseValueError('gains should be positive integers')
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


class Snake(Organism):
    def __init__(self,energy_counter,strike_success_probability,hunting_hours = None,rng):
        super().__init__(landscape,energy_counter)
        self.energy_counter = energy_counter
        self.strike_success_probability = strike_success_probability
        self.hunting = False
        self.hunting_hours = self.hunting_period_gen(hunting_hours)
        self.rng = rng

    def hunting_period_gen(self,hunting_hours):
        if hunting_hours == None:
            hunting_hours = [0,1,2,3,4,5,20,21,22,23]
        return hunting_hours

    def hunting_period(self,time_of_day):
        if time_of_day in hunting_hours:
            self.hunting = True
        else:
            self.hunting = False


class Krat(Organism):
    def __init__(self,energy_counter,home_cell,rng):
        super().__init__(landscape,energy_counter)
        self.energy_counter = energy_counter
        self.home_cell = home_cell
        self.foraging = False
        self.rng = rng

    def hunting_period_gen(self,foraging_hours):
        if foraging_hours == None:
            foraging_hours = [0,1,2,3,4,5,20,21,22,23]
        return foraging_hours

    def foraging_period(self,time_of_day):
        if time_of_day in foraging_hours:
            self.foraging = True
        else:
            self.foraging = False
