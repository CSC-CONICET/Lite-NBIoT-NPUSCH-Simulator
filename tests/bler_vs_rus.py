
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


def initTransBlocks():

	nbr_of_blocks = 20
	TBSs = [256] * nbr_of_blocks
	TB_ids = list(range(10,nbr_of_blocks+10))

	return TBSs, TB_ids
	

def main():

	############################################
	# Initialization
	###########################################

	# Number of experiments to be averaged
	experiments_nbr = 10

	# Initiate schedulers
	scheduler = RadSched_ITBS_Rep()

    # BLER
	init_BLER = 1
	error_BLER = 0. # 0.03
	measured_BLER_error = 0. # 0.25

	blers = [ 0.0, 0.05, 0.1, 0.15 ]

	# Initiate blocks sizes and SNR
	TBSs, TB_ids = initTransBlocks()

	# SNR list values
	snrs = [-20, -16, -12, -8]

	ret = False

	# Simulator
	sim = RadSchedSim()

	###########################################
	# Run experiments
	###########################################

	nbr_RUs_avgs_by_snr_by_bler = []
	nbr_RUs_devs_by_snr_by_bler = []

	for bler in blers:

		nbr_RUs_avgs_by_snr = []
		nbr_RUs_devs_by_snr = []

		for snr in snrs:	

			s_loss = 0

			nbr_RUs = []

			print ( "Processing experiments for SNR", snr, ", scheduler", scheduler.getLabel() )

			for j in range( experiments_nbr ):

				# Init transmission blocks and SNR:
				TBSs, TB_ids = initTransBlocks()
				
				SNR_t = [snr] * len(TB_ids) * 1280
				
				# Simulate
				sim.init(	scheduler, ret, init_BLER, bler, error_BLER, \
							measured_BLER_error, TBSs, TB_ids, SNR_t )

				sim.simulate()

				# Register output parameters
				nbr_RUs.append( sim.getNbrRUs() )

			# Calculate averages
			nbr_RUs_avg = sum( nbr_RUs ) / experiments_nbr

			# Calculate standard deviations
			s = 0
			for x in nbr_RUs:
				s += ( x - nbr_RUs_avg )**2
			nbr_RUs_dev = ( s / ( experiments_nbr - 1 ) )**0.5

			# Register averages
			nbr_RUs_avgs_by_snr.append( nbr_RUs_avg )
			
			# Register standard deviations
			nbr_RUs_devs_by_snr.append( nbr_RUs_dev )

		# Register parameters by scheduler
		nbr_RUs_avgs_by_snr_by_bler.append(nbr_RUs_avgs_by_snr)
		nbr_RUs_devs_by_snr_by_bler.append(nbr_RUs_devs_by_snr)

	# Plot figures
	out_file = 'rus_by_snr_by_bler.pdf'
	x_axis_label = 'SNR \ dB'
	y_axis_label = 'NPUSCH resource usage \ RUs'
	plot_figure( out_file, x_axis_label, y_axis_label, snrs, blers,
				 nbr_RUs_avgs_by_snr_by_bler , nbr_RUs_devs_by_snr_by_bler)


# Plot a barchart with error bar
def plot_figure( out_file, x_axis_label, y_axis_label, snrs,
				 blers, avgs , devs):


	fig = plt.figure()
	
	plt.style.use('seaborn-darkgrid')
	plt.rcParams.update({'font.size': 15})
	
	avgs_trans = list(map(list, zip(*avgs)))
	
	legends = []
	i = 0
	for b in blers:
		legends.append( b )
		i += 1
	
	df = pd.DataFrame(avgs_trans, index=snrs, columns=legends)
	df.plot.bar(yerr=devs, colormap='Reds', width=0.8, rot=0.);

	plt.xlabel(x_axis_label)
	plt.ylabel(y_axis_label)
	ymax = max(max(avgs_trans))
	plt.ylim(700, ymax*1.3)
	plt.yscale('symlog')
	plt.legend(	ncol=2, title='BLER', borderaxespad=0., fontsize='medium')
	plt.tight_layout()
	fig.set_size_inches(8, 6)
	plt.savefig(str(out_file), dpi=500)
	plt.close(fig)

if __name__ == '__main__':
	main()
