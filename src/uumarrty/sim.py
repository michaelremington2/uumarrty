#!/usr/bin/python
from enum import Enum,auto
import random
from json import load
from uumarrty import organismsim as org
from itertools import chain
import time
import csv
import uuid
import os
#look up contact rates based on spatial scale and tempor
#brownian motion 




class Sim(object):
    '''
    loads the initial conditions, initializes the landscape and organism populations, and runs the sim for the appropraite amount of cycles.
    Once the sim concludes two csvs are generated with krat and snake information.
    Args:
        initial_conditions_file_path -- file path for a json file with all the appropriate initial conditions of interest for the simulation.
        rng -- random number generator object. (default is none)
    Attributes:
        snake_info -- an array with info on every snake object per cycle.
        krat_info -- an array with info on every krat object per cycle.
        cycle -- a genral time unit. Starts at zero and the simulation runs until the cycle reaches end time. (int)
        end_time -- the length of the simulation in cycles. (int)
        initial_krat_pop -- the number of krats in the population. This is a constant integer. (int)
        initial_snake_pop -- the number of snake in the population. This is a constant integer. (int)
        krat_reproduction_freq -- the length in cycles until the new generation of krats is formed.
        snake_reproduction_freq -- the length in cycles until the new generation of snakes is formed.
        krat_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for krats. (int)
        snake_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for snakes. (int)
        krat_mutation_probability -- a probabilty less than one that the bush preference of an individual krat offspring accrues a mutation to it's bush preference.
        snake_mutation_probability -- a probabilty less than one that the bush preference of an individual snake offspring accrues a mutation to it's bush preference.

    '''
    def __init__(self,initial_conditions_file_path, krat_csv_output_file_path, snake_csv_output_file_path, parameters_csv_output_file_path, rng=None,seed=None,burn_in = None,_output_landscape=False,_output_landscape_file_path=None,sim_info_output_file=None):
        self.sim_id = uuid.uuid4().hex
        self.initial_conditions_file_path = initial_conditions_file_path
        #self.snake_info = []
        #self.krat_info = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.krat_file_path = krat_csv_output_file_path
        self.snake_file_path = snake_csv_output_file_path
        self.sim_parameters_and_totals = parameters_csv_output_file_path
        self.cycle = 0
        self.krat_generation = 0
        self.snake_generation = 0
        if seed is not None:
            self.seed = seed
            self.rng.seed(seed)
        if burn_in is not None:
            self.burn_in = burn_in       
        else:
            self.burn_in = 0
        if sim_info_output_file is not None:
            self.sim_info_output_file = sim_info_output_file
        self._output_landscape = _output_landscape
        self._output_landscape_file_path = _output_landscape_file_path
        

    def genotype_freq_test(self,genotype_freq_dict):
        if sum(genotype_freq_dict.values()) != 1:
            raise Exception("Genotype frequencies do not sum to 1.")

    def exception_bool_values(self, mixed_preference, prey_competition):
        test_vals = {'mixed_preference': mixed_preference,
                    'prey_competition' : prey_competition}
        for key, val in test_vals.items():
            if not type(val) is bool:
                raise TypeError("{} check should be a boolean (True or False).".format(key))

    def exception_int_values(
                        self, end_time, initial_krat_pop, initial_snake_pop,
                        krat_reproduction_freq, snake_reproduction_freq, energy_gain_per_krat,
                        snake_energy_cost, snake_move_range, snake_movement_frequency,
                        krat_move_range, krat_movement_frequency, krat_energy_gain_bush,
                        krat_energy_gain_open, krat_energy_cost, owl_move_range,
                        landscape_size_x, landscape_size_y, initial_owl_pop
                        ):
        test_vals = {'end_time': end_time,
                    'initial_krat_pop' : initial_krat_pop,
                    'initial_snake_pop' : initial_snake_pop,
                    'krat_reproduction_freq' : krat_reproduction_freq,
                    'snake_reproduction_freq' : snake_reproduction_freq,
                    'energy_gain_per_krat' : energy_gain_per_krat,
                    'snake_energy_cost' : snake_energy_cost,
                    'snake_movement_frequency' : snake_movement_frequency,
                    'krat_move_range' : krat_move_range,
                    'krat_movement_frequency' : krat_movement_frequency,
                    'krat_energy_gain_bush' : krat_energy_gain_bush,
                    'krat_energy_gain_open' : krat_energy_gain_open,
                    'krat_energy_cost' : krat_energy_cost,
                    'landscape_size_x' : landscape_size_x,
                    'landscape_size_y' : landscape_size_y,
                    'initial_owl_pop' : initial_owl_pop,
                    'owl_move_range' : owl_move_range}
        for key, val in test_vals.items():
            if not type(val) is int:
                raise TypeError("{} value should be an integer".format(key))

    def exception_float_or_int_values(
                        self, krat_mutation_std, snake_mutation_std,
                        krat_mutation_probability, snake_mutation_probability, snake_strike_success_probability_bush,
                        strike_success_probability_open, snake_death_probability,  owl_strike_success_probability 
                        ):
        test_vals = {'krat_mutation_std': krat_mutation_std,
                    'snake_mutation_std' : snake_mutation_std,
                    'krat_mutation_probability' : krat_mutation_probability,
                    'snake_mutation_probability' : snake_mutation_probability,
                    'snake_strike_success_probability_bush' : snake_strike_success_probability_bush,
                    'strike_success_probability_open' : strike_success_probability_open,
                    'snake_death_probability' : snake_death_probability,
                    'owl_strike_success_probability ' : owl_strike_success_probability}
        for key, val in test_vals.items():
            if type(val) not in [int,float]:
                raise TypeError("{} value should be a number".format(key))
            if 0 > val > 1:
                raise Exception("{} value should be between 0 and 1".format(key))

    def run_config_checks(self,config_d):
        self.exception_bool_values(mixed_preference=config_d["mixed_preference_individuals"], prey_competition=config_d["prey_competition"])
        self.exception_int_values(
                        end_time = config_d["cycles_of_sim"], initial_krat_pop=config_d["initial_krat_pop"], initial_snake_pop=config_d["initial_snake_pop"],
                        krat_reproduction_freq=config_d["krat_reproduction_freq_per_x_cycles"], snake_reproduction_freq=config_d["snake_reproduction_freq_per_x_cycles"], energy_gain_per_krat=config_d["snake_energy_gain"],
                        snake_energy_cost=config_d["snake_energy_cost"], snake_move_range=config_d["snake_move_range"], snake_movement_frequency=config_d["snake_movement_frequency_per_x_cycles"],
                        krat_move_range=config_d["krat_move_range"], krat_movement_frequency=config_d["krat_movement_frequency_per_x_cycles"], krat_energy_gain_bush=config_d["krat_energy_gain_bush"],
                        krat_energy_gain_open=config_d["krat_energy_gain_open"], krat_energy_cost=config_d["krat_energy_cost"], owl_move_range=config_d["owl_move_range"],
                        landscape_size_x=config_d["landscape_size_x"], landscape_size_y=config_d["landscape_size_y"], initial_owl_pop=config_d["initial_owl_pop"]
                        )
        self.exception_float_or_int_values(
                        krat_mutation_std=config_d["krat_mutation_std"], snake_mutation_std=config_d["snake_mutation_std"],
                        krat_mutation_probability=config_d["krat_mutation_probability"], snake_mutation_probability=config_d["snake_mutation_probability"], snake_strike_success_probability_bush=config_d["snake_strike_success_probability_bush"],
                        strike_success_probability_open=config_d["snake_strike_success_probability_open"], snake_death_probability=config_d["snake_death_probability"],  owl_strike_success_probability=config_d["owl_catch_success"]
                        )

    def config_sim_species_attributes_and_sim_paramaters(self,config_d):
        self.mixed_individuals = config_d["mixed_preference_individuals"]
        self.prey_competition = config_d["prey_competition"]
        self.end_time = config_d["cycles_of_sim"]
        self.initial_krat_pop = config_d["initial_krat_pop"]
        self.initial_snake_pop = config_d["initial_snake_pop"]
        self.krat_reproduction_freq = config_d["krat_reproduction_freq_per_x_cycles"]
        self.snake_reproduction_freq = config_d["snake_reproduction_freq_per_x_cycles"]
        self.krat_mutation_std = config_d["krat_mutation_std"]
        self.snake_mutation_std = config_d["snake_mutation_std"]
        self.krat_mutation_probability = config_d["krat_mutation_probability"]
        self.snake_mutation_probability = config_d["snake_mutation_probability"]
        self.data_sample_frequency = config_d["data_sample_freq"]


    def initialize_snake_pop(self,config_d):
        if self.mixed_individuals:
            self.landscape.initialize_snake_pop_continuous_preference(
                strike_success_probability_bush = config_d["snake_strike_success_probability_bush"],
                strike_success_probability_open = config_d["snake_strike_success_probability_open"],
                death_probability = config_d["snake_death_probability"],
                energy_gain_per_krat = config_d["snake_energy_gain"],
                energy_cost = config_d["snake_energy_cost"],
                move_range = config_d["snake_move_range"],
                movement_frequency = config_d["snake_movement_frequency_per_x_cycles"],
            )
        else:
            snake_genotype_frequencies = {1:(1/2), 0:(1/2)}
            self.landscape.initialize_snake_pop_discrete_preference(
                strike_success_probability_bush = config_d["snake_strike_success_probability_bush"],
                strike_success_probability_open = config_d["snake_strike_success_probability_open"],
                death_probability = config_d["snake_death_probability"],
                energy_gain_per_krat = config_d["snake_energy_gain"],
                energy_cost = config_d["snake_energy_cost"],
                move_range = config_d["snake_move_range"],
                movement_frequency = config_d["snake_movement_frequency_per_x_cycles"],
                snake_genotype_frequencies = snake_genotype_frequencies
            )

    def initialize_krat_pop(self,config_d):
        if self.mixed_individuals:
                self.landscape.initialize_krat_pop_continuous_preference(
                move_range = config_d["krat_move_range"],
                movement_frequency = config_d["krat_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["krat_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["krat_energy_gain_open"], #from bouskila
                energy_cost=config_d["krat_energy_cost"],
                )
        else:
            krat_genotype_frequencies = {1:(1/2), 0:(1/2)}
            self.landscape.initialize_krat_pop_discrete_preference(
                move_range = config_d["krat_move_range"],
                movement_frequency = config_d["krat_movement_frequency_per_x_cycles"],
                energy_gain_bush=config_d["krat_energy_gain_bush"], #from bouskila
                energy_gain_open=config_d["krat_energy_gain_open"], #from bouskila
                energy_cost=config_d["krat_energy_cost"],
                krat_genotype_frequencies = krat_genotype_frequencies
                )

    def configure(self, config_d):
        self.config_sim_species_attributes_and_sim_paramaters(config_d = config_d)
        self.landscape = Landscape(
                sim=self,
                size_x=config_d["landscape_size_x"],
                size_y=config_d["landscape_size_y"],
                microhabitat_open_bush_proportions = config_d["microhabitat_open_bush_proportions"],
                _output_landscape = self._output_landscape,
                _output_landscape_file_path = self._output_landscape_file_path
                )
        self.landscape.build()
        self.initialize_snake_pop(config_d = config_d)
        self.initialize_krat_pop(config_d = config_d)
        self.landscape.initialize_owl_pop(
                initial_owl_pop=config_d["initial_owl_pop"],
                move_range = config_d["owl_move_range"],
                strike_success_probability = config_d["owl_catch_success"],
                open_preference_weight = 1,
                bush_preference_weight = 0
                )

    def read_configuration_file(self):
        with open(self.initial_conditions_file_path) as f:
            self.config_d = load(f)
        self.run_config_checks(config_d = self.config_d)
        self.configure(self.config_d)

    def test(self):
        self.read_configuration_file()
        cells = self.landscape.cells
        for cell_width in cells:
            for cell in cell_width:
                cell_id = '{},{}'.format(cell.cell_id[0],cell.cell_id[1])
                print(cell_id)
        

    def make_csv(self,file_name):
        with open(file_name, 'w', newline='\n') as file:
            pass

    def append_data(self,file_name,data_row):
        with open(file_name, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(data_row)

    def sim_info(self, line):
        if self.sim_info_output_file is not None:
            with open(self.sim_info_output_file, 'a') as file:
                file.write(line)

    def sim_initial_conditions(self, config_d):
        data_row = []
        start_local_time = time.localtime()
        start_day= '{}/{}/{}'.format(start_local_time.tm_year,
                                            start_local_time.tm_mon, 
                                            start_local_time.tm_mday)
        start_time='{}:{}:{}'.format(start_local_time.tm_hour,
                                     start_local_time.tm_min,
                                     start_local_time.tm_sec)

        if os.path.isfile(self.sim_parameters_and_totals):
            data_row.append(self.sim_id)
            data_row.append(self.seed)
            data_row.append(start_day)
            data_row.append(start_time)
            for keys, vals in config_d.items():
                data_row.append(vals)
            self.append_data(file_name = self.sim_parameters_and_totals, data_row = data_row)
        else:
            self.make_csv(file_name = self.sim_parameters_and_totals) 
            data_row.append("sim_id")
            data_row.append("seed")
            data_row.append("start_day")
            data_row.append("start_time")
            for keys, vals in config_d.items():
                data_row.append(keys)
            self.append_data(file_name = self.sim_parameters_and_totals, data_row = data_row)
            data_row = []
            data_row.append(self.sim_id)
            data_row.append(self.seed)
            data_row.append(start_day)
            data_row.append(start_time)
            for keys, vals in config_d.items():
                data_row.append(vals)
            self.append_data(file_name = self.sim_parameters_and_totals, data_row = data_row)

    def main(self):
        start = round(time.time())
        start_local_time = time.localtime()
        start_info = 'Sim start time {}:{} {}/{}/{}, Data config {}\n'.format(start_local_time.tm_hour,
                                                                               start_local_time.tm_min,
                                                                               start_local_time.tm_year,
                                                                               start_local_time.tm_mon, 
                                                                               start_local_time.tm_mday, 
                                                                               self.initial_conditions_file_path)
        data_info ='{}, {} \n'.format(self.krat_file_path,self.snake_file_path )
        self.sim_info(line = data_info)
        self.sim_info(line = start_info)
        self.make_csv(file_name = self.krat_file_path )
        self.make_csv(file_name = self.snake_file_path )
        self.read_configuration_file()
        self.sim_initial_conditions(self.config_d)
        for i in range(0,self.end_time,1):
            self.landscape.landscape_dynamics()
            self.cycle += 1
        time_elapsed = round(time.time()) - start
        end_local_time = time.localtime()
        end_info = 'Sim end time {}:{} {}/{}/{}, time elapsed {}\n'.format(end_local_time.tm_hour,
                                                                           end_local_time.tm_min,
                                                                           end_local_time.tm_year,
                                                                           end_local_time.tm_mon, 
                                                                           end_local_time.tm_mday,
                                                                           time_elapsed)
        self.sim_info(line = end_info)



if __name__ ==  "__main__":
    pass
    #sim = Sim(initial_conditions_file_path = 'data.txt', krat_tsv_output_file_path = 'krat_energy.tsv', snake_tsv_output_file_path = 'snake_energy.tsv')
    #sim.main()
    #print('test')



