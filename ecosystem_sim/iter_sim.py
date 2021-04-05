#!/usr/bin/python

import csv
import json
import sim
# add in interaction rate
# add in movement of organism
experiment_iterations = 2

control_group = {
    "cycles_of_sim": 100, 
    "krat_data_sample_freq": 50,
    "snake_data_sample_freq": 50, 
    "landscape_size_x": 150,
    "landscape_size_y": 150,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 40,
    "initial_krat_pop": 250,
    "initial_owl_pop": 0,
    "snake_death_probability":0.001,
    "snake_strike_success_probability_bush":0.21, #0.032, #from bouskila 
    "snake_strike_success_probability_open":0.21, #0.009, #from bouskila
    "krat_energy_gain_bush": 12, #from bouskila
    "krat_energy_gain_open": 12, #from bouskila
    "snake_energy_gain": 1500, ## estimate numerical approximationkrat total reproduction death cost 
    "krat_energy_cost":7, # alpha from bouskila
    "snake_energy_cost":14, # beta value not reported by bouskila, using 14 for now because it is twice as much as the krat. it might be worth trying to make this proportional to body size.
    "krat_move_range":20,
    "snake_move_range":20,
    "owl_move_range":20,
    "krat_movement_frequency_per_x_cycles":1, # once per cycle
    "snake_movement_frequency_per_x_cycles":8, # once per 8 cycles
    "owl_movement_frequency_per_x_cycles":1, # once per 8 cycles
    "owl_catch_success":0.21, #from bouskila
    "move_preference_algorithm":False,
    "memory_length_krat":20,
    "memory_length_snake":20,
    "krat_mutation_std":0.15,
    "snake_mutation_std":0.15,
    "krat_mutation_probability":0.01,
    "snake_mutation_probability":0.01,
    "krat_reproduction_freq_per_x_cycles": 50,
    "snake_reproduction_freq_per_x_cycles": 50,
    "mixed_preference_individuals": False
    # 1000 reproduction events
    }

experimental_group_1 = {
    "cycles_of_sim": 100, 
    "krat_data_sample_freq": 50,
    "snake_data_sample_freq": 50, 
    "landscape_size_x": 150,
    "landscape_size_y": 150,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 30,
    "initial_krat_pop": 250,
    "initial_owl_pop": 10,
    "snake_death_probability":0.001,
    "snake_strike_success_probability_bush":0.21, #0.032, #from bouskila 
    "snake_strike_success_probability_open":0.21, #0.009, #from bouskila
    "krat_energy_gain_bush": 12, #from bouskila
    "krat_energy_gain_open": 12, #from bouskila
    "snake_energy_gain": 1500, ## estimate numerical approximationkrat total reproduction death cost 
    "krat_energy_cost":7, # alpha from bouskila
    "snake_energy_cost":14, # beta value not reported by bouskila, using 14 for now because it is twice as much as the krat. it might be worth trying to make this proportional to body size.
    "krat_move_range":20,
    "snake_move_range":20,
    "owl_move_range":20,
    "krat_movement_frequency_per_x_cycles":1, # once per cycle
    "snake_movement_frequency_per_x_cycles":8, # once per 8 cycles
    "owl_movement_frequency_per_x_cycles":1, # once per 8 cycles
    "owl_catch_success":0.21, #from bouskila
    "move_preference_algorithm":False,
    "memory_length_krat":20,
    "memory_length_snake":20,
    "krat_mutation_std":0.15,
    "snake_mutation_std":0.15,
    "krat_mutation_probability":0.01,
    "snake_mutation_probability":0.01,
    "krat_reproduction_freq_per_x_cycles": 50,
    "snake_reproduction_freq_per_x_cycles": 50,
    "mixed_preference_individuals": False
    # 1000 reproduction events
    }

experimental_group_2 = {
    "cycles_of_sim": 100, 
    "krat_data_sample_freq": 50,
    "snake_data_sample_freq": 50, 
    "landscape_size_x": 150,
    "landscape_size_y": 150,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 20,
    "initial_krat_pop": 250,
    "initial_owl_pop": 20,
    "snake_death_probability":0.001,
    "snake_strike_success_probability_bush":0.21, #0.032, #from bouskila 
    "snake_strike_success_probability_open":0.21, #0.009, #from bouskila
    "krat_energy_gain_bush": 12, #from bouskila
    "krat_energy_gain_open": 12, #from bouskila
    "snake_energy_gain": 1500, ## estimate numerical approximationkrat total reproduction death cost 
    "krat_energy_cost":7, # alpha from bouskila
    "snake_energy_cost":14, # beta value not reported by bouskila, using 14 for now because it is twice as much as the krat. it might be worth trying to make this proportional to body size.
    "krat_move_range":20,
    "snake_move_range":20,
    "owl_move_range":20,
    "krat_movement_frequency_per_x_cycles":1, # once per cycle
    "snake_movement_frequency_per_x_cycles":8, # once per 8 cycles
    "owl_movement_frequency_per_x_cycles":1, # once per 8 cycles
    "owl_catch_success":0.21, #from bouskila
    "move_preference_algorithm":False,
    "memory_length_krat":20,
    "memory_length_snake":20,
    "krat_mutation_std":0.15,
    "snake_mutation_std":0.15,
    "krat_mutation_probability":0.01,
    "snake_mutation_probability":0.01,
    "krat_reproduction_freq_per_x_cycles": 50,
    "snake_reproduction_freq_per_x_cycles": 50,
    "mixed_preference_individuals": False
    # 1000 reproduction events
    }

experimental_group_3 = {
    "cycles_of_sim": 100, 
    "krat_data_sample_freq": 50,
    "snake_data_sample_freq": 50, 
    "landscape_size_x": 150,
    "landscape_size_y": 150,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 10,
    "initial_krat_pop": 250,
    "initial_owl_pop": 30,
    "snake_death_probability":0.001,
    "snake_strike_success_probability_bush":0.21, #0.032, #from bouskila 
    "snake_strike_success_probability_open":0.21, #0.009, #from bouskila
    "krat_energy_gain_bush": 12, #from bouskila
    "krat_energy_gain_open": 12, #from bouskila
    "snake_energy_gain": 1500, ## estimate numerical approximationkrat total reproduction death cost 
    "krat_energy_cost":7, # alpha from bouskila
    "snake_energy_cost":14, # beta value not reported by bouskila, using 14 for now because it is twice as much as the krat. it might be worth trying to make this proportional to body size.
    "krat_move_range":20,
    "snake_move_range":20,
    "owl_move_range":20,
    "krat_movement_frequency_per_x_cycles":1, # once per cycle
    "snake_movement_frequency_per_x_cycles":8, # once per 8 cycles
    "owl_movement_frequency_per_x_cycles":1, # once per 8 cycles
    "owl_catch_success":0.21, #from bouskila
    "move_preference_algorithm":False,
    "memory_length_krat":20,
    "memory_length_snake":20,
    "krat_mutation_std":0.15,
    "snake_mutation_std":0.15,
    "krat_mutation_probability":0.01,
    "snake_mutation_probability":0.01,
    "krat_reproduction_freq_per_x_cycles": 50,
    "snake_reproduction_freq_per_x_cycles": 50,
    "mixed_preference_individuals": False
    # 1000 reproduction events
    }

experimental_groups = {
	"control" : control_group,
	"experiment_1": experimental_group_1,
	"experiment_2": experimental_group_2,
	"experiment_3": experimental_group_3,
}


class run_experiments(object):
	def __init__(self,experimental_groups_dictionary, experiment_iterations, output_file_folder = None, rng = None):
		self.experimental_groups = experimental_groups_dictionary
		self.experimental__iterations = experimental_iterations
		self.format_output_folder_fp(output_file_folder = output_file_folder)
		self.rng = rng

	def format_output_folder_fp(self,output_file_folder):
		if output_file_folder is None:
			self.output_file_folder = ''
		else:
			temp_fp_list = list(output_file_folder)
			if temp_fp_list[-1] != '/':
				self.output_file_folder = '/'.join(output_file_folder)
			else:
				self.output_file_folder = output_file_folder

	def run_single_experiment(self, experiment_dictionary, experiment_label):
		ex_label = experiment_dictionary.keys()
		data = experiment_dictionary
		with open('ex_data.txt', 'w') as outfile:
    		json.dump(data, outfile)
		for i in range(self.experiment_iterations):
			krat_data_output_label = self.output_file_folder.join(ex_label + 'sim_{}_krat_info.tsv'.format(i))
			snake_data_output_label = self.output_file_folder.join(ex_label + 'sim_{}_snake_info.tsv'.format(i))
			if self.rng is None:
				sim = Sim(initial_conditions_file_path = 'ex_data.txt', krat_tsv_output_file_path = krat_data_output_label, snake_tsv_output_file_path = snake_data_output_label)
			else:
				sim = Sim(initial_conditions_file_path = 'ex_data.txt', krat_tsv_output_file_path = krat_data_output_label, snake_tsv_output_file_path = snake_data_output_label, rng = self.rng)
    		sim.main()

    def main(self):
    	for key, ex_group in self.experimental_groups.items():
    		self.run_single_experiment(experiment_dictionary = ex_group, experiment_label = key)

if __name__ ==  "__main__":
	differeing_owls = run_experiments(experimental_groups_dictionary = experimental_groups, experiment_iterations = experiment_iterations)
	differeing_owls.main()





