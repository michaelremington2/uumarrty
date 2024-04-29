#!/usr/bin/python
import csv
import sys
import argparse
import pandas as pd 
import glob
import re
import json


class export_data_from_sims(object):
    def __init__(self,sims, output_file_path_total, output_file_path_per_cycle=None):
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

    def open_counts(self, phenotype_counts):
        if 'OPEN' in phenotype_counts.index:
            # Get the count value for 'X'
            open_n = phenotype_counts.loc['OPEN']
        else:
            open_n = 0
        return open_n

    def bush_counts(self, phenotype_counts):
        if 'BUSH' in phenotype_counts.index:
            # Get the count value for 'X'
            bush_n = phenotype_counts.loc['BUSH']
        else:
            bush_n = 0
        return bush_n

    def overall_stats(self, sim):
        data = pd.read_csv(sim,header=None)
        data.columns = ['id','generation', 'cycle','phenotype', 'open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','other_in_cell','owls_in_cell']
        cycles = data['cycle'].max()
        generations = data['generation'].max()
        mean_bush_pref = data['bush_pw'].mean()
        std_bush_pref = data['bush_pw'].std()
        se_bush_pref = data['bush_pw'].sem()
        total_counts = data.shape[0] 
        # phenotype_counts = data['phenotype'].value_counts()
        # open_n = self.open_counts(phenotype_counts)
        # bush_n = self.bush_counts(phenotype_counts)
        return cycles, generations, total_counts,  mean_bush_pref, std_bush_pref, se_bush_pref

    def data_label(self, file_name):
        if 'krat' in file_name:
            data_type='krat'
        if 'snake' in file_name:
            data_type='snake'
        return data_type


    def extract_info_totals(self):
        #,output_file_path
        self.create_csv(fp = self.output_file_path_total)
        for sim in self.sims:
            file_name = self.get_file_name(sim = sim)
            experiment = self.format_experiment_label(file_name = file_name)
            sim_number = re.findall(r'\d+',sim)[-1]
            cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref = self.overall_stats(sim =sim)
            data_type = self.data_label(file_name = file_name)
            row = [file_name, experiment, sim_number, data_type, cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref]
            self.append_data(fp = self.output_file_path_total,d_row = row)

    def mean_by_cycle(self):
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
            data.columns = ['id','generation', 'cycle', 'phenotype', 'open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','other_in_cell','owls_in_cell']
            grouped_data = data.groupby(['cycle', 'phenotype']).agg({
                'id': 'count',        # Count of individuals (assuming 'id' is unique identifier)
                'bush_pw': 'mean'     # Mean bush preference
            }).reset_index()
            pivot_data = grouped_data.pivot(index='cycle', columns='phenotype', values=['id', 'bush_pw'])
            pivot_data.columns = [f'{agg_type}_{column}_{phenotype}' for (agg_type, column, phenotype) in pivot_data.columns]

            for index, row in grouped_data.iterrows():
                dr = [file_name, experiment, sim_number, data_type, row['cycle'], row['bush_pw']]
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



def run(args):
    directory = args.input
    output_file_path_total = args.output_file_path_total
    output_file_path_per_cycle = args.output_file_path_per_cycle
    sims = glob.glob(directory + "*.csv")
    edfs = export_data_from_sims(sims = sims, output_file_path_total=output_file_path_total, output_file_path_per_cycle = output_file_path_per_cycle)
    edfs.main()

    #output_file_path = args.output # from dest="output"


def main():
    # python agg_sims.py -in  owl_data/sim_data/ -totals owl_data/total_sims_stats.csv
    #python agg_sims.py -in  owl_data/sim_data/ -per_cycle owl_data/owl_sim_stats_per_cycle.csv
    parser=argparse.ArgumentParser(description="Aggregate the results and output a csv of them.")
    parser.add_argument("-in",help="a directory full of csvs." ,dest="input", type=str, required=True)
    parser.add_argument("-totals",help="a file path for the output csv of the stat on all simulations" ,dest="output_file_path_total", type=str, required=False, default=None)
    parser.add_argument("-per_cycle",help="a file path for the output csv of the stats on all simulations grouped by cycle" ,dest="output_file_path_per_cycle", type=str, required=False, default=None)
    #parser.add_argument("-exp_config_file",help="the file of the config for the experiment" ,dest="config", type=str, required=False, default=None)
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)
    

if __name__=="__main__":
    main()
