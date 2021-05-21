import unittest
from unittest.mock import patch
from xomar import organismsim as org
from xomar import sim

class TestSimConfig(unittest.TestCase):
	
	@classmethod
	def setUp(self):
		print('setup and initalizing null sim')
		self.data_file = 'Data/null_exp.txt'
		self.null_sim = sim.Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.tsv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.tsv',rng=None)
		#self.org_bush = org.Organsim
		#self.org_open = None

	def tearDown(self):
		pass

	###### Tests for movement Algorithm ##########


if __name__ == '__main__':
	unittest.main()