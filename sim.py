class microclimate:
	def __init__(self,micro_id,width,height, top_left_corner_point = (0,0)):
		self.micro_id = micro_id
		self.width = width
		self.height = hieght
		self.start_point = top_left_corner_point
		self.start_x = self.start_point[0]
		self.start_y = self.start_point[1]
		self.microclimate_type =  random.choice(['open','bush'])
		self.micro_grid = []


	def micro_climate_grid_gen(self):
        ''' This generates a list of (x,y) points that compose the microgrid'''
        for x in range(self.start_x,self.start_x+self.width):
            for y in range(self.start_y,self.start_y+self.micro_height):
                point = [x,y]
                self.micro_grid.append(point)
class climate:
	pass

class.sim:
	pass

