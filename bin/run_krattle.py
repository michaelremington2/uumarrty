#!/usr/bin/python

import csv
import json
import os
import sys
#import krattle
#from krattle import sim

class run_experiments(object):
    def __init__(self,experimental_groups_dict, experiment_iterations, output_file_folder = None, rng = None):
        self.experimental_groups= experimental_groups_dict
        self.experiment_iterations = experiment_iterations
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
        ex_label = experiment_label
        data = experiment_dictionary
        with open('ex_data.txt', 'w') as outfile:
            json.dump(data, outfile)
        for i in range(self.experiment_iterations):
            krat_data_output_file_label = self.output_file_folder.join(ex_label + '_sim_{}_krat_info.tsv'.format(i))
            snake_data_output_file_label = self.output_file_folder.join(ex_label + '_sim_{}_snake_info.tsv'.format(i))
            if self.rng is None:
                sim_object = Sim(initial_conditions_file_path = 'ex_data.txt', krat_tsv_output_file_path = krat_data_output_label, snake_tsv_output_file_path = snake_data_output_label)
            else:
                sim_object = Sim(initial_conditions_file_path = 'ex_data.txt', krat_tsv_output_file_path = krat_data_output_label, snake_tsv_output_file_path = snake_data_output_label, rng = self.rng)
            sim_object.main()
        if os.path.exists('ex_data.txt'):
            os.remove('ex_data.txt')

    def main(self):
        for key, ex_group in self.experimental_groups.items():
            self.run_single_experiment(experiment_dictionary = ex_group, experiment_label = key)


def run(args):
    init_file_path= args.input # these match the "dest": dest="input"
    iterations = args.iterations
    output_file_path = args.output # from dest="output"
    with open(input_file_path) as f:
        config_exp = json.load(f)
    run_simulations = run_experiments(experimental_groups_dict=config_exp, experiment_iterations=experiment_iterations, output_file_folder=output_file_path)
    run_simulations.main()


def main():
    parser=argparse.ArgumentParser(description="Run experiments through krattle game theory model.")
    parser.add_argument("-in",help="json or txt file full of 1 to several experimental groups." ,dest="input", type=str, required=True)
    parser.add_argument("-iter",help="Number of times you want the experiment to be repeated." ,dest="iterations", type=int, required=True)
    parser.add_argument("-out",help="output file path" ,dest="output", type=str, required=False, default=None)
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)

if __name__=="__main__":
    #main()
    print(sys.path)
    








