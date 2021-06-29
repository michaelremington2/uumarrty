#!/usr/bin/python
import unittest
from unittest.mock import patch
import json
import random
import pandas as pd
import numpy as np
import math
from uumarrty import organismsim as org
from uumarrty.sim import Sim, Landscape, Cell



class TestOrganismsimScript(unittest.TestCase):
	
	def setUp(self):
		'''Tests organisms are moving around landscape at an expected frequency.'''
		self.rng = random.Random()
		self.rng.seed(555)
		#self.null_sim = Sim(initial_conditions_file_path = 'Data/null_exp.txt', krat_tsv_output_file_path = 'Data/null_exp_krat_energy.csv', snake_tsv_output_file_path = 'Data/null_exp_snake_energy.csv',rng=self.rng)
		self.org_movement = Sim(
							initial_conditions_file_path = 'Data/movement_test.txt',
							krat_tsv_output_file_path = 'Data/two_krat_movement.csv',
							snake_tsv_output_file_path = 'Data/no_snake.csv',
							rng = self.rng,
							_output_landscape = True,
							_output_landscape_file_path = 'Data/test_landscape.csv')
		self.set_up_movement_data()
		self.org_1_data_frame_build()
		self.org_2_data_frame_build()

	def tearDown(self):
		pass


	def set_up_movement_data(self):
		'''Runs sim and sets up the dataframes for the landscape, and two krats operating on it.'''
		self.org_movement.main()
		self.data_path_krat = 'Data/two_krat_movement.csv'
		self.data_path_landscape = 'Data/test_landscape.csv'
		self.kratdata=pd.read_csv(self.data_path_krat,header=None)
		self.kratdata.columns = ['krat_id', 'cycle','open_pw','bush_pw','energy_score','movements','cell_id','microhabitat','snakes_in_cell','owls_in_cell']
		self.landscape=pd.read_csv(self.data_path_landscape,header=None)
		self.landscape.columns = ['cell_id','microhabitat_type']
		self.kratdata['cell_id'] = self.kratdata['cell_id'].astype('string')
		self.landscape['cell_id'] = self.landscape['cell_id'].astype('string')
		krat_ids = self.kratdata['krat_id'].unique()
		self.k1 = self.kratdata[self.kratdata['krat_id'] == krat_ids[0]]
		self.k2 = self.kratdata[self.kratdata['krat_id'] == krat_ids[1]]

	def org_1_data_frame_build(self):
		'''Builds data frame for first krat of expected and observed movement frequencies.'''
		k1_temp = self.k1[["cell_id",'cycle']].groupby(["cell_id"]).cycle.nunique()
		k1_temp = k1_temp.reset_index()
		self.lk1 = pd.merge(self.landscape, k1_temp, on="cell_id",how='left')
		self.lk1['cycle'] = self.lk1['cycle'].fillna(0)
		self.lk1['total_cycles'] = [len(self.k1) for _ in range(0,len(self.lk1))]
		# Microhabitat Preference Weight
		k1_bush_preference = self.k1['bush_pw'].unique()[0]
		k1_open_preference = 1-k1_bush_preference
		microhabitat_preference_weight = []
		for cell_type in self.lk1['microhabitat_type']:
		    if cell_type == 'OPEN':
		        microhabitat_preference_weight.append(k1_open_preference)
		    else:
		        microhabitat_preference_weight.append(k1_bush_preference)
		self.lk1['mh_pref_weight'] = microhabitat_preference_weight
		#expected movement probability
		ls_counts = self.lk1[['microhabitat_type',"cell_id"]].groupby(["microhabitat_type"]).cell_id.nunique()
		ls_counts = ls_counts.reset_index()
		for index, row in ls_counts.iterrows():
		    if row['microhabitat_type'] == 'BUSH':
		        ls_bush_expected = 1/row['cell_id']
		    elif row['microhabitat_type'] == 'OPEN':
		        ls_open_expected = 1/row['cell_id']
		        
		ls_expected_weight = []
		for cell_type in self.lk1['microhabitat_type']:
		    if cell_type == 'OPEN':
		        ls_expected_weight.append(ls_open_expected)
		    else:
		        ls_expected_weight.append(ls_bush_expected)
		                                  
		self.lk1['ls_expected_weight'] = ls_expected_weight
		self.lk1['expected'] = self.lk1['ls_expected_weight']*self.lk1['mh_pref_weight']
		#observed movement probability and standard error
		self.lk1['observed'] = self.lk1['cycle']/self.lk1['total_cycles']
		std = np.std(self.lk1['observed'])
		self.lk1['st_error_observed']= [std/math.sqrt(len(self.lk1['observed'])) for _ in range(0,len(self.lk1))]
		### Error Check column
		error_check = []
		for index, row in self.lk1.iterrows():
		    upper = row['observed']+row['st_error_observed']
		    lower = row['observed']-row['st_error_observed']
		    if lower <= row['expected'] <= upper:
		        error = 0
		    elif row['observed'] > 1:
		        error = 1
		    elif row['observed'] < 0:
		        error = 1
		    else:
		        error = 1
		    error_check.append(error)
		self.lk1['error_check'] = error_check

	def org_2_data_frame_build(self):
		'''Builds data frame for the second krat of expected and observed movement frequencies.'''
		k2_temp = self.k2[["cell_id",'cycle']].groupby(["cell_id"]).cycle.nunique()
		k2_temp = k2_temp.reset_index()
		self.lk2 = pd.merge(self.landscape, k2_temp, on="cell_id",how='left')
		self.lk2['cycle'] = self.lk2['cycle'].fillna(0)
		self.lk2['total_cycles'] = [len(self.k2) for _ in range(0,len(self.lk2))]
		# Microhabitat Preference Weight
		k2_bush_preference = self.k2['bush_pw'].unique()[0]
		k2_open_preference = 1-k2_bush_preference
		microhabitat_preference_weight = []
		for cell_type in self.lk2['microhabitat_type']:
		    if cell_type == 'OPEN':
		        microhabitat_preference_weight.append(k2_open_preference)
		    else:
		        microhabitat_preference_weight.append(k2_bush_preference)
		self.lk2['mh_pref_weight'] = microhabitat_preference_weight
		#expected movement probability
		ls_counts = self.lk2[['microhabitat_type',"cell_id"]].groupby(["microhabitat_type"]).cell_id.nunique()
		ls_counts = ls_counts.reset_index()
		for index, row in ls_counts.iterrows():
		    if row['microhabitat_type'] == 'BUSH':
		        ls_bush_expected = 1/row['cell_id']
		    elif row['microhabitat_type'] == 'OPEN':
		        ls_open_expected = 1/row['cell_id']
		        
		ls_expected_weight = []
		for cell_type in self.lk2['microhabitat_type']:
		    if cell_type == 'OPEN':
		        ls_expected_weight.append(ls_open_expected)
		    else:
		        ls_expected_weight.append(ls_bush_expected)
		                                  
		self.lk2['ls_expected_weight'] = ls_expected_weight
		self.lk2['expected'] = self.lk2['ls_expected_weight']*self.lk2['mh_pref_weight']
		#observed movement probability and standard error
		self.lk2['observed'] = self.lk2['cycle']/self.lk2['total_cycles']
		std = np.std(self.lk2['observed'])
		self.lk2['st_error_observed']= [std/math.sqrt(len(self.lk2['observed'])) for _ in range(0,len(self.lk2))]
		### Error Check column
		error_check = []
		for index, row in self.lk2.iterrows():
		    upper = row['observed']+row['st_error_observed']
		    lower = row['observed']-row['st_error_observed']
		    if lower <= row['expected'] <= upper:
		        error = 0
		    elif row['observed'] > 1:
		        error = 1
		    elif row['observed'] < 0:
		        error = 1
		    else:
		        error = 1
		    error_check.append(error)
		self.lk2['error_check'] = error_check

	def test_k1_error_check(self):
		test_passed = True
		if sum(self.lk1['error_check']) > 0:
			test_passed = False
		if test_passed:
			pass
		else:
			labels = lk1['cell_id']
			observed = lk1['observed']
			expected = lk1['expected']
			yerror = lk1['st_error_observed']
			x = np.arange(len(labels))  # the label locations
			width = 0.35  # the width of the bars
			fig, ax = plt.subplots()
			fig.set_figheight(15)
			fig.set_figwidth(15)
			rects1 = ax.bar(x - width/2, expected, width, label='expected')
			rects2 = ax.bar(x + width/2, observed, width,yerr = yerror, label='observed')
			# Add some text for labels, title and custom x-axis tick labels, etc.
			ax.set_ylabel('Movement Frequencies')
			ax.set_title('Cell Ids')
			ax.set_xticks(x)
			ax.set_xticklabels(labels)
			ax.legend()
			fig.tight_layout()
			plt.show()
		self.assertEqual(test_passed,True)

	def test_k2_error_check(self):
		test_passed = True
		if sum(self.lk2['error_check']) > 0:
			test_passed = False
		if test_passed:
			pass
		else:
			labels = lk2['cell_id']
			observed = lk2['observed']
			expected = lk2['expected']
			yerror = lk2['st_error_observed']
			x = np.arange(len(labels))  # the label locations
			width = 0.35  # the width of the bars
			fig, ax = plt.subplots()
			fig.set_figheight(15)
			fig.set_figwidth(15)
			rects1 = ax.bar(x - width/2, expected, width, label='expected')
			rects2 = ax.bar(x + width/2, observed, width,yerr = yerror, label='observed')
			# Add some text for labels, title and custom x-axis tick labels, etc.
			ax.set_ylabel('Movement Frequencies')
			ax.set_title('Cell Ids')
			ax.set_xticks(x)
			ax.set_xticklabels(labels)
			ax.legend()
			fig.tight_layout()
			plt.show()
		self.assertEqual(test_passed,True)



if __name__ == '__main__':
	unittest.main()
