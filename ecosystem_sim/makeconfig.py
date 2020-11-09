#!/usr/bin/python
import json
# add in interaction rate
# add in movement of organism
data = {}
data['sim'] = []
data['sim'].append({
    "days_of_sim": 365,
    "time_step":1,
    "energy_dependence_movement":False,
    "landscape_size_x": 500,
    "landscape_size_y": 500,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 15,
    "initial_krat_pop": 150,
    "cell_energy_pool": 1200,
    "snake_initial_energy": 300,
    "snake_energy_deviation":100,
    "krat_initial_energy": 40,
    "krat_energy_deviation":10,
    "snake_energy_cost": 0.25,
    "krat_energy_cost": 0.5,
    "strike_success_probability": (7/32),
    "krat_energy_gain": 0.00142,
    "krat_max_litter_size": 6,
    "snake_max_litter_size":1,
    "krat_litter_frequency":(1/365),
    "snake_litter_frequency": (1/420),
    "krat_move_range":1,
    "snake_move_range":6,
    "krat_number_of_moves_per_night":16,
    "snake_number_of_moves_per_night":4,
    "snake_move_range":4,
    "krat_open_preference_weight":1,
    "krat_bush_preference_weight":1,
    "snake_open_preference_weight":1,
    "snake_bush_preference_weight":1
    })

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)