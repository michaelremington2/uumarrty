#!/usr/bin/python
import random
from json import load
from uumarrty import organismsim as org
from uumarrty import environment as env
import time
import csv
import uuid
#look up contact rates based on spatial scale and tempor
#brownian motion 
class Sim(object):
    '''
    loads the initial conditions, initializes the landscape and organism populations, and runs the sim for the appropraite amount of cycles.
    Once the sim concludes two csvs are generated with prey and predator information.
    Args:
        initial_conditions_file_path -- file path for a json file with all the appropriate initial conditions of interest for the simulation.
        rng -- random number generator object. (default is none)
    Attributes:
        predator_info -- an array with info on every predator object per cycle.
        prey_info -- an array with info on every prey object per cycle.
        cycle -- a genral time unit. Starts at zero and the simulation runs until the cycle reaches end time. (int)
        end_time -- the length of the simulation in cycles. (int)
        initial_prey_pop -- the number of preys in the population. This is a constant integer. (int)
        initial_predator_pop -- the number of predator in the population. This is a constant integer. (int)
        prey_reproduction_freq -- the length in cycles until the new generation of preys is formed.
        predator_reproduction_freq -- the length in cycles until the new generation of predators is formed.
        prey_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for preys. (int)
        predator_mutation_std -- the standard deviation of the population used to calculate the mutation quantity that the bush preference is changed by if the mutation probabilty is successfully met for predators. (int)
        prey_mutation_probability -- a probabilty less than one that the bush preference of an individual prey offspring accrues a mutation to it's bush preference.
        predator_mutation_probability -- a probabilty less than one that the bush preference of an individual predator offspring accrues a mutation to it's bush preference.

    '''
    def __init__(self,initial_conditions_file_path, prey_csv_output_file_path, predator_csv_output_file_path, parameters_csv_output_file_path, rng=None,seed=None,burn_in = None,_output_landscape=False,_output_landscape_file_path=None,sim_info_output_file=None):
        self.sim_id = uuid.uuid4().hex
        self.initial_conditions_file_path = initial_conditions_file_path
        #self.predator_info = []
        #self.prey_info = []
        if rng is None:
            self.rng = random.Random()
        else:
            self.rng = rng
        self.prey_file_path = prey_csv_output_file_path
        self.predator_file_path = predator_csv_output_file_path
        self.sim_parameters_and_totals = parameters_csv_output_file_path
        self.cycle = 0
        self.prey_generation = {}
        self.predator_generation = {}
        self.predator_population_parameters = {}
        if seed is not None:
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
                        self, end_time, initial_prey_pop, initial_predator_pop,
                        prey_reproduction_freq, predator_reproduction_freq, energy_gain_per_prey,
                        predator_energy_cost, predator_move_range, predator_movement_frequency,
                        prey_move_range, prey_movement_frequency, prey_energy_gain_bush,
                        prey_energy_gain_open, prey_energy_cost, owl_move_range,
                        landscape_size_x, landscape_size_y, initial_owl_pop
                        ):
        test_vals = {'end_time': end_time,
                    'initial_prey_pop' : initial_prey_pop,
                    'initial_predator_pop' : initial_predator_pop,
                    'prey_reproduction_freq' : prey_reproduction_freq,
                    'predator_reproduction_freq' : predator_reproduction_freq,
                    'energy_gain_per_prey' : energy_gain_per_prey,
                    'predator_energy_cost' : predator_energy_cost,
                    'predator_movement_frequency' : predator_movement_frequency,
                    'prey_move_range' : prey_move_range,
                    'prey_movement_frequency' : prey_movement_frequency,
                    'prey_energy_gain_bush' : prey_energy_gain_bush,
                    'prey_energy_gain_open' : prey_energy_gain_open,
                    'prey_energy_cost' : prey_energy_cost,
                    'landscape_size_x' : landscape_size_x,
                    'landscape_size_y' : landscape_size_y,
                    'initial_owl_pop' : initial_owl_pop,
                    'owl_move_range' : owl_move_range}
        for key, val in test_vals.items():
            if not type(val) is int:
                raise TypeError("{} value should be an integer".format(key))

    def exception_float_or_int_values(
                        self, prey_mutation_std, predator_mutation_std,
                        prey_mutation_probability, predator_mutation_probability, predator_strike_success_probability_bush,
                        strike_success_probability_open, predator_death_probability,  owl_strike_success_probability 
                        ):
        test_vals = {'prey_mutation_std': prey_mutation_std,
                    'predator_mutation_std' : predator_mutation_std,
                    'prey_mutation_probability' : prey_mutation_probability,
                    'predator_mutation_probability' : predator_mutation_probability,
                    'predator_strike_success_probability_bush' : predator_strike_success_probability_bush,
                    'strike_success_probability_open' : strike_success_probability_open,
                    'predator_death_probability' : predator_death_probability,
                    'owl_strike_success_probability ' : owl_strike_success_probability}
        for key, val in test_vals.items():
            if type(val) not in [int,float]:
                raise TypeError("{} value should be a number".format(key))
            if 0 > val > 1:
                raise Exception("{} value should be between 0 and 1".format(key))

    def run_config_checks(self,config_d):
        self.exception_bool_values(mixed_preference=config_d["mixed_preference_individuals"], prey_competition=config_d["prey_competition"])
        self.exception_int_values(
                        end_time = config_d["cycles_of_sim"], initial_prey_pop=config_d["initial_prey_pop"], initial_predator_pop=config_d["initial_predator_pop"],
                        prey_reproduction_freq=config_d["prey_reproduction_freq_per_x_cycles"], predator_reproduction_freq=config_d["predator_reproduction_freq_per_x_cycles"], energy_gain_per_prey=config_d["predator_energy_gain"],
                        predator_energy_cost=config_d["predator_energy_cost"], predator_move_range=config_d["predator_move_range"], predator_movement_frequency=config_d["predator_movement_frequency_per_x_cycles"],
                        prey_move_range=config_d["prey_move_range"], prey_movement_frequency=config_d["prey_movement_frequency_per_x_cycles"], prey_energy_gain_bush=config_d["prey_energy_gain_bush"],
                        prey_energy_gain_open=config_d["prey_energy_gain_open"], prey_energy_cost=config_d["prey_energy_cost"], owl_move_range=config_d["owl_move_range"],
                        landscape_size_x=config_d["landscape_size_x"], landscape_size_y=config_d["landscape_size_y"], initial_owl_pop=config_d["initial_owl_pop"]
                        )
        self.exception_float_or_int_values(
                        prey_mutation_std=config_d["prey_mutation_std"], predator_mutation_std=config_d["predator_mutation_std"],
                        prey_mutation_probability=config_d["prey_mutation_probability"], predator_mutation_probability=config_d["predator_mutation_probability"], predator_strike_success_probability_bush=config_d["predator_strike_success_probability_bush"],
                        strike_success_probability_open=config_d["predator_strike_success_probability_open"], predator_death_probability=config_d["predator_death_probability"],  owl_strike_success_probability=config_d["owl_catch_success"]
                        )

    def config_sim_species_attributes_and_sim_paramaters(self,config_d):
        self.sim_parameters = config_d['sim']
        self.landscape_parameters = config_d['landscape']
        self.prey_parameters = config_d['prey']
        self.predator_parameters = config_d['predator']
        self.mixed_individuals = self.sim_parameters["mixed_preference_individuals"]
        self.prey_competition = self.sim_parameters["prey_competition"]
        self.end_time = self.sim_parameters["cycles_of_sim"]
        self.data_sample_frequency = sim_config_d["data_sample_freq"]
        #for 
        # self.initial_prey_pop = config_d["initial_prey_pop"]
        # self.initial_predator_pop = config_d["initial_predator_pop"]
        # self.prey_reproduction_freq = config_d["prey_reproduction_freq_per_x_cycles"]
        # self.predator_reproduction_freq = config_d["predator_reproduction_freq_per_x_cycles"]
        # self.prey_mutation_std = config_d["prey_mutation_std"]
        # self.predator_mutation_std = config_d["predator_mutation_std"]
        # self.prey_mutation_probability = config_d["prey_mutation_probability"]
        # self.predator_mutation_probability = config_d["predator_mutation_probability"]


    def initialize_predator_pop(self,predator_config_d):
        for predator_label, pred_pm in self.predator_parameters:
            if self.mixed_individuals:
                self.landscape.initialize_predator_pop_continuous_preference(
                    organism_label = predator_label,
                    strike_success_probability_bush = pred_pm["strike_success_probability_bush"],
                    strike_success_probability_open = pred_pm["strike_success_probability_open"],
                    death_probability = pred_pm["death_probability"],
                    energy_gain_per_prey = pred_pm["energy_gain"],
                    energy_cost = pred_pm["energy_cost"],
                    move_range = pred_pm["move_range"],
                    movement_frequency = pred_pm["movement_frequency_per_x_cycles"],
                )
            else:
                predator_genotype_frequencies = {1:(1/2), 0:(1/2)}
                self.landscape.initialize_predator_pop_discrete_preference(
                    organism_label = predator_label,
                    strike_success_probability_bush = pred_pm["strike_success_probability_bush"],
                    strike_success_probability_open = pred_pm["strike_success_probability_open"],
                    death_probability = pred_pm["death_probability"],
                    energy_gain_per_prey = pred_pm["energy_gain"],
                    energy_cost = pred_pm["energy_cost"],
                    move_range = pred_pm["move_range"],
                    movement_frequency = pred_pm["movement_frequency_per_x_cycles"],
                    predator_genotype_frequencies = predator_genotype_frequencies
                )

    def initialize_prey_pop(self,prey_config_d):
        for prey_label, prey_pm in self.prey_parameters:
            if self.mixed_individuals:
                    self.landscape.initialize_prey_pop_continuous_preference(
                    organism_label = prey_label,
                    movement_frequency = prey_pm["prey_movement_frequency_per_x_cycles"],
                    energy_gain_bush=prey_pm["prey_energy_gain_bush"], #from bouskila
                    energy_gain_open=prey_pm["prey_energy_gain_open"], #from bouskila
                    energy_cost=prey_pm["prey_energy_cost"],
                    )
            else:
                prey_genotype_frequencies = {1:(1/2), 0:(1/2)}
                self.landscape.initialize_prey_pop_discrete_preference(
                    organism_label = prey_label,
                    movement_frequency = prey_pm["prey_movement_frequency_per_x_cycles"],
                    energy_gain_bush=prey_pm["prey_energy_gain_bush"], #from bouskila
                    energy_gain_open=prey_pm["prey_energy_gain_open"], #from bouskila
                    energy_cost=prey_pm["prey_energy_cost"],
                    prey_genotype_frequencies = prey_genotype_frequencies
                    )

    def configure(self, config_d):
        self.config_sim_species_attributes_and_sim_paramaters(sim_config_d = config_d['sim'])
        self.landscape = env.Landscape(
                sim=self,
                size_x=self.landscape_parameters["landscape_size_x"],
                size_y=self.landscape_parameters["landscape_size_y"],
                microhabitat_open_bush_proportions = self.landscape_parameters["microhabitat_open_bush_proportions"],
                _output_landscape = self._output_landscape,
                _output_landscape_file_path = self._output_landscape_file_path
                )
        self.landscape.build()
        self.initialize_predator_pop(config_d = config_d[])
        self.initialize_prey_pop(config_d = config_d)
        # self.landscape.initialize_owl_pop(
        #         initial_owl_pop=config_d["initial_owl_pop"],
        #         move_range = config_d["owl_move_range"],
        #         strike_success_probability = config_d["owl_catch_success"],
        #         open_preference_weight = 1,
        #         bush_preference_weight = 0
        #         )

    def set_predator_population_parameters(self,predator_config_d):
        pass

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

    def sim_stats_per_cycle(self, config_d):
        if self.cycle == 0:
            data_row = []
            data_row.append("sim_id")
            data_row.append("cycle")
            for keys, vals in config_d.items():
                data_row.append(keys)
            self.append_data(file_name = self.sim_parameters_and_totals, data_row = data_row)
        elif self.cycle >= self.burn_in and (self.cycle % self.data_sample_frequency) == 0:
            data_row = []
            data_row.append(self.sim_id)
            data_row.append(self.cycle)
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
        data_info ='{}, {} \n'.format(self.prey_file_path,self.predator_file_path )
        self.sim_info(line = data_info)
        self.sim_info(line = start_info)
        self.make_csv(file_name = self.prey_file_path )
        self.make_csv(file_name = self.predator_file_path )
        self.make_csv(file_name = self.sim_parameters_and_totals)
        self.read_configuration_file()
        for i in range(0,self.end_time,1):
            self.sim_stats_per_cycle(self.config_d)
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
    #sim = Sim(initial_conditions_file_path = 'data.txt', prey_tsv_output_file_path = 'prey_energy.tsv', predator_tsv_output_file_path = 'predator_energy.tsv')
    #sim.main()
    #print('test')



