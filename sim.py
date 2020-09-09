class Cell(object):
	def __init__(self):
		pass

	



	def micro_climate_grid_gen(self):
        ''' This generates a list of (x,y) points that compose the microgrid'''
        for x in range(self.start_x,self.start_x+self.width):
            for y in range(self.start_y,self.start_y+self.micro_height):
                point = [x,y]
                self.micro_grid.append(point)

class Landscape(object):
	pass

class.Sim(object):
	pass

