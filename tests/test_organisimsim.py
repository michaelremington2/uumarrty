#!/usr/bin/python
import unittest
from unittest.mock import patch
import json
from uumarrty import organismsim as org
from uumarrty.sim import Sim, Landscape, Cell



class TestOrganismsimScript(unittest.TestCase):
	
	def setUp(self):
		self.null_sim = sim.Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.tsv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.tsv',rng=None)
		#self.org_bush = org.Organsim
		#self.org_open = None

	def tearDown(self):
		pass

	###### Tests for movement Algorithm ##########


if __name__ == '__main__':
	unittest.main()