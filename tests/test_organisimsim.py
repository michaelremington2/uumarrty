#!/usr/bin/python
import unittest
from unittest.mock import patch
from xomar import organismsim as org
from xomar import sim

class TestOrganismsimScript(unittest.TestCase):
	
	def setUp(self):
		self.org_bush = org.Organsim
		self.org_open = None

	def tearDown(self):
		pass


if __name__ == '__main__':
	unittest.main()