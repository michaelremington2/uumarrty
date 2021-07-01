#!/usr/bin/python
import unittest
from unittest.mock import patch
import json
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
        with open(self.data_file) as f:
            self.config_d = json.load(f)
        self.null_sim = Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.tsv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.tsv',rng=None)
        self.blank_cell_prey_true = Cell(sim = self.null_sim, habitat_type=Landscape.MicrohabitatType.BUSH, cell_id=(0,0),prey_competition=True)
        self.blank_cell_prey_false = Cell(sim = self.null_sim, habitat_type=Landscape.MicrohabitatType.OPEN, cell_id=(0,0),prey_competition=False)


    def tearDown(self):
        print('Tearing Down Cell Tests')

    def _add_krat_to_cell(self):
        krat = org.Krat(sim = self.null_sim,
                        energy_gain_bush = 10, #from bouskila
                        energy_gain_open = 10, #from bouskila
                        energy_cost = 5,
                        move_range = 1,
                        movement_frequency = 1,
                        home_cell = self.blank_cell_prey_true,
                        open_preference_weight = 1,
                        bush_preference_weight = 0)
        cell.add_krat(krat)

if __name__ == '__main__':
    unittest.main()