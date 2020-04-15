import pygame
import random
import Organisms

class sim:
    def __init__(self,initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop):
        # Parameters
        self.width =800
        self.height = 600
        self.background_color = (255,255,255)
        self.start = pygame.font.init()
        self.initial_snake_pop = initial_snake_pop
        self.initial_kr_pop = initial_kr_pop
        self.initial_bush_pop = initial_bush_pop
        self.initial_grass_pop = initial_grass_pop
        self.clock = pygame.time.Clock()
        self.title = 'Snake Vs Kangaroo Rat'
        self.game_display = pygame.display.set_mode((self.width,self.height))
        self.caption = pygame.display.set_caption(self.title)
        self.font = pygame.font.SysFont(None, 25)

    def background(self):
        'Generates Game Background. This should be run first.'
        self.game_display.fill(self.background_color)

    def add_organisms(self,org_list,org_type):
        '''This function designates shape and color of objects depending on the organism type.
        org type is either KRAT, SNAKE, BUSH, GRASS.'''
        if org_type == 'KRAT':   
            for org in org_list:
                pygame.draw.circle(self.game_display,org.color,[org.x,org.y],org.size)
                org.krat_move()
        elif org_type == 'SNAKE':
            for org in org_list:
                pygame.draw.circle(self.game_display,org.color,[org.x,org.y],org.size)
                org.snake_move()
        elif org_type in ['BUSH','GRASS']:
            for org in org_list:
                pygame.draw.rect(self.game_display,org.color,(org.x,org.y,org.wid,org.length))
        pygame.display.update()
    
    def set_organisms(self):
        self.SNAKES = dict(enumerate([Organisms.snake(Organisms.snake.animal_color('red'),6,self.width,self.height) for i in range(self.initial_snake_pop)]))
        self.KANGAROO_RATS = dict(enumerate([Organisms.kangaroo_rat(Organisms.kangaroo_rat.animal_color('blue'),3,self.width,self.height) for i in range(self.initial_kr_pop)]))
        self.BUSHES = dict(enumerate([Organisms.bush(self.width,self.height) for i in range(self.initial_bush_pop)]))
        self.GRASSES = dict(enumerate([Organisms.grass(self.width,self.height) for i in range(self.initial_grass_pop)]))
    
    def time_set(self,n,time_counter,fps):
        if (n % 13) == 0:
            return time_counter+1
        else:
            return time_counter
    
    def population_counts_and_time(self,count,num_snakes,num_rats):
        self.text1 = self.font.render("Time Step: "+str(count), True, (0,0,0))
        self.game_display.blit(self.text1,(0,0))
        self.text2 = self.font.render("Snakes: "+ str(len(num_snakes)), True, (0,0,0))
        self.game_display.blit(self.text2,(0,20))
        self.text3 = self.font.render("Kangaroo Rats: "+ str(len(num_rats)), True, (0,0,0))
        self.game_display.blit(self.text3,(0,40))

    def main(self):
        '''Main function that runs and compiles the program'''
        time_counter=0
        n = 0
        self.set_organisms()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            self.background()
            self.population_counts_and_time(time_counter,self.SNAKES,self.KANGAROO_RATS)
            self.add_organisms(self.SNAKES.values(),'SNAKE')
            self.add_organisms(self.KANGAROO_RATS.values(),'KRAT')
            self.add_organisms(self.BUSHES.values(),'BUSH')
            self.add_organisms(self.GRASSES.values(),'GRASS')
            self.clock.tick(30)
            n=n+1
            time_counter = self.time_set(n,time_counter,30)
            #print(time_counter)
    
if __name__ ==  "__main__":
    initial_snake_pop = 5
    initial_kr_pop = 20
    initial_bush_pop = 3
    initial_grass_pop = 400
    sim = sim(initial_snake_pop,initial_kr_pop,initial_bush_pop,initial_grass_pop)
    sim.main()
    
