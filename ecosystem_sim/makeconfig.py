#!/usr/bin/python
import json
# add in interaction rate
# add in movement of organism
data = {}
data['sim'] = []
data['sim'].append({
    "days_of_sim": 3650,
    "time_step":1,
    "energy_dependence_movement":False,
    "landscape_size_x": 500,
    "landscape_size_y": 500,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 8,
    "initial_krat_pop": 100,
    "initial_owl_pop": 2,
    "snake_strike_success_probability_bush": 0.032,
    "snake_strike_success_probability_open": 0.009,
    "krat_energy_gain_bush": 12,
    "krat_energy_gain_open": 12,
    "krat_move_range":1,
    "snake_move_range":4,
    "owl_move_range":6,
    "owl_catch_success":0.02,
    "krat_open_preference_weight":1,
    "krat_bush_preference_weight":1,
    "snake_open_preference_weight":1,
    "snake_bush_preference_weight":1,
    "owl_open_preference_weight":1,
    "owl_bush_preference_weight":1
    })

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)

#krat_benefit_bush
#krat_benefit_open
#probability_snake_bush
#probability_snake_open
#probability_owl_open
#alpha cost to krat in either microhabitat
#beta cost to snake in either microhabitat
#percapita payoff bush krat
#percapita payoff open krat
#E payoff to snake if krat is caught
#a determinse intensity of dilution effect
#k number of rodents in the homerange of owl