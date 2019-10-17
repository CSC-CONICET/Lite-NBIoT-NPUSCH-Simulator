
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

	nbr_of_blocks = 500
	TBSs = [256] * nbr_of_blocks
	TB_ids = list(range(10,nbr_of_blocks+10))

	return TBSs, TB_ids
	

def main():

	############################################
	# Initialization
	###########################################

	# Number of experiments to be averaged
	experiments_nbr = 50

	# Initiate schedulers
	schedulers = initSchedulers()

	# BLER
	init_BLER = 1
	error_BLER = 0.0 # 0.03
	measured_BLER_error = 0.0 # 0.25

	# Initiate blocks sizes and SNR
	TBSs, TB_ids = initTransBlocks()
	init_ITBS = 4
	init_nr = 64

	# SNR list values
	snrs = [-24,-20,-16]

	comm_overhead = 0.012
	comm_init_overhead = 3 * 0.012
	ru_time = 0.008
	
	# Simulate
	sim = RadSchedSim()


	###########################################
	# Run experiments
	###########################################

	for ret in [ True, False ]:

		if ret :
			targetBLERs = [ 0.05 ]
		else:
			targetBLERs = [ 0, 0.05 ]

		for tb in targetBLERs :

			# Experiment outputs init.	
			tb_losses_avgs_by_snr_by_sched = []
			tb_losses_devs_by_snr_by_sched = []
			nbr_RUs_avgs_by_snr_by_sched = []
			nbr_RUs_devs_by_snr_by_sched = []
			delay_avgs_by_snr_by_sched = []
			delay_devs_by_snr_by_sched = []

			for i in range( len( schedulers ) ):

				tb_losses_avgs_by_snr = []
				tb_losses_devs_by_snr = []

				nbr_RUs_avgs_by_snr = []
				nbr_RUs_devs_by_snr = []

				delay_avgs_by_snr = []
				delay_devs_by_snr = []

				for snr in snrs:

					s_loss = 0

					tb_losses = []

					nbr_RUs = []

					delay = []

					print ( "Processing experiments... Ret ", "enable" if ret else "disable" ,", Target-BLER ", tb, ", Scheduler ", schedulers[i].getLabel(), ", SNR ", snr)

					for j in range( experiments_nbr ):

						print ( "{0:.2f}".format( j / ( experiments_nbr - 1 ) * 100 ),"%", end="\r")

						# Init.
						TBSs, TB_ids = initTransBlocks()
						
						SNR_t = [snr] * len(TB_ids) * 1280

						init_ITBS = random.randint(0, 8)

						init_nr = pow(2,random.randint(0, 7))

						# Simulate
						sim.init(	schedulers[i], ret, 
								init_ITBS, init_nr, init_BLER,
								tb, error_BLER, \
								measured_BLER_error, TBSs, TB_ids, SNR_t)

						sim.simulate()

						# Register output parameters
						if not ret:
							tb_losses.append( sim.getTBLoss() )
						nbr_RUs.append( sim.getNbrRUs() )
						delay.append( sim.getNbrRUs() * ru_time + comm_overhead )


					# Calculate averages
					if not ret:
						tb_losses_avg = sum( tb_losses ) / experiments_nbr
					nbr_RUs_avg = sum( nbr_RUs ) / experiments_nbr
					delay_avg = sum( delay ) / experiments_nbr

					# Calculate standard deviations
					if not ret:
						s = 0
						for x in tb_losses:
							s += ( x - tb_losses_avg )**2
						tb_losses_dev = ( s / ( experiments_nbr - 1 ) )**0.5

					s = 0
					for x in nbr_RUs:
						s += ( x - nbr_RUs_avg )**2
					nbr_RUs_dev = ( s / ( experiments_nbr - 1 ) )**0.5

					s = 0
					for x in delay:
						s += ( x - delay_avg )**2
					delay_dev = ( s / ( experiments_nbr - 1 ) )**0.5

					# Register averages
					if not ret:
						tb_losses_avgs_by_snr.append( tb_losses_avg )
					nbr_RUs_avgs_by_snr.append( nbr_RUs_avg )
					delay_avgs_by_snr.append( delay_avg )
					
					# Register standard deviations
					if not ret:
						tb_losses_devs_by_snr.append( tb_losses_dev )
					nbr_RUs_devs_by_snr.append( nbr_RUs_dev )
					delay_devs_by_snr.append( delay_dev )

				# Register parameters by scheduler
				if not ret:
					tb_losses_avgs_by_snr_by_sched.append( tb_losses_avgs_by_snr )
					tb_losses_devs_by_snr_by_sched.append( tb_losses_devs_by_snr )
				nbr_RUs_avgs_by_snr_by_sched.append( nbr_RUs_avgs_by_snr )
				nbr_RUs_devs_by_snr_by_sched.append( nbr_RUs_devs_by_snr )
				delay_avgs_by_snr_by_sched.append( delay_avgs_by_snr )
				delay_devs_by_snr_by_sched.append( delay_devs_by_snr )


			# Plot figures

			out_file = 'nru_snr_sched_bler_' + str(int(tb*100)) + "_ret_" + str(ret) +'.pdf'
			x_axis_label = 'SNR \ dB'
			y_axis_label = 'NPUSCH resource usage \ RUs'
			plot_figure( out_file, x_axis_label, y_axis_label, snrs, schedulers,
						 nbr_RUs_avgs_by_snr_by_sched , nbr_RUs_devs_by_snr_by_sched, 0. )


			# out_file = 'delay_snr_sched_bler_' + str(int(tb*100)) + "_ret_" + str(ret) +'.pdf'
			# x_axis_label = 'SNR \ dB'
			# y_axis_label = 'delay \ s'
			# plot_figure( out_file, x_axis_label, y_axis_label, snrs, schedulers,
			# 			 delay_avgs_by_snr_by_sched , delay_devs_by_snr_by_sched, 0. )

			if not ret:

				out_file = 'losses_snr_sched_bler_' + str(int(tb*100)) + "_ret_" + str(ret) + '.pdf'
				x_axis_label = 'SNR \ dB'
				y_axis_label = 'Block losses %'
				plot_figure( out_file, x_axis_label, y_axis_label, snrs, schedulers,
							 tb_losses_avgs_by_snr_by_sched , tb_losses_devs_by_snr_by_sched, tb )
	
				performance = []
				devs = []
				for i in range( len(tb_losses_devs_by_snr_by_sched) ):
					performance_aux = []
					devs_aux = []
					for j in range( len(tb_losses_devs_by_snr_by_sched[0]) ):
						performance_aux.append( (100. - tb_losses_avgs_by_snr_by_sched[i][j])**2 / nbr_RUs_avgs_by_snr_by_sched[i][j] )
						devs_aux.append(0.)
					performance.append(performance_aux)
					devs.append(devs_aux)

				out_file = 'performance_snr_sched_bler_' + str(int(tb*100)) + "_ret_" + str(ret) +'.pdf'
				x_axis_label = 'SNR \ dB'
				y_axis_label = 'Performance'
				plot_figure( out_file, x_axis_label, y_axis_label, snrs, schedulers,
							 performance , devs, 0. )
		

# Plot a barchart with error bar
def plot_figure( out_file, x_axis_label, y_axis_label, snrs,
				 schedulers, avgs_by_sched , devs_by_sched, 
				 targetBLER):

	plt.style.use('seaborn-darkgrid')
	plt.rcParams.update({'font.size': 15})
	plt.rcParams.update({"font.family": "Times New Roman"})
	
	fig = plt.figure()
	
	avgs_by_sched_trans = list(map(list, zip(*avgs_by_sched)))
	legends = []
	i = 0
	for s in schedulers:
		legends.append( s.getLabel() )
		i += 1
	df = pd.DataFrame(avgs_by_sched_trans, index=snrs, columns=legends)
	df.plot.bar(yerr=devs_by_sched, colormap='Reds', width=0.8, rot=0.);

	plt.xlabel(x_axis_label)
	plt.ylabel(y_axis_label)
	ymax = max(max(avgs_by_sched_trans))
	plt.ylim(0, ymax*1.25)
	plt.legend(	ncol=3, mode="expand", borderaxespad=0.)
	plt.tight_layout()
	plt.savefig(str(out_file))

	plt.close(fig)

if __name__ == '__main__':
	main()
