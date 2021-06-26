#!/usr/bin/python
import unittest
from unittest.mock import patch
import json
import random
import pandas as pd
from uumarrty import organismsim as org
from uumarrty.sim import Sim, Landscape, Cell



class TestOrganismsimScript(unittest.TestCase):
	
	@classmethod
	def setUp(self):
		self.rng = random.Random()
		self.rng.seed(555)
		self.null_sim = Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.csv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.csv',rng=self.rng)
		self.org_movement = Sim(
							initial_conditions_file_path = 'Data/movement_test.txt',
							krat_tsv_output_file_path = 'Data/one_krat_movement.csv',
							snake_tsv_output_file_path = 'Data/no_snake.csv',
							rng = self.rng,
							_output_landscape = True,
							_output_landscape_file_path = 'Data/test_landscape.csv')

	@classmethod	
	def tearDown(self):
		pass

	def test_movement_data(self):
		self.org_movement.main()
		kratdata=pd.read_csv('Data/one_krat_movement.csv',header=None)
		kratdata.columns = ['krat_id', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','snakes_in_cell','owls_in_cell']
		#print(kratdata['cell_id'].head(10))




	###### Tests for movement Algorithm ##########


if __name__ == '__main__':
	unittest.main()
