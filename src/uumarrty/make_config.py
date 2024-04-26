#!/usr/bin/python
import json
import argparse


control_group = {"cycles_of_sim": 50000,
                 "organisms": {"Organism_1": {"Species_Label": "Kangaroo Rat",
                                              "Class": "Prey",
                                              "Data_Sampling_Frequency": 25,
                                              "Initial_Pop_Size": 1000,
                                              "Movement_Frequency": 1,
                                              "Mixed_Preference_Individuals": True,
                                              "Reproduction_Frequency":,
                                              "Mutation_Probability": 0.1,
                                              "Mutation_Standard_Deviation": 0.15,
                                              "Payoffs": {"Microhabitat_1": {"Foraging_Gain": 12,
                                                                             "Foraging_Cost": 7},
                                                          "Microhabitat_2": {"Foraging_Gain": 8,
                                                                             "Foraging_Cost": 7},
                                                          "Microhabitat_3": {"Foraging_Gain": 0,
                                                                             "Foraging_Cost": 7}
                                                         }
                                              },
                                "Organism_2": {"Species_Label": "Rattlesnake",
                                              "Class": "Predator",
                                              "Data_Sampling_Frequency": 25,
                                              "Initial_Pop_Size": 50,
                                              "Movement_Frequency": 8,
                                              "Mixed_Preference_Individuals": True,
                                              "Mutation_Probability": 0.1,
                                              "Mutation_Standard_Deviation": 0.15,
                                              "Death_Probability":0.001,
                                              "Strike_Success_Probability": {"Prey_Name": "Kangaroo Rat",
                                                                             "Microhabitat_1": 0.21,
                                                                             "Microhabitat_2": 0.21,
                                                                             "Microhabitat_3": 0.21},
                                              "Payoffs":{"Prey_Name": "Kangaroo Rat",
                                                         "Foraging_Gain": 1500,
                                                         "Foraging_Cost": 14,
                                              }
                                                                             }
                                }
                 "landscape_size_x": 15,
                 "landscape_size_y": 15, 
                 "microhabitat_open_bush_proportions": [0.5, 0.5],
                 "initial_owl_pop": 0,
                 "snake_energy_gain": 1500,
                 "krat_energy_cost": 7,
                 "snake_energy_cost": 14,
                 "snake_movement_frequency_per_x_cycles": 8,
                 "owl_movement_frequency_per_x_cycles": 1,
                 "owl_catch_success": 0.21,
                 "krat_mutation_std": 0.15,
                 "snake_mutation_std": 0.15,
                 "krat_mutation_probability": 0.01,
                 "snake_mutation_probability": 0.01,
                 "krat_reproduction_freq_per_x_cycles": 50,
                 "snake_reproduction_freq_per_x_cycles": 50,
                 "mixed_preference_individuals": False,
                 "prey_competition": False}

experimental_groups = {
    "control" : control_group,
    # "experiment_1": experimental_group_1,
    # "experiment_2": experimental_group_2,
    # "experiment_3": experimental_group_3,
}
def make_file(experimental_groups, file_name):
    with open(file_name, 'w') as outfile:
        json.dump(experimental_groups, outfile)

def run(args):
    file_name = args.file_name
    make_file(experimental_groups = experimental_groups, file_name = file_name) 

def main():
    # python agg_sims.py -in  owl_data/sim_data/ -totals owl_data/total_sims_stats.csv
    #python agg_sims.py -in  owl_data/sim_data/ -per_cycle owl_data/owl_sim_stats_per_cycle.csv
    parser=argparse.ArgumentParser(description="Makes a config file for uumarrty software.")
    parser.add_argument("-file_name",help="the output config filename." ,dest="file_name", type=str, required=True)
    parser.set_defaults(func=run)
    args=parser.parse_args()
    args.func(args)
    

if __name__=="__main__":
    main()
