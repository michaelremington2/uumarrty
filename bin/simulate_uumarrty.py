#!/usr/bin/python

import csv
import json
import os
import sys
import argparse
import glob
import re
import json
import uuid
import pandas as pd
from uumarrty import sim
from uumarrty import organismsim


class export_data_from_sims(object):
    def __init__(self,sims, output_file_path_total=None, output_file_path_per_cycle=None):
        self.sims = sims
        self.output_file_path_total = output_file_path_total
        self.output_file_path_per_cycle = output_file_path_per_cycle


    def create_csv(self,fp):
        with open(fp, "w") as my_empty_csv:
            pass

    def get_file_name(self,sim):
        return sim.split("/")[-1]

    def format_experiment_label(self,file_name):
        if len(file_name.split("_")[1]) <= 2:
            experiment = file_name.split("_")[0]+file_name.split("_")[1]
        else:
            experiment = file_name.split("_")[0]
        return experiment       

    def overall_stats(self, sim):
        data=pd.read_csv(sim,header=None)
        data.columns = ['id','generation', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','other_in_cell','owls_in_cell']
        cycles=data['cycle'].max()
        generations=data['generation'].max()
        mean_bush_pref=data['bush_pw'].mean()
        std_bush_pref=data['bush_pw'].std()
        se_bush_pref=data['bush_pw'].sem()
        return cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref

    def data_label(self, file_name):
        if 'krat' in file_name:
            data_type='krat'
        if 'snake' in file_name:
            data_type='snake'
        return data_type

    def extract_info_totals(self):
        #,output_file_path
        if os.path.isfile(self.output_file_path_total):
            pass 
        else: 
            self.create_csv(fp = self.output_file_path_total)
        for sim in self.sims:
            file_name = self.get_file_name(sim = sim)
            experiment = self.format_experiment_label(file_name = file_name)
            sim_number = re.findall(r'\d+',sim)[-1]
            cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref = self.overall_stats(sim=sim)
            data_type = self.data_label(file_name = file_name)
            row = [file_name, experiment, sim_number, data_type, cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref]
            self.append_data(fp = self.output_file_path_total,d_row = row)

    def mean_by_cycle(self):
        if os.path.isfile(self.output_file_path_per_cycle):
            pass 
        else:
            self.create_csv(fp = self.output_file_path_per_cycle)
        # file_names = list(map(self.get_file_name,self.sims))
        # experiment_names = list(map(self.format_experiment_label, file_names))
        # for experiment, sim in zip(experiment_names, self.sims, experiment_names):
        for sim in self.sims:
            file_name = self.get_file_name(sim = sim)
            experiment = self.format_experiment_label(file_name = file_name)
            sim_number = re.findall(r'\d+',sim)[-1]
            data_type = self.data_label(file_name = file_name)
            data=pd.read_csv(sim,header=None)
            data.columns = ['id','generation', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','other_in_cell','owls_in_cell']
            grouped_data = data.groupby("cycle").agg({'id':['count'], 'bush_pw':['mean','std'],'energy_score':['mean','std','sum'],'movements':['mean','std','sum'],'others_in_cell':['mean','std','sum'],'owls_in_cell':['mean','std','sum'] })
            grouped_data = grouped_data.reset_index()
            for index, row in grouped_data.iterrows():
                dr = [file_name, experiment, sim_number, data_type] + row
                self.append_data(fp = self.output_file_path_per_cycle, d_row = dr)

    def append_data(self,fp,d_row):
        with open(fp, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(d_row)

    def main(self):
        if self.output_file_path_total is not None:
            self.extract_info_totals()
        if self.output_file_path_per_cycle is not None:
            self.mean_by_cycle()


class run_experiments(object):
    def __init__(self,experimental_groups_dict, experiment_iterations, output_file_folder = None, rng = None, seed = None, burn_in = None, agg_sim_info=False, sim_info_output_file=None):
        self.experimental_groups= experimental_groups_dict
        self.experiment_iterations = experiment_iterations
        self.format_output_folder_fp(output_file_folder = output_file_folder)
        self.rng = rng
        self.seed = seed
        self.burn_in = burn_in
        self.agg_sim_info = agg_sim_info
        self.sim_info_output_file =  sim_info_output_file


    def format_output_folder_fp(self,output_file_folder):
        if output_file_folder is None:
            self.output_file_folder = ''
        else:
            self.output_file_folder = output_file_folder 

    def run_single_experiment(self, experiment_dictionary, experiment_label):
        ex_label = experiment_label
        data = experiment_dictionary
        config_file_name = 'config_{}.txt'.format(ex_label)
        with open(config_file_name, 'w') as outfile:
            json.dump(data, outfile)
        for i in range(self.experiment_iterations):
            krat_data_output_file_label = self.output_file_folder + ex_label + '_sim_{}_krat_info.csv'.format(i)
            snake_data_output_file_label = self.output_file_folder + ex_label + '_sim_{}_snake_info.csv'.format(i)
            print(krat_data_output_file_label)
            print(snake_data_output_file_label)
            sim_object = sim.Sim(initial_conditions_file_path = config_file_name,
                                 krat_csv_output_file_path = krat_data_output_file_label,
                                 snake_csv_output_file_path = snake_data_output_file_label,
                                 seed = self.seed,
                                 burn_in = self.burn_in,
                                 sim_info_output_file=self.sim_info_output_file)
            sim_object.main()
            if self.agg_sim_info:
                sims = [krat_data_output_file_label, snake_data_output_file_label]
                output_file_path_total = self.output_file_folder + 'totals.csv'
                output_file_path_per_cycle = self.output_file_folder + 'per_cycle.csv'
                edfs = export_data_from_sims(sims = sims, output_file_path_total=output_file_path_total, output_file_path_per_cycle = output_file_path_per_cycle)
                edfs.main()
                for i in sims:
                    if os.path.exists(i):
                        os.remove(i)

    def main(self):
        for key, ex_group in self.experimental_groups.items():
            self.run_single_experiment(experiment_dictionary = ex_group, experiment_label = key)



def run(args):
    init_file_path = args.input # these match the "dest": dest="input"
    iterations = args.iterations
    output_file_path = args.output # from dest="output"
    sim_info = args.sim_info
    burn_in = args.burn_in
    seed = args.seed
    agg_sims = args.agg_sims
    with open(init_file_path) as f:
        config_exp = json.load(f)
    run_simulations = run_experiments(experimental_groups_dict=config_exp,
                                      experiment_iterations=iterations,
                                      output_file_folder=output_file_path,
                                      burn_in = burn_in,
                                      seed = seed,
                                      agg_sim_info=agg_sims,
                                      sim_info_output_file=sim_info)
    run_simulations.main()


def main():
    parser=argparse.ArgumentParser(description="Run experiments through uumarrty game theory model.")
    parser.add_argument("-in",help="json or txt file full of 1 to several experimental groups." ,dest="input", type=str, required=True)
    parser.add_argument("-out",help="output file folder. ex: Data/" ,dest="output", type=str, required=False, default=None)
    parser.add_argument("-iter",help="Number of times you want the experiment to be repeated." ,dest="iterations", type=int, required=True)
    parser.add_argument("-sim_info",help="txt file for updates on meta stats of how simulations are running." ,dest="sim_info", type=str, required=False, default=None)
    parser.add_argument("-burn_in",help="Number of cycles before the simulation starts collecting data on the simulation." ,dest="burn_in", type=int, required=False)
    parser.add_argument("-seed",help="Random number seed for the sim." ,dest="seed", type=int, required=False)
    parser.add_argument("-agg_sims",help="Aggregates data from sims and removes the indiviudal sim data csvs." ,dest="agg_sims", type=bool, required=False)
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)

if __name__=="__main__":
    main()

    








