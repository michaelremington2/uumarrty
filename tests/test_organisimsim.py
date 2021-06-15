#!/usr/bin/python
import unittest
from unittest.mock import patch
import json
import random
import pandas as pd
from uumarrty import organismsim as org
from uumarrty.sim import Sim, Landscape, Cell



class TestOrganismsimScript(unittest.TestCase):
	
	def setUp(self):
		self.rng = random.Random()
		self.rng.seed(555)
		self.null_sim = Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.csv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.csv',rng=self.rng)
		self.org_bush = Sim(initial_conditions_file_path = 'Data/movement_test.txt', krat_tsv_output_file_path = 'Data/one_krat_movement.csv', snake_tsv_output_file_path = 'Data/no_snake.csv',rng=self.rng)

	def tearDown(self):
		pass

	def test_movement_data(self):
		self.org_bush.main()
		kratdata=pd.read_csv('Data/one_krat_movement.csv',header=None)
		kratdata.columns = ['krat_id', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','snakes_in_cell','owls_in_cell']
		print(len(kratdata))




	###### Tests for movement Algorithm ##########


if __name__ == '__main__':
	unittest.main()
