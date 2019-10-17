
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

	nbr_of_blocks = 1000
	TBSs = [256] * nbr_of_blocks
	TB_ids = list(range(1,nbr_of_blocks+1))

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
	targetBLER = 0.035

	# Initiate blocks sizes and SNR
	TBSs, TB_ids = initTransBlocks()

	# SNR list values
	snr = -27

	comm_overhead = 0.012
	comm_init_overhead = 3 * 0.012
	ru_time = 0.008
	ret = True
	
	# Simulate
	sim = RadSchedSim()


	###########################################
	# Run experiments
	###########################################

	n = 6

	id_subplot = n * 100 + 10

	plt.style.use('seaborn-dark')

#	plt.rcParams.update({'font.size': 12})
	plt.rcParams.update({"font.family": "Times New Roman"})

	fig = plt.figure()

	color = 'Red'

	sim = RadSchedSim()

	for i in range( len( schedulers ) ):

		print()

		# Init transmission blocks and SNR:
		TBSs, TB_ids = initTransBlocks()
		
		SNR_t = [snr] * len(TB_ids) * 128000
		
		# Simulate
		sim.init(	schedulers[i], ret, init_BLER, targetBLER, error_BLER, \
					measured_BLER_error, TBSs, TB_ids, SNR_t)

		sim.simulate()

		id_subplot += 1

		ax = plt.subplot(id_subplot)
		ax.fill_between(sim.RU_acum, 0,sim.nbr_acks_acum, facecolor="red", alpha=.3)
		plt.ylabel(sim.scheduler.getLabel(), rotation=0, ha='right')
		

		RU_acum_min = sim.RU_acum[0]
		RU_acum_max = sim.RU_acum[-1]
#		plt.xlim(RU_acum_min,RU_acum_max)
		plt.xlim(0,2180000)
#		plt.ylim(-2,sim.nbr_blocks+2)
		#plt.xticks([],[])
		

	plt.xticks()
	plt.xlabel('NPUSCH resource usage \ RUs')
	#fig.set_size_inches(10, 5)
	plt.tight_layout()
	plt.subplots_adjust(wspace=0, hspace=0.18)
	plt.savefig("simple_sched_comparation.pdf", dpi=500)
	plt.close(fig)



if __name__ == '__main__':
	main()
