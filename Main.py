import pygame
import random
import organisms
import time
import numpy as np 


class sim:
    def __init__(self,initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop, end_time=0):
        # Parameters
        self.width = 800
        self.height = 600
        self.background_color=(255,255,255)
        self.start = pygame.init()
        self.initial_snake_pop = initial_snake_pop
        self.initial_kr_pop = initial_kr_pop
        self.initial_bush_pop = initial_bush_pop
        self.initial_grass_pop = initial_grass_pop
        self.clock = pygame.time.Clock()
        self.title = 'Snake Vs Kangaroo Rat'
        self.game_display = pygame.display.set_mode((self.width,self.height))
        self.caption = pygame.display.set_caption(self.title)
        self.font = pygame.font.SysFont(None, 25)
        self.climate_grid = {}
        self.open_area_keys = []
        self.bush_area_keys = []
        self.climate_grid_gen()
        self.dead_kr_list = []
        self.dead_snake_list = []
        self.dead_grass_list = []
        self.krat_energy_check = []
        self.snake_energy = 0
        self.time_history = {}
        self.end_time = end_time

    def background(self):
        '''Generates Game Background. This should be run first.'''
        self.game_display.fill(self.background_color)

    def microclimate_key_list_gen(self,microclimate_key,climate_type):
        if climate_type == 'bush':
            self.bush_area_keys.append(microclimate_key)
        elif climate_type == 'open':
            self.open_area_keys.append(microclimate_key)
        else:
            raise ValueError('Too many microclimates defined')

    def climate_grid_gen_retired(self):
        ''' This function breaks the game grid into 15 rectangular microclimates and labels them as such.
        The microclimate sizes are 200(h) x 160(w) pixels'''
        micro_height = 200
        micro_width = 160
        microclimate_key = 1
        while microclimate_key <= 15:
            for y in range(0,self.height, micro_height):
                for x in range(0,self.width,micro_width):
                    climate_type = random.choice(['open','bush'])
                    self.microclimate_key_list_gen(microclimate_key,climate_type)
                    if microclimate_key not in self.climate_grid:
                        microclimate_grid = (np.arange(x,x+micro_width),np.arange(y,y+micro_height))
                        self.climate_grid[microclimate_key] = [climate_type,microclimate_grid]
                    microclimate_key += 1

    def micro_climate_grid_gen(self,start_x,start_y):
        ''' This function breaks the game grid into 15 rectangular microclimates and labels them as such.
        The microclimate sizes are 200(h) x 160(w) pixels'''
        micro_height = 200
        micro_width = 160
        micro_grid = []
        for x in range(start_x,start_x+micro_width):
            for y in range(start_y,start_y+micro_height):
                point = (x,y)
                micro_grid.append(point)
        return np.array(micro_grid)

    def climate_grid_gen(self):
        ''' This function breaks the game grid into 15 rectangular microclimates and labels them as such.
        The microclimate sizes are 200(h) x 160(w) pixels'''
        micro_height = 200
        micro_width = 160
        microclimate_key = 1
        start_x_list = list(range(0,self.width,micro_width))
        start_y_list = list(range(0,self.height,micro_height))
        microclimate_key = 1
        for x in start_x_list:
            for y in start_y_list:
                climate_type = random.choice(['open','bush'])
                self.microclimate_key_list_gen(microclimate_key,climate_type)
                if microclimate_key not in self.climate_grid:
                    microclimate_grid = self.micro_climate_grid_gen(x,y)
                    self.climate_grid[microclimate_key] = [climate_type,microclimate_grid]
                microclimate_key += 1
                if microclimate_key > 15:
                    break
                 

    def set_organisms(self):
        '''Initiates enumierated dictionaries of all the organism objects based on initial populations and randomly 
        places objects across the area of the board.'''
        self.bushes_dict = dict(enumerate(
            [organisms.bush(self.climate_grid,self.bush_area_keys,self.width,self.height) for i in range(self.initial_bush_pop)]
            ))
        self.grasses_dict = dict(enumerate(
            [organisms.grass(self.climate_grid,self.open_area_keys,self.width,self.height) for i in range(self.initial_grass_pop)]
            ))
        self.snake_dict = dict(enumerate(
            [organisms.snake(self.width,self.height) for i in range(self.initial_snake_pop)]
            ))
        self.krat_dict = dict(enumerate(
            [organisms.kangaroo_rat(self.width,self.height) for i in range(self.initial_kr_pop)]
            ))

    #def org_microhabitat_check(self,org_x_coord,org_y_coord):
    #    for key, microclimates in self.climate_grid.items():



    def add_organisms(self,org_list,org_type):
        '''Designates shape, color, and sets energy and move counters of objects depending on the organism type.
        org type is either KRAT, SNAKE, BUSH, GRASS.'''
        if org_type == 'KRAT':   
            for org in org_list:
                org.krat_energy(self.time_counter)
                pygame.draw.circle(self.game_display,org.color,[org.x,org.y],org.size)
                org.krat_move()
        elif org_type == 'SNAKE':
            for org in org_list:
                org.snake_energy(self.time_counter)
                pygame.draw.circle(self.game_display,org.color,[org.x,org.y],org.size)
                org.snake_move()
                #org.move()
        elif org_type in ['BUSH','GRASS']:
            for org in org_list:
                pygame.draw.rect(self.game_display,org.color,(org.x,org.y,org.wid,org.length))
        pygame.display.update()
    
    def snake_attack(self):
        '''Establishes the likelyhood (set to 50% chance probability) of a rattlesnake killing a kangaroo rat if it enters
        a radius of 5 pixels. If a strike is succesful the kangaroo rat is set to be dead and the energy is then added 
        to the snakes energy counter based on how much it metabalizes.'''
        for i, snake in self.snake_dict.items():
            for j, kr in self.krat_dict.items():
                dx = abs(kr.x - snake.x) # assess distance of rattle snake and krat
                dy = abs(kr.y - snake.y)
                R = 5 #radius of strikes
                if dx <= R and dy <= R:
                    chance_to_kill = 95 #probability a kill is successful
                    strike = random.randrange(0,100)
                    if strike <= chance_to_kill:
                        snake.energy_counter += kr.energy_counter*snake.metabolism #metabolism
                        kr.alive = False
                        kr.krat_dead()
                        pygame.display.update()

    def krat_grass_attack(self):
        '''Establishes kangaroo rats eating grass if it is in a 3 pixel  radius range of a grass. There is a 100% likelyhood
        of the kangaroo rat eating the grass if it enters the range. The grass is then set as dead and the energy is transfered to
        the kangaroo rat based on it's metabolism.'''
        for i, grass in self.grasses_dict.items():
            for j, kr in self.krat_dict.items():
                if kr.energy_counter <= kr.hunger_level:
                    dx = abs(grass.x - kr.x)
                    dy = abs(grass.y - kr.y)
                    R = 3 # radius of interest
                    if dx <= R and dy <= R:
                        grass.alive = False
                        kr.energy_counter += grass.energy_counter*kr.metabolism #metabolism
                        grass.grass_dead()
                        pygame.display.update()
    
    def krat_bush_attack(self):
        '''Establishes kangaroo rats eating off bushes if it is in a 5 pixel  radius range of a bush. There is a 100% likelyhood
        of the kangaroo rat eating off the bush if it enters the range. The kangaroo rat only eats 10 units of energy during an encounter and
        is converted based on it's metabolism.'''
        for i, bush in self.bushes_dict.items():
            for j, kr in self.krat_dict.items():
                dx = abs(bush.x - kr.x)
                dy = abs(bush.y - kr.y)
                R = 5
                if dx <= R and dy <= R:
                    kr.energy_counter += 50*kr.metabolism
                    bush.energy_counter += -50
                    bush.bush_dead()
                    pygame.display.update()

    def organism_breed_type(self,org_type):
        if org_type == 'KRAT':
            x = organisms.kangaroo_rat(self.width,self.height)
        elif org_type == 'SNAKE':
            x = organisms.snake(self.width,self.height)
        elif org_type == 'GRASS':
            x = organisms.grass(self.width,self.height)
        return x

    def breed(self,organism_dict,org_type):
        if self.time_counter not in self.time_history:
            #print('I made it 1 deep!')
            for i,org in organism_dict.items():
                prob = random.random() #number to check against breed probability
                if prob <= org.litters_per_year:
                    babies ={}
                    #print('I made it 2 deep!')
                    for i in range(org.children):
                        max_key = max(organism_dict.keys())
                        if (max_key+i) not in organism_dict and (max_key+i) not in babies:
                            org_object = self.organism_breed_type(org_type)
                            babies[(max_key+i)] = org_object
            try:
                organism_dict.update(babies)
            except UnboundLocalError:
                pass     

    def krat_energy_total(self):
        '''Checks how an individual kangaroo rats metabolism changes over time for troublshooting.'''
        try:
            kr=self.krat_dict.get(1)
            #print('Kangaroo Rat 1 Energy Counter ' + str(kr.energy_counter)+ ' time: ' +str(time_counter))
            self.krat_energy_check.append((self.time_counter,kr.energy_counter))
        except AttributeError:
            self.program_quit()

    def krat_grave(self):
        '''Populates set of dead krat ID's to be used in the program for establishing counters. 
        Filters out dead Kangaroo Rats from the main kangaroo rat dictionary to save computational space.'''
        for j, kr in self.krat_dict.items():
            if kr.alive == False:
                self.dead_kr_list.append(j)
            self.krat_dict = dict((j, self.krat_dict[j]) for j in self.krat_dict if j not in self.dead_kr_list)

    def snake_grave(self):
        '''Populates set of dead snake ID's to be used in the program for establishing counters. 
        Filters out dead snakes from the main snake dictionary to save computational space.'''
        for j, snake in self.snake_dict.items():
            if snake.alive == False:
                self.dead_snake_list.append(j)
            self.snake_dict = dict((j, self.snake_dict[j]) for j in self.snake_dict if j not in self.dead_snake_list)

    def grass_grave(self):
        '''Populates set of dead grass ID's to be used in the program for establishing counters. 
        Filters out dead grasses from the main grass dictionary to save computational space.'''
        for j, grass in self.grasses_dict.items():
            if grass.alive == False:
                self.dead_grass_list.append(j)
            self.grasses_dict = dict((j, self.grasses_dict[j]) for j in self.grasses_dict if j not in self.dead_grass_list)
    
    def stopwatch(self,seconds):
        '''This function was just for tests of the systems clock.'''
        start = round(time.time())
        elapsed = 0
        while elapsed < seconds:
            elapsed = round(time.time()) - start
    
    def population_counts_and_time(self,num_snakes,num_rats,num_grass):
        '''Sets legend. counts for time, snake population, and krat population'''
        self.text1 = self.font.render("Time Step: "+str(self.time_counter), True, (0,0,0))
        self.game_display.blit(self.text1,(0,0))
        self.text2 = self.font.render("Snakes: "+ str(len(self.snake_dict)), True, (0,0,0))
        self.game_display.blit(self.text2,(0,20))
        self.text3 = self.font.render("Kangaroo Rats: "+ str(len(self.krat_dict)), True, (0,0,0))
        self.game_display.blit(self.text3,(0,40))
        self.text4 = self.font.render("Grass: "+ str(num_grass- len(self.dead_grass_list)), True, (0,0,0))
        self.game_display.blit(self.text4,(0,55))

    def program_quit(self):
        '''Quits python and pygame when run.'''
        print(self.climate_grid[1])
        print(self.climate_grid[15])
        pygame.quit()
        quit() 

    def program_time(self):
        '''Runs quit system program once the end time (seconds) is reached.'''
        if self.end_time !=0:
            if self.time_counter == self.end_time:
                self.program_quit()
                

    def history(self):
        '''Creates a dictionary for analysis on how things change over time in the system.'''
        snake_count = len(self.snake_dict)
        krat_count = len(self.krat_dict)
        grass_count = len(self.grasses_dict)
        data = [snake_count,krat_count,grass_count]
        if self.time_counter not in self.time_history:
            self.time_history[self.time_counter] = data           

    def main(self):
        '''Main function that runs and compiles the program'''
        fps = 40
        start = round(time.time())
        self.time_counter = 0
        self.set_organisms()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.program_quit()
            self.background()
            self.population_counts_and_time(self.initial_snake_pop,self.initial_kr_pop,self.initial_grass_pop)
            self.add_organisms(self.snake_dict.values(),'SNAKE')
            self.add_organisms(self.krat_dict.values(),'KRAT')
            self.add_organisms(self.bushes_dict.values(),'BUSH')
            self.add_organisms(self.grasses_dict.values(),'GRASS')
            self.snake_attack()
            self.krat_grass_attack()
            self.krat_bush_attack()
            #self.krat_energy_total(time_counter)
            self.clock.tick(fps)
            self.krat_grave()
            self.snake_grave()
            self.grass_grave()
            self.time_counter = round(time.time()) - start
            self.breed(self.krat_dict,'KRAT')
            self.breed(self.snake_dict,'SNAKE')
            self.history()
            self.program_time()
    
if __name__ ==  "__main__":
    initial_snake_pop = 15
    initial_kr_pop = 40
    initial_bush_pop = 40
    initial_grass_pop = 500
    sim = sim(initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop)
    sim.main()
