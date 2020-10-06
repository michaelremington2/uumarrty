#!/usr/bin/python
import json

data = {}
data['sim'] = []
data['sim'].append({
    "days_of_sim": 730,
    "time_step":2,
    "landscape_size_x": 500,
    "landscape_size_y": 500,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 15,
    "initial_krat_pop": 100,
    "cell_energy_pool": 1500,
    "snake_initial_energy": 300,
    "krat_initial_energy": 40,
    "snake_energy_cost": 1,
    "krat_energy_cost": 1,
    "strike_success_probability": (7/32),
    "krat_energy_gain": 0.00145,
    "krat_max_litter_size": 6,
    "snake_max_litter_size":1,
    "krat_litter_frequency":(1/365),
    "snake_litter_frequency": (1/365)
    })

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)