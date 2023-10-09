#!/usr/bin/python


class Cell(object):
    '''
    This object represents a sub space of the landscape object that is a container for organisms to interact in.
    The user will have to keep in mind the abstract size of these interaction landscapes when setting up simulation variables.
    Args:
        sim -- the simulation object with base parameters such as a random number generator and a time parameter. (sim object)
        habitat_type -- this is a label from an enumerated habitat object. (enum object)
        cell_id -- a tuple of the postion of the cell on the landscape in the y direction (rows) and the landscape in the x direction (columns). (tuple with 2 elements)
    Attributes:
        krats -- a list that holds krat objects. (list)
        snakes -- a list that holds sake objects. (list)
        landscape -- the landscape object the cell operates in.
        rng -- a random number operator object.
    '''
    def __init__(self, sim, habitat_type,cell_id,prey_competition=False):
        self.sim = sim
        self.krats = []
        self.snakes = []
        self.owls = []
        self.habitat_type = habitat_type
        self.landscape = sim.landscape
        self.cell_id = cell_id
        self.prey_competition = prey_competition     
        self.rng = self.sim.rng

    def __hash__(self):
        return id(self)

    def add_krat(self, krat):
        '''Add a krat to the population of this cells krats'''
        self.krats.append(krat)

    def add_snake(self, snake):
        '''Add a snake to the population of this cells snakes'''
        self.snakes.append(snake)

    def add_owl(self,owl):
        '''adds an owl object to the landscape.'''
        self.owls.append(owl)

    def select_krat(self,krat_index = None):
        '''returns a random krat object if no specific index is provided.'''
        if krat_index == None:
            krat_index = self.rng.randint(0,len(self.krats)-1)
        krat = self.krats[krat_index]
        return krat

    def select_snake(self,snake_index = None):
        '''returns a random snake object if no specific index is provided.'''
        if snake_index == None:
            snake_index = self.rng.randint(0,len(self.snake)-1)
        snake = self.snakes[snake_index]
        return snake

    def pop_krat(self,krat_index):
        '''Selects a krat at random from population and removes it and returns the object '''
        return self.krats.pop(krat_index)

    def pop_snake(self,snake_index):
        '''Selects a snake at random from population and removes it and returns the object '''
        return self.snakes.pop(snake_index)

    def clean_krat_list(self):
        '''creates a fresh list for the attribute krats'''
        self.krats = []

    def clean_snake_list(self):
        '''creates a fresh list for the attribute snakes'''
        self.snakes = []

    def cell_over_populated(self):
        '''test that makes sure cells don't become overpopulated and break sim'''
        if len(self.krats) > self.sim.initial_krat_pop:
            raise ValueError("Krats mating too much")
        if len(self.snakes) > self.sim.initial_snake_pop:
            raise ValueError("snakes mating too much")

    def krat_move(self, krat,moving_krat_list,return_home=False):
        '''runs the krat movement algorithm and moves the krat from the cell to a temp list in the landscape. 
        Optional can designate the krat to return to designated nest cell tied to the krat object.'''
        if return_home== True:
            new_cell = krat.return_home()
        else:
            new_cell = krat.organism_movement()
        if new_cell != self:
            moving_krat = (new_cell,krat,self)
            self.landscape.krat_move_pool.append(moving_krat)
            moving_krat_list.append(krat)

    def snake_move(self,snake,moving_snake_list):
        '''runs the snake movement algorithm and moves the krat from the cell to a temp list in the landscape. '''
        new_cell = snake.organism_movement()
        if new_cell != self:
            moving_snake = (new_cell,snake,self)
            self.landscape.snake_move_pool.append(moving_snake)
            moving_snake_list.append(snake)

    def owl_move(self,owl,moving_owl_list):
        '''runs the owl movement algorithm and moves the krat from the cell to a temp list in the landscape. '''
        new_cell = owl.organism_movement()
        if new_cell != self:
            moving_owl = (new_cell,owl,self)
            self.landscape.owl_move_pool.append(moving_owl)
            moving_owl_list.append(owl)             

    def krat_predation_by_snake(self,snake):
        '''determines whether or not the snake that was passed into the function successfully kills and obtains payoff of a krat that shares the cell with it.'''
        live_krats = [krat for krat in self.krats if krat.alive] 
        ss = snake.calc_strike_success_probability(self)
        energy_cost = snake.energy_cost
        if len(live_krats) > 0 and self.rng.random() < ss:
            krat_index = self.rng.randint(0,len(live_krats)-1)
            krat = self.select_krat(krat_index = krat_index)
            krat.alive = False
            energy_gain = snake.energy_gain_per_krat              
        else:
            energy_gain = 0
        energy_delta = (energy_gain - energy_cost)
        snake.energy_score += energy_delta

    def krat_predation_by_owl(self,owl):
        '''determines whether or not the owl that was passed into the function successfully kills and obtains payoff of a krat that shares the cell with it.'''
        live_krats = [krat for krat in self.krats if krat.alive] 
        if len(live_krats) > 0 and self.rng.random() < owl.strike_success_probability and self.habitat_type[0].name == 'OPEN':
            krat_index = self.rng.randint(0,len(live_krats)-1)
            krat = self.select_krat(krat_index = krat_index)
            krat.alive = False

    def foraging_rat(self,krat):
        '''Provides krat with appropriate pay off for foraging in the cell.'''
        if self.prey_competition:
            krat_energy_gain = krat.calc_energy_gain(self)/len(self.krats)
        else:
            krat_energy_gain = krat.calc_energy_gain(self)
        krat_energy_cost = krat.calc_energy_cost()
        energy_delta = (krat_energy_gain - krat_energy_cost)
        krat.energy_score += energy_delta

    def krat_activity_pulse_behavior(self):
        """ Krat function, this is the general behavior of either moving or foraging of the krat for one activity pulse."""
        moving_krats = []
        for krat in self.krats:
            if (self.sim.cycle % self.sim.data_sample_frequency) == 0 and krat.alive:
                krat.generate_krat_stats()
            self.foraging_rat(krat)
            if self.sim.cycle % krat.movement_frequency == 0 and self.sim.cycle != 0 and krat.alive:
                self.krat_move(krat,moving_krat_list = moving_krats)           
        self.krats = [krat for krat in self.krats if krat not in moving_krats and krat.alive]     

    def snake_activity_pulse_behavior(self):
        """ snake function, this is the general behavior of either moving or hunting of the krat for one activity pulse."""
        moving_snakes = []
        for snake in self.snakes:
            snake.snake_death()
            if (self.sim.cycle % self.sim.data_sample_frequency) == 0 and snake.alive:
                snake.generate_snake_stats()
            self.krat_predation_by_snake(snake)
            if self.sim.cycle % snake.movement_frequency == 0 and self.sim.cycle != 0 and snake.alive: 
                self.snake_move(snake, moving_snake_list=moving_snakes)            
        self.snakes = [snake for snake in self.snakes if snake not in moving_snakes and snake.alive]

    def owl_activity_pulse_behavior(self):
        moving_owls = []
        for owl in self.owls:
            self.krat_predation_by_owl(owl)
            self.owl_move(owl, moving_owl_list=moving_owls)
        self.owls = [owl for owl in self.owls if owl not in moving_owls]