#!/usr/bin/python
import json
# add in interaction rate
# add in movement of organism
data = {}
data['sim'] = []


data['sim'].append({
    "cycles_of_sim": 100, #3each day is one cycle
    "landscape_size_x": 100,
    "landscape_size_y": 100,
    "microhabitat_open_bush_proportions": [0.5,0.5],
    "initial_snake_pop": 6,
    "initial_krat_pop": 30,
    "initial_owl_pop": 0,
    "snake_strike_success_probability_bush": 0.032, #from bouskila 
    "snake_strike_success_probability_open": 0.009, #from bouskila
    "krat_energy_gain_bush": 12, #from bouskila
    "krat_energy_gain_open": 12, #from bouskila
    "snake_energy_gain": 1500, ## estimate numerical approximationkrat total reproduction death cost divided by 5 because thats about how many kids a krat has on average in its life. This number prolly needs some work.
    "krat_energy_cost":7, # alpha from bouskila
    "krat_cost_of_death":1500, #bouskila value d
    "snake_energy_cost":14, # beta value not reported by bouskila, using 14 for now because it is twice as much as the krat. it might be worth trying to make this proportional to body size.
    "krat_move_range":1,
    "snake_move_range":10,
    "owl_move_range":10,
    "krat_movement_frequency_per_x_cycles":1, # once per cycle
    "snake_movement_frequency_per_x_cycles":8, # once per 8 cycles
    "owl_movement_frequency_per_x_cycles":1, # once per 8 cycles
    "owl_catch_success":0.02, #from bouskila
    "move_preference_algorithm":False,
    "memory_length_krat":20,
    "memory_length_snake":20,
    "krat_pop_genotype_freq": {"open":(1/3),
                               "bush":(1/3),
                               "mixed":(1/3)},
    "snake_pop_genotype_freq": {"open":(1/3),
                               "bush":(1/3),
                               "mixed":(1/3)},
    "krat_reproduction_freq_per_x_cycles": 10,
    "snake_reproduction_freq_per_x_cycles": 100
    })

with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)

#krat_benefit_bush x
#krat_benefit_open x
#probability_snake_bush x
#probability_snake_open x
#probability_owl_open x
#alpha cost to krat in either microhabitat x
#beta cost to snake in either microhabitat x
#percapita payoff bush krat
#percapita payoff open krat
#E payoff to snake if krat is caught
#a determinse intensity of dilution effect
#k number of rodents in the homerange of owl