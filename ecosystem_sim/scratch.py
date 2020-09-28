cell = (3,0)
for x in [-1,0,1]:
            for y in [-1,0,1]:
            	x_coord = cell[0]+x
            	y_coord = cell[1]+y
            	if x_coord >= 0 and x_coord <= 9 and y_coord >= 0 and y_coord <= 7:
            		print('{},{}'.format(x_coord,y_coord))
