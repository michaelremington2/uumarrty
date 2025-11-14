import csv
import os
import pandas as pd
import re

class Export_Data(object):
    def __init__(self,sims, output_file_path_total=None, output_file_path_per_cycle=None):
        self.sims = sims
        self.output_file_path_total = output_file_path_total
        self.output_file_path_per_cycle = output_file_path_per_cycle


    def create_csv(self,fp, header=None):
        with open(fp, "w") as my_empty_csv:
            pass
        if header is not None:
            self.append_data(fp = fp, d_row = header)

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
        data.columns = ['sim_id','id','generation', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','other_in_cell','owls_in_cell']
        sim_id=data['sim_id'].max()
        cycles=data['cycle'].max()
        generations=data['generation'].max()
        mean_bush_pref=data['bush_pw'].mean()
        std_bush_pref=data['bush_pw'].std()
        se_bush_pref=data['bush_pw'].sem()
        return sim_id, cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref

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
            header = ['sim_id', 'file_name', 'experiment', 'sim_number', 'data_type', 'cycles', 'generations', 'mean_bush_pref', 'std_bush_pref', 'se_bush_pref']
            self.append_data(fp = self.output_file_path_total,d_row = header)
        for sim in self.sims:
            file_name = self.get_file_name(sim = sim)
            experiment = self.format_experiment_label(file_name = file_name)
            sim_number = re.findall(r'\d+',sim)[-1]
            try:
                sim_id, cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref = self.overall_stats(sim=sim)
            except pd.errors.EmptyDataError:
                sim_id=float("NaN")
                cycles=float("NaN")
                generations=float("NaN")
                mean_bush_pref=float("NaN")
                std_bush_pref= float("NaN")
                se_bush_pref= float("NaN")
            data_type = self.data_label(file_name = file_name)
            row = [sim_id, file_name, experiment, sim_number, data_type, cycles, generations, mean_bush_pref, std_bush_pref, se_bush_pref]
            self.append_data(fp = self.output_file_path_total,d_row = row)

    def mean_by_cycle(self):
        #parameter_df = pd.read_csv(self.parameter_file, header = 0, index_col=None)
        if os.path.isfile(self.output_file_path_per_cycle):
            pass 
        else:
            header = ['file_name','experiment','sim_number',
                  'org','sim_id', 'generation','cycle','pop_count',
                  'bush_pw_mean','bush_pw_std',
                  'energy_score_mean','energy_score_std','energy_score_sum',
                  'movements_mean','movements_std','movements_sum',
                  'other_in_cell_mean','other_in_cell_std','other_in_cell_sum',
                  'owls_in_cell_mean','owls_in_cell_std','owls_in_cell_sum']
            header = header# + par_file_headers
            self.create_csv(fp = self.output_file_path_per_cycle, header = header)
            #self.create_csv(fp = self.output_file_path_per_cycle, header = header)
        for sim in self.sims:
            file_name = self.get_file_name(sim = sim)
            experiment = self.format_experiment_label(file_name = file_name)
            sim_number = re.findall(r'\d+',sim)[-1]
            data_type = self.data_label(file_name = file_name)
            try:
                data=pd.read_csv(sim,header=None)
                data.columns = ['sim_id','id','generation', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','other_in_cell','owls_in_cell']
                grouped_data = data.groupby(['sim_id','generation','cycle']).agg({'id':['count'], 'bush_pw':['mean','std'],'energy_score':['mean','std','sum'],'movements':['mean','std','sum'],'other_in_cell':['mean','std','sum'],'owls_in_cell':['mean','std','sum'] })
                grouped_data = grouped_data.reset_index()
                for index, row in grouped_data.iterrows():
                    d1 = [file_name, experiment, sim_number, data_type]
                    dr =  d1 + list(row)
                    self.append_data(fp = self.output_file_path_per_cycle, d_row = dr)
            except pd.errors.EmptyDataError:
                d1 = [file_name, experiment, sim_number, data_type]
                dr = d1 + [float("NaN") for i in range(len(header)-4)]
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