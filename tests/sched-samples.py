import sys
sys.path.append('../src')
from RadSchedSim import RadSchedSim
from RadSched_ITBS_and_Rep import RadSched_ITBS_and_Rep
from RadSched_ITBS_Rep import RadSched_ITBS_Rep
from RadSched_Rep_ITBS import RadSched_Rep_ITBS
from RadSched_Rep import RadSched_Rep
from RadSched_ITBS import RadSched_ITBS
from RadSched_FCMRSA import RadSched_FCMRSA

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

def initSchedulers():
	schedulers = []

	schedulers.append( RadSched_ITBS() )
	schedulers.append( RadSched_ITBS_and_Rep() )
	schedulers.append( RadSched_Rep_ITBS() )
	schedulers.append( RadSched_Rep() )
	schedulers.append( RadSched_ITBS_Rep() )
	schedulers.append( RadSched_FCMRSA() )
	
	return schedulers


def initTransBlocks():

	nbr_of_blocks = 20
	TBSs = [256] * nbr_of_blocks
	TB_ids = list(range(10,nbr_of_blocks+10))

	return TBSs, TB_ids


def main():

	############################################
	# Initialization
	###########################################

	# Initiate schedulers
	schedulers = initSchedulers()

    # BLER
	init_BLER = 1
	error_BLER = 0.0
	measured_BLER_error = 0.0
	targetBLER = 0.05

	# Initiate blocks sizes and SNR
	TBSs, TB_ids = initTransBlocks()
	init_ITBS = 4
	init_nr = 64

	# SNR list values
	snrs = [-24]

	# Simulate
	sim = RadSchedSim()

	###########################################
	# Run experiments
	###########################################

	for ret in [ True, False ]:

			for i in range( len( schedulers ) ):

				for snr in snrs:

					print ( "Processing experiments... Ret ", "enable" if ret else "disable" ,", Target-BLER ", targetBLER, ", Scheduler ", schedulers[i].getLabel(), ", SNR ", snr)

					# Init.
					TBSs, TB_ids = initTransBlocks()
					
					SNR_t = [snr] * len(TB_ids) * 1280

					# Simulate
					sim.init(	schedulers[i], ret, 
								init_ITBS, init_nr, init_BLER,
								targetBLER, error_BLER, \
								measured_BLER_error, TBSs, TB_ids, SNR_t)

					sim.simulate()

					sim.plot_results(	str(schedulers[i].getLabel()) + "_targetBLER_"
										+ str(int(targetBLER*100)) + "_SNR_" + str(snr)
										+ "_ret_" + str(ret) + ".pdf")

if __name__ == '__main__':
	main()
