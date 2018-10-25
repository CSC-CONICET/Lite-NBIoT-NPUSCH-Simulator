
import numpy as np
import matplotlib.pyplot as plt
from random import randint
import random
from math import ceil

class RadSched_ITBS_Rep:

	def __init__(self):
		self.label = "ITBS-Rep"
		self.BLER_updated_time = 0
		self.BLER_T = 320
		self.last_BLER = -1

	def getLabel(self):
		return self.label

	def schedule( self, simulator):

		curr_time = simulator.time[-1]
		curr_HARQ_feedback = simulator.HARQ_feedback[-1]
		curr_nbr_rep = simulator.nbr_repetitions[-1]
		curr_ITBS = simulator.ITBS[-1]

		#################################################################
		# BLER and repetitions update
		#################################################################

		e = simulator.measured_BLER_error
		curr_measured_BLER_error = random.uniform(-e,e)
		self.last_BLER = simulator.BLER_CHANEL[-1] + curr_measured_BLER_error
		if self.last_BLER > 1.:
			self.last_BLER = 1.
		elif self.last_BLER < 0.:
			self.last_BLER = 0.

		#################################################################
		# Update Number of repetitions and ITBS
		#################################################################

		if self.last_BLER < simulator.target_BLER - simulator.error_BLER:

			if curr_ITBS < simulator.ITBS_max:
				curr_ITBS = curr_ITBS + 1
			else:
				curr_nbr_rep = max( ceil( curr_nbr_rep / 2 ) , simulator.nbr_rep_min)
				
		elif self.last_BLER > simulator.target_BLER + simulator.error_BLER:

			if curr_ITBS > simulator.ITBS_min:
				curr_ITBS = curr_ITBS - 1
			else:
				curr_nbr_rep = min( 2 * curr_nbr_rep , simulator.nbr_rep_max)
				

		return curr_nbr_rep, curr_ITBS, self.last_BLER



	