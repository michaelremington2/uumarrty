import pygame
import random
import organisms
import time

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
        self.dead_kr_list = []
        self.dead_snake_list = []
        self.dead_grass_list = []
        self.kr_energy = 0
        self.snake_energy = 0
        self.end_time = end_time

    def background(self):
        '''Generates Game Background. This should be run first.'''
        self.game_display.fill(self.background_color)

    def set_organisms(self):
        '''Initiates enumierated dictionaries of all the organism objects based on initial populations and randomly 
        places objects across the area of the board.'''
        self.snake_dict = dict(enumerate(
            [organisms.snake(self.width,self.height) for i in range(self.initial_snake_pop)]
            ))
        self.krat_dict = dict(enumerate(
            [organisms.kangaroo_rat(self.width,self.height) for i in range(self.initial_kr_pop)]
            ))
        self.bushes_dict = dict(enumerate(
            [organisms.bush(self.width,self.height) for i in range(self.initial_bush_pop)]
            ))
        self.grasses_dict = dict(enumerate(
            [organisms.grass(self.width,self.height) for i in range(self.initial_grass_pop)]
            ))

    def add_organisms(self,org_list,org_type,time):
        '''Designates shape, color, and sets energy and move counters of objects depending on the organism type.
        org type is either KRAT, SNAKE, BUSH, GRASS.'''
        if org_type == 'KRAT':   
            for org in org_list:
                org.krat_energy(time)
                pygame.draw.circle(self.game_display,org.color,[org.x,org.y],org.size)
                org.krat_move()
        elif org_type == 'SNAKE':
            for org in org_list:
                org.snake_energy(time)
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
                    chance_to_kill = 90 #probability a kill is successful
                    strike = random.randrange(0,100)
                    if strike <= chance_to_kill:
                        kr.alive = False
                        kr.krat_dead()
                        snake.energy_counter += kr.energy_counter*snake.metabolism #metabolism
                        pygame.display.update()

    def krat_grass_attack(self):
        '''Establishes kangaroo rats eating grass if it is in a 3 pixel  radius range of a grass. There is a 100% likelyhood
        of the kangaroo rat eating the grass if it enters the range. The grass is then set as dead and the energy is transfered to
        the kangaroo rat based on it's metabolism.'''
        for i, grass in self.grasses_dict.items():
            for j, kr in self.krat_dict.items():
                dx = abs(grass.x - kr.x)
                dy = abs(grass.y - kr.y)
                R = 3 # radius of interest
                if dx <= R and dy <= R:
                    grass.alive = False
                    grass.grass_dead()
                    kr.energy_counter += grass.energy_counter*kr.metabolism #metabolism
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
                    kr.energy_counter += 10*kr.metabolism
                    bush.energy_counter += -10
                    bush.bush_dead()
                    pygame.display.update()

    def krat_energy_total(self,time_counter):
        '''Checks how an individual kangaroo rats metabolism changes over time for troublshooting.'''
        kr=self.krat_dict.get(1)
        print('Kangaroo Rat 1 Energy Counter ' + str(kr.energy_counter)+ 'time: ' +str(time_counter))

    def krat_count(self):
        '''Populates set of dead krat ID's to be used in the program for establishing counters. 
        Filters out dead Kangaroo Rats from the main kangaroo rat dictionary to save computational space.'''
        for j, kr in self.krat_dict.items():
            if kr.alive == False:
                self.dead_kr_list.append(j)
            self.krat_dict = dict((j, self.krat_dict[j]) for j in self.krat_dict if j not in self.dead_kr_list)

    def snake_count(self):
        '''Populates set of dead snake ID's to be used in the program for establishing counters. 
        Filters out dead snakes from the main snake dictionary to save computational space.'''
        for j, snake in self.snake_dict.items():
            if snake.alive == False:
                self.dead_snake_list.append(j)
            self.snake_dict = dict((j, self.snake_dict[j]) for j in self.snake_dict if j not in self.dead_snake_list)

    def grass_count(self):
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
    
    def population_counts_and_time(self,time,num_snakes,num_rats,num_grass):
        '''Sets legend. counts for time, snake population, and krat population'''
        self.text1 = self.font.render("Time Step: "+str(time), True, (0,0,0))
        self.game_display.blit(self.text1,(0,0))
        self.text2 = self.font.render("Snakes: "+ str(num_snakes-len(self.dead_snake_list)), True, (0,0,0))
        self.game_display.blit(self.text2,(0,20))
        self.text3 = self.font.render("Kangaroo Rats: "+ str(num_rats - len(self.dead_kr_list)), True, (0,0,0))
        self.game_display.blit(self.text3,(0,40))
        self.text4 = self.font.render("Grass: "+ str(num_grass- len(self.dead_grass_list)), True, (0,0,0))
        self.game_display.blit(self.text4,(0,55))

    def program_quit(self):
        '''Quits python and pygame when run.'''
        pygame.quit()
        quit() 

    def program_time(self,time_counter):
        '''Runs quit system program once the end time (seconds) is reached.'''
        if self.end_time !=0:
            if time_counter == self.end_time:
                self.program_quit()         

    def main(self):
        '''Main function that runs and compiles the program'''
        fps = 30
        start = round(time.time())
        time_counter = 0
        self.set_organisms()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.program_quit()
            self.background()
            self.population_counts_and_time(time_counter,self.initial_snake_pop,self.initial_kr_pop,self.initial_grass_pop)
            self.add_organisms(self.snake_dict.values(),'SNAKE',time_counter)
            self.add_organisms(self.krat_dict.values(),'KRAT',time_counter)
            self.add_organisms(self.bushes_dict.values(),'BUSH',time_counter)
            self.add_organisms(self.grasses_dict.values(),'GRASS',time_counter)
            self.snake_attack()
            self.krat_grass_attack()
            self.krat_bush_attack()
            #self.krat_energy_total(time_counter)
            self.clock.tick(fps)
            self.krat_count()
            self.snake_count()
            self.grass_count()
            time_counter = round(time.time()) - start
            self.program_time(time_counter)
    
if __name__ ==  "__main__":
    initial_snake_pop = 5
    initial_kr_pop = 30
    initial_bush_pop = 2
    initial_grass_pop = 500
    sim = sim(initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop,60)
    sim.main()
    
