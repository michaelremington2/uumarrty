import random
import pygame
class organism:
    def __init__(self,color,size,boundary_x=800,boundary_y= 600):
        self.color = color
        self.size = size
        self.boundary_y = boundary_y
        self.boundary_x = boundary_x
        self.x = random.randrange(0,boundary_x)
        self.y = random.randrange(0,boundary_y)
    
    def animal_color(color_name):
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

    def move(self):
        self.move_x = random.randrange(-1,2)
        self.move_y = random.randrange(-1,2)
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
        self.energy_counter = 1000
        self.alive = True

    def snake_walk_x(self):
        chance_to_move = random.randrange(0,100)
        long_distiance = random.randrange(0,100)
        if long_distiance <=95:
            if chance_to_move < 25:
                movement = random.randrange(1,3)
            elif chance_to_move >=25 and chance_to_move < 50:
                movement = random.randrange(-2,-1)
            elif chance_to_move >= 50:
                movement = 0
            return movement
        else:
            if chance_to_move < 50:
                movement = random.randrange(4,7)
            elif chance_to_move >=50:
                movement = random.randrange(-6,-4)
            return movement*2 

    def snake_walk_y(self):
        chance_to_move = random.randrange(0,100)
        long_distiance = random.randrange(0,100)
        if long_distiance <=95:
            if chance_to_move < 25:
                movement = random.randrange(1,3)
            elif chance_to_move >=25 and chance_to_move < 50:
                movement = random.randrange(-2,-1)
            elif chance_to_move >= 50:
                movement = 0
            return movement
        else:
            if chance_to_move < 50:
                movement = random.randrange(4,7)
            elif chance_to_move >=50:
                movement = random.randrange(-6,-4)
            return movement*2 


    def snake_move(self):
        self.move_x = self.snake_walk_x()
        self.move_y = self.snake_walk_y()
        self.x += self.move_x
        self.y += self.move_y
        self.boundary()
    
    def snake_energy(self,n):
        if n % 13 == 0:
            self.energy_counter = self.energy_counter - 5
        print('Snake Energy Level:' + str(self.energy_counter))


class kangaroo_rat(organism):
    def __init__(self,boundary_x=800,boundary_y = 800):
        super().__init__(boundary_x,boundary_y)
        self.color = (0,0,255)
        #animal_color('red')
        self.size = 3
        self.boundary_x = boundary_x
        self.boundary_y = boundary_y
        self.initial_energy_counter = 200
        self.alive = True
    
    def krat_move(self):
        self.move_x = random.randrange(-2,3)
        self.move_y = random.randrange(-2,3)
        self.x += self.move_x
        self.y += self.move_y
        self.boundary()

class bush:
    def __init__(self,boundary_x=800,boundary_y= 600):
        self.color = (0,255,0)
        self.wid= 15
        self.length = 15
        self.boundary_y = boundary_y
        self.boundary_x = boundary_x
        self.x = random.randrange(0,boundary_x)
        self.y = random.randrange(0,boundary_y)
        self.energy = random.randrange(2000,3000)
        self.alive = True
class grass:
    def __init__(self,boundary_x=800,boundary_y= 600):
        self.color = (0,255,0)
        self.wid= 2
        self.length = 2
        self.boundary_y = boundary_y
        self.boundary_x = boundary_x
        self.x = random.randrange(0,boundary_x)
        self.y = random.randrange(0,boundary_y)
        self.energy = random.randrange(50,60)
        self.alive = True

if __name__ == "__main__":
    pass

