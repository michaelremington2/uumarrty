import pygame
import random
import Organisms
import time
#import pandas as pd
#from collections import Counter

class sim:
    def __init__(self,initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop):
        # Parameters
        self.width =800
        self.height = 600
        self.background_color = (255,255,255)
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
        self.dead_kr = 0
        self.dead_snake = 0 
        self.dead_grass = 0 
        self.dead_bush = 0
        self.kr_energy = 0
        self.snake_energy = 0

    def background(self):
        'Generates Game Background. This should be run first.'
        self.game_display.fill(self.background_color)

    def set_organisms(self):
        self.SNAKES = dict(enumerate(
            [Organisms.snake(self.width,self.height) for i in range(self.initial_snake_pop)]
            ))
        self.KANGAROO_RATS = dict(enumerate(
            [Organisms.kangaroo_rat(self.width,self.height) for i in range(self.initial_kr_pop)]
            ))
        self.BUSHES = dict(enumerate(
            [Organisms.bush(self.width,self.height) for i in range(self.initial_bush_pop)]
            ))
        self.GRASSES = dict(enumerate(
            [Organisms.grass(self.width,self.height) for i in range(self.initial_grass_pop)]
            ))

    def add_organisms(self,org_list,org_type,time):
        '''This function designates shape, color, and sets energy and move counters of objects depending on the organism type.
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
        for i, snake in self.SNAKES.items():
            for j, kr in self.KANGAROO_RATS.items():
                dx = abs(kr.x - snake.x)
                dy = abs(kr.y - snake.y)
                R = 5
                if dx <= R and dy <= R:
                    chance_to_kill = 50
                    strike = random.randrange(0,100)
                    if strike <= chance_to_kill:
                        kr.alive = False
                        kr.krat_dead()
                        snake.energy_counter += kr.energy_counter*snake.metabolism
                        pygame.display.update()

    def krat_grass_attack(self):
        for i, grass in self.GRASSES.items():
            for j, kr in self.KANGAROO_RATS.items():
                dx = abs(grass.x - kr.x)
                dy = abs(grass.y - kr.y)
                R = 3
                if dx <= R and dy <= R:
                    grass.alive = False
                    grass.grass_dead()
                    self.dead_grass += 1
                    kr.energy_counter += grass.energy_counter*kr.metabolism
                    pygame.display.update()
    
    def krat_bush_attack(self):
        for i, bush in self.BUSHES.items():
            for j, kr in self.KANGAROO_RATS.items():
                dx = abs(bush.x - kr.x)
                dy = abs(bush.y - kr.y)
                R = 5
                if dx <= R and dy <= R:
                    kr.energy_counter += 10*kr.metabolism
                    bush.energy_counter += -10
                    bush.bush_dead()
                    pygame.display.update()

    def krat_energy_total(self,time_counter):
        kr=self.KANGAROO_RATS.get(1)
        print('Kangaroo Rat 1 Energy Counter ' + str(kr.energy_counter)+ 'time: ' +str(time_counter))

    def krat_count(self):
        dead_krat_list = []
        for j, kr in self.KANGAROO_RATS.items():
            if kr.alive == False:
                dead_krat_list.append(j)
        self.dead_kr=len(set(dead_krat_list))

    def snake_count(self):
        dead_snake_list = []
        for j, snake in self.SNAKES.items():
            if snake.alive == False:
                dead_snake_list.append(j)
        self.dead_snake=len(set(dead_snake_list))
    
    def stopwatch(self,seconds):
        start = round(time.time())
        elapsed = 0
        while elapsed < seconds:
            elapsed = round(time.time()) - start
    
    def population_counts_and_time(self,time,num_snakes,num_rats):
        '''Sets legend. counts for time, snake population, and krat population'''
        self.text1 = self.font.render("Time Step: "+str(time), True, (0,0,0))
        self.game_display.blit(self.text1,(0,0))
        self.text2 = self.font.render("Snakes: "+ str(len(num_snakes)-self.dead_snake), True, (0,0,0))
        self.game_display.blit(self.text2,(0,20))
        self.text3 = self.font.render("Kangaroo Rats: "+ str(len(num_rats) - self.dead_kr), True, (0,0,0))
        self.game_display.blit(self.text3,(0,40))

    def main(self):
        '''Main function that runs and compiles the program'''
        fps = 30
        start = round(time.time())
        time_counter = 0
        self.set_organisms()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            self.background()
            self.population_counts_and_time(time_counter,self.SNAKES,self.KANGAROO_RATS)
            self.add_organisms(self.SNAKES.values(),'SNAKE',time_counter)
            self.add_organisms(self.KANGAROO_RATS.values(),'KRAT',time_counter)
            self.add_organisms(self.BUSHES.values(),'BUSH',time_counter)
            self.add_organisms(self.GRASSES.values(),'GRASS',time_counter)
            self.snake_attack()
            self.krat_grass_attack()
            self.krat_bush_attack()
            #self.krat_energy_total(time_counter)
            self.clock.tick(fps)
            self.krat_count()
            time_counter = round(time.time()) - start
    
if __name__ ==  "__main__":
    initial_snake_pop = 5
    initial_kr_pop = 30
    initial_bush_pop = 2
    initial_grass_pop = 100
    sim = sim(initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop)
    sim.main()
