import unittest
from unittest.mock import patch
import json
from xomar import organismsim as org
from xomar.sim import Sim

class TestSimConfig(unittest.TestCase):
    
    @classmethod
    def setUp(self):
        print('setup and initalizing null sim')
        self.data_file = 'Data/null_exp.txt'
        with open(self.data_file) as f:
            self.config_d = json.load(f)
        #self.null_sim = Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.tsv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.tsv',rng=None)

    @classmethod
    def tearDown(self):
        print('Tearing Down')

    def test_exception_bool_values(self):
        with self.assertRaises(TypeError):
            Sim.exception_bool_values(mixed_preference=self.config_d["mixed_preference_individuals"], prey_competition=self.config_d["prey_competition"])

    def test_exception_int_values(self):
        with self.assertRaises(TypeError):
            Sim.exception_int_values(
                        end_time = self.config_d["cycles_of_sim"], initial_krat_pop=self.config_d["initial_krat_pop"], initial_snake_pop=self.config_d["initial_snake_pop"],
                        krat_reproduction_freq=self.config_d["krat_reproduction_freq_per_x_cycles"], snake_reproduction_freq=self.config_d["snake_reproduction_freq_per_x_cycles"], energy_gain_per_krat=self.config_d["snake_energy_gain"],
                        snake_energy_cost=self.config_d["snake_energy_cost"], snake_move_range=self.config_d["snake_move_range"], snake_movement_frequency=self.config_d["snake_movement_frequency_per_x_cycles"],
                        krat_move_range=self.config_d["krat_move_range"], krat_movement_frequency=self.config_d["krat_movement_frequency_per_x_cycles"], krat_energy_gain_bush=self.config_d["krat_energy_gain_bush"],
                        krat_energy_gain_open=self.config_d["krat_energy_gain_open"], krat_energy_cost=self.config_d["krat_energy_cost"], owl_move_range=self.config_d["owl_move_range"],
                        landscape_size_x=self.config_d["landscape_size_x"], landscape_size_y=self.config_d["landscape_size_y"], initial_owl_pop=self.config_d["initial_owl_pop"]
                        )

    def test_exception_float_or_int_values(self):
        with self.assertRaises(TypeError):
            Sim.exception_float_or_int_values(
                        krat_mutation_std=self.config_d["krat_mutation_std"], snake_mutation_std=self.config_d["snake_mutation_std"],
                        krat_mutation_probability=self.config_d["krat_mutation_probability"], snake_mutation_probability=self.config_d["snake_mutation_probability"], snake_strike_success_probability_bush=self.config_d["snake_strike_success_probability_bush"],
                        strike_success_probability_open=self.config_d["snake_strike_success_probability_open"], snake_death_probability=self.config_d["snake_death_probability"],  owl_strike_success_probability=self.config_d["owl_catch_success"]
                        )



if __name__ == '__main__':
    unittest.main()