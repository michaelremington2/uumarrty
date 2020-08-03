import random
import pygame
import time

class organism:
    def __init__(self,color,size,boundary_x=800,boundary_y= 600):
        self.color = color
        self.size = size
        self.boundary_y = boundary_y
        self.boundary_x = boundary_x
        self.x = random.randrange(0,boundary_x)
        self.y = random.randrange(0,boundary_x)
        self.point =(self.x,self.y)
    
    def animal_color(self,color_name):
        ''' red, blue, green, white, black, random'''
        colors={
            'red' : (255,0,0),
            'blue': (0,0,255),
            'green':(0,255,0),
            'white': (255,255,255),
            'black': (0,0,0),
            'random':(random.randrange(0,255),random.randrange(0,255),random.randrange(0,255))
        }
        return colors[color_name]

    def boundary(self):
        if self.x > self.boundary_x:
            self.x = self.boundary_x
        elif self.x < 0:
            self.x = 0
        if self.y > self.boundary_y:
            self.y = self.boundary_y
        elif self.y < 0:
            self.y = 0

    ############## New Movement #################
    def move_direction(self):
        self.y_direction = random.choice([0,1])
        self.x_direction = random.choice([0,1])
        y_distance = random.randrange(1,4)
        x_distance = random.randrange(1,4)
        if self.y_direction == 1:
            # up 
            for i in range(y_distance):
                self.move_y = 1
        elif self.y_direction == 0:
            # down 
            for i in range(y_distance):
                self.move_y = -1
        if self.x_direction == 1:
            # right 
            for i in range(x_distance):
                self.move_x = 1
        elif self.x_direction == 0:
            for i in range(x_distance):
                self.move_x = -1

    def move(self):
        self.move_direction()
        self.x += self.move_x
        self.y += self.move_y
        self.boundary()

        
class snake(organism):
    def __init__(self,boundary_x=800,boundary_y = 800):
        super().__init__(boundary_x,boundary_y)
        self.color = (255,0,0)
        #animal_color('red')
        self.size = 5
        self.boundary_x = boundary_x
        self.boundary_y = boundary_y
        self.energy_counter = random.randrange(750,950)
        self.alive = True
        self.metabolism = 0.5 #ability to metabolize food

    def snake_walk_x(self):
        #### Old 
        long_distiance = random.randrange(0,100)
        if long_distiance <=95:
            movement = random.randrange(-2,3)
        else:
            movement = random.randrange(-24,25)*2
        return movement

    def snake_walk_y(self):
        #### Old 
        long_distiance = random.randrange(0,100)
        if long_distiance <=95:
            movement = random.randrange(-2,3)
        else:
            movement = random.randrange(-24,25)*2
        return movement

    def snake_move_distance(self):
        y_short_distance = random.randrange(1,4)
        x_short_distance = random.randrange(1,4)
        y_long_distance = random.randrange(5,15)
        x_long_distance = random.randrange(5,15)
        long_move_coefficent = random.randrange(0,100)
        if self.energy_counter <=100:
            self.chance_to_move_long = 50
        else:
            self.chance_to_move_long = 10 
        if long_move_coefficent <= self.chance_to_move_long:
            self.y_distance = y_long_distance
            self.x_distance = x_long_distance 
        else:
            self.y_distance = y_short_distance
            self.x_distance = x_short_distance 

    def snake_move_direction(self):
        self.y_direction = random.choice([0,1])
        self.x_direction = random.choice([0,1])
        self.snake_move_distance()
        if self.y_direction == 1:
            # up 
            for i in range(self.y_distance):
                self.move_y = 1
        elif self.y_direction == 0:
            # down 
            for i in range(self.y_distance):
                self.move_y = -1
        if self.x_direction == 1:
            # right 
            for i in range(self.x_distance):
                self.move_x = 1
        elif self.x_direction == 0:
            for i in range(self.x_distance):
                self.move_x = -1

    def snake_move(self):
        if self.alive == True:
            chance_to_move = random.randrange(0,100)
            if chance_to_move <= 50:
                self.snake_move_direction()
            else:
                self.move_x = 0
                self.move_y = 0
            self.x += self.move_x
            self.y += self.move_y
            #print( 'snake x:' + str(self.x) + ' y:' + str(self.y))
            self.boundary()

    def snake_dead(self):
        if self.alive == False:
            self.color = (255,255,255)
            self.move_x = 0
            self.move_y = 0
            #self.x = 0 
            #self.y = 0 
            self.size = 1

    def snake_energy(self,time):
        if self.alive == True:
            if time % 15 == 0:
                self.energy_counter = self.energy_counter - 1
            elif time % 15 != 0:
                self.energy_counter = round(self.energy_counter)
            if self.energy_counter <= 1:
                self.alive = False
                self.snake_dead()
                
    


class kangaroo_rat(organism):
    def __init__(self,boundary_x=800,boundary_y = 800):
        super().__init__(boundary_x,boundary_y)
        self.color = (0,0,255)
        #animal_color('red')
        self.size = 3
        self.boundary_x = boundary_x
        self.boundary_y = boundary_y
        self.energy_counter = random.randrange(190,220)
        self.alive = True
        self.metabolism = .8
    
    def krat_walk_x(self):
        #old
        long_distiance = random.randrange(0,100)
        if long_distiance <=80:
            movement = random.randrange(-2,3)
        else:
            movement = random.randrange(-6,7)*2
        return movement 

    def krat_walk_y(self):
        #old
        long_distiance = random.randrange(0,100)
        if long_distiance <=80:
            movement = random.randrange(-2,3)
        else:
            movement = random.randrange(-6,7)*2
        return movement

    def krat_move_distance(self):
        y_short_distance = random.randrange(1,4)
        x_short_distance = random.randrange(1,4)
        y_long_distance = random.randrange(5,15)
        x_long_distance = random.randrange(5,15)
        long_move_coefficent = random.randrange(0,100)
        if self.energy_counter <=40:
            self.chance_to_move_long = 80
        else:
            self.chance_to_move_long = 10 
        if long_move_coefficent <= self.chance_to_move_long:
            self.y_distance = y_long_distance
            self.x_distance = x_long_distance 
        else:
            self.y_distance = y_short_distance
            self.x_distance = x_short_distance 

    def krat_move_direction(self):
        self.y_direction = random.choice([0,1])
        self.x_direction = random.choice([0,1])
        self.krat_move_distance()
        if self.y_direction == 1:
            # up 
            for i in range(self.y_distance):
                self.move_y = 1
        elif self.y_direction == 0:
            # down 
            for i in range(self.y_distance):
                self.move_y = -1
        if self.x_direction == 1:
            # right 
            for i in range(self.x_distance):
                self.move_x = 1
        elif self.x_direction == 0:
            for i in range(self.x_distance):
                self.move_x = -1

    def krat_move(self):
        if self.alive == True:
            chance_to_move = random.randrange(0,100)
            if chance_to_move <= 80:
                self.krat_move_direction()
            else:
                self.move_x = 0
                self.move_y = 0
            self.x += self.move_x
            self.y += self.move_y
            #print( 'snake x:' + str(self.x) + ' y:' + str(self.y))
            self.boundary()

    def krat_dead(self):
        if self.alive == False:
            self.color = (255,255,255)
            self.move_x = 0
            self.move_y = 0
            #self.x = 0 
            #self.y = 0 
            self.size = 0
            self.energy_counter = 0

    def krat_energy(self,time):
        if self.alive == True:
            if time % 5 == 0:
                self.energy_counter = self.energy_counter - 1
            elif time % 5 != 0:
                self.energy_counter = round(self.energy_counter)
            if self.energy_counter == 1:
                self.alive = False
                self.krat_dead()           

   
class bush:
    def __init__(self,boundary_x=800,boundary_y= 600):
        self.color = (0,255,0)
        self.wid= 15
        self.length = 15
        self.boundary_y = boundary_y
        self.boundary_x = boundary_x
        self.x = random.randrange(0,boundary_x)
        self.y = random.randrange(0,boundary_y)
        self.energy_counter = random.randrange(2000,3000)
        self.alive = True

    def bush_dead(self):
        if self.energy_counter <=0:
            self.alive = False
            self.color = (255,255,255)
            self.move_x = 0
            self.move_y = 0
            #self.x = 0 
            #self.y = 0 
            self.size = 1
            self.energy_counter = 0
        
class grass:
    def __init__(self,boundary_x=800,boundary_y= 600):
        self.color = (0,255,0)
        self.wid= 2
        self.length = 2
        self.boundary_y = boundary_y
        self.boundary_x = boundary_x
        self.x = random.randrange(0,boundary_x)
        self.y = random.randrange(0,boundary_y)
        self.energy_counter = random.randrange(50,60)
        self.alive = True

    def grass_dead(self):
        if self.alive == False:
            self.color = (255,255,255)
            self.move_x = 0
            self.move_y = 0
            #self.x = 0 
            #self.y = 0 
            self.size = 1
            self.energy_counter = 0
if __name__ == "__main__":
   pass
