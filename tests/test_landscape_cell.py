#!/usr/bin/python
import unittest
from unittest.mock import patch
import json
import random
from uumarrty import organismsim as org
from uumarrty.sim import Sim, Landscape, Cell

#fixed number seed
#hand check results
# Test movement of a rat
#Test for a uniform distribution with error
# Fix microhabitat preference at a given run
# Set up artificial conditions

class TestCell_and_Landscape(unittest.TestCase):

    def setUp(self):
        print('setup and initalizing cell object')
        self.data_file = 'Data/null_exp.txt'
        self.rng = random.Random()
        self.rng.seed(555)
        self.null_sim = Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.csv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.csv',rng=self.rng)
        self.null_sim.read_configuration_file()
        self.cells = []
        for y in self.null_sim.landscape.cells:
            for x in y:
                self.cells.append(x)


    def tearDown(self):
        print('Tearing Down Cell Tests')

    def test_landscape_size(self):
        self.assertEqual(len(self.cells),4)

    def test_add_krat_to_cell(self):
        cell = self.cells[0]
        krat_1 = org.Krat(sim = self.null_sim,
                        energy_gain_bush = 10, 
                        energy_gain_open = 10, 
                        energy_cost = 5,
                        move_range = 1,
                        movement_frequency = 1,
                        home_cell = (0,0),
                        open_preference_weight = 1,
                        bush_preference_weight = 0)

        krat_2 = org.Krat(sim = self.null_sim,
                        energy_gain_bush = 10, 
                        energy_gain_open = 10, 
                        energy_cost = 5,
                        move_range = 1,
                        movement_frequency = 1,
                        home_cell = (0,0),
                        open_preference_weight = 1,
                        bush_preference_weight = 0)
        krat_3 = org.Krat(sim = self.null_sim,
                        energy_gain_bush = 10, 
                        energy_gain_open = 10, 
                        energy_cost = 5,
                        move_range = 1,
                        movement_frequency = 1,
                        home_cell = (0,0),
                        open_preference_weight = 1,
                        bush_preference_weight = 0)
        cell.add_krat(krat_1)
        cell.add_krat(krat_2)
        cell.add_krat(krat_3)
        self.assertEqual(len(cell.krats),3)

    def test_add_snake_to_cell(self):
        cell = self.cells[0]
        snake_1 = org.Snake(sim = self.null_sim,
                        strike_success_probability_bush = 0.21,
                        strike_success_probability_open = 0.21,
                        death_probability = 0,
                        energy_gain_per_krat = 1500,
                        energy_cost = 10,
                        move_range = 1,
                        movement_frequency = 1,
                        open_preference_weight = 1,
                        bush_preference_weight = 0
                            )

        snake_2 = org.Snake(sim = self.null_sim,
                        strike_success_probability_bush = 0.21,
                        strike_success_probability_open = 0.21,
                        death_probability = 0,
                        energy_gain_per_krat = 1500,
                        energy_cost = 10,
                        move_range = 1,
                        movement_frequency = 1,
                        open_preference_weight = 0,
                        bush_preference_weight = 1
                            )
        cell.add_snake(snake_1)
        cell.add_snake(snake_2)
        self.assertEqual(len(cell.snakes),2)


if __name__ == '__main__':
    unittest.main()