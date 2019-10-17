import numpy as np
import matplotlib.pyplot as plt
import random
from math import log10
import csv

# import inspect, os
# import sqlite3
# from threading import Thread, Event, Lock
# import matlab.engine
# import logging


class RadSchedSim:

	################################################################
	################################################################
	## Initialization
	################################################################
	################################################################

	def __init__(self):

		# Scheduling algorithm
		self.scheduler = -1

		# Retransmitions enable
		self.retransmit = -1

		# Input blocks
		self.nbr_of_TBs = -1
		self.TBSs = -1
		self.TB_ids = -1
		self.nbr_blocks = -1

		# Time
		self.time = -1

		# Transmisions (needed for stats)
		self.nbr_transmission = -1
		self.nbr_succ_TB_trans = -1

		# Repetitions		
		self.nbr_repetitions = -1
		self.HARQ_feedback = -1
		
		self.nbr_rep_max = -1
		self.nbr_rep_min = -1

		# ITBS level
		self.ITBS = -1
		self.ITBS_min = -1
		self.ITBS_max = -1

		# RU time
		self.RU_acum = -1
		self.RU_time = -1

		self.nbr_acks_acum = -1

		# ITBS vs TBS vs number of RU

		self.I_RU = [1, 2, 3, 4, 5, 6, 8, 10] # RU index -> Number of RU

		self.I_TBS = [0, 2, 1, 3, 4, 5, 6, 7, 8, 9, 10] # TBS index -> ITBS index

		# Table 16.5.1.2-2: Transport block size (TBS) table for NPUSCH.
		# LTE (Physical Layer) ts_136213v140400p
		self.ITBS_IRU_TBS =[
					[16, 32, 56, 88, 120, 152, 208, 256],
					[24, 56, 88, 144, 176, 208, 256, 344],
					[32, 72, 144, 176, 208, 256, 328, 424],
					[40, 104, 176, 208, 256, 328, 440, 568],
					[56, 120, 208, 256, 328, 408, 552, 680],
					[72, 144, 224, 328, 424, 504, 680, 872],
					[88, 176, 256, 392, 504, 600, 808, 1000],
					[104, 224, 328, 472, 584, 712, 1000, 1224],
					[120, 256, 392, 536, 680, 808, 1096, 1384],
					[136, 296, 456, 616, 776, 936, 1256, 1544],
					[144, 328, 504, 680, 872, 1000, 1384, 1736],
				]

		# BLER
		self.init_BLER = -1
		self.target_BLER = -1
		self.error_BLER = -1
		self.measured_BLER_error = -1
		self.BLER = -1
		self.BLER_CHANEL = -1

		# Chanel SNR
		self.SNR_t = -1
		self.snr = -1
		self.snr_min = -1
		self.snr_max = -1
		self.filtered_SNR_t = []
		self.LUT = []
		self.load_LUT(self.LUT)

		curr_TBS = -1
		curr_TB_id = -1


		
	def init(	self, scheduler, retransmit, 
				init_ITBS, init_nr, init_BLER, \
				target_BLER, error_BLER, \
				measured_BLER_error, TBSs, TB_ids, SNR_t):

		# Scheduling algorithm
		self.scheduler = scheduler

		# Retransmitions enable
		self.retransmit = retransmit

		# Input blocks
		self.nbr_of_TBs = len(TBSs)
		self.TBSs = TBSs
		self.TB_ids = TB_ids
		self.nbr_blocks = len(TBSs)

		# Time
		self.time = [0]

		# Transmisions (needed for stats)
		self.nbr_transmission = 0
		self.nbr_succ_TB_trans = 0

		# Repetitions		
		self.nbr_repetitions = [init_nr]
		self.HARQ_feedback = ['NACK']
		
		self.nbr_rep_max = 128
		self.nbr_rep_min = 1

		# ITBS level
		self.ITBS = [init_ITBS] # Initial ITBS level = 8 (for 256 bits)
		self.ITBS_min = 0 
		self.ITBS_max = 8

		# RU time
		self.RU_acum = [0]
		self.RU_time = 16 # ms for 3.75kHz tone

		self.nbr_acks_acum = [0]

		# BLER
		self.init_BLER = init_BLER
		self.target_BLER = target_BLER # %, Desirable BLER level
		self.error_BLER = error_BLER # target BLER tolerable error
		self.measured_BLER_error = measured_BLER_error # BLER error obtained when BLER is estimated
		self.BLER_CHANEL = [init_BLER] # Actual chanel BLER
		self.BLER = [] # BLER estimated by scheduler algorithm

		# Chanel SNR
		self.SNR_t = SNR_t
		self.snr = SNR_t[0]
		self.measured_SNR_error = 0
		self.snr_min = -30
		self.snr_max = 20
		self.filtered_SNR_t = [] # auxiliar variable

		curr_TBS = -1
		curr_TB_id = -1

		# rootdir="../src/NPUSCH-Simulator/"
		# logging.basicConfig(filename=os.path.join(rootdir,"sample.log"),
		# 					format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
		# 					datefmt='%m-%d %H:%M',
		# 					level=logging.INFO)
		# logging.getLogger().addHandler(logging.StreamHandler())
		# eng = matlab.engine.start_matlab( "-sd %s" % rootdir )


	def load_LUT(self,LUT):
		with open('../src/LUT/LUT2.csv', 'r') as f:
			reader = csv.reader(f)
			t = list(reader)
			for j in range(1,len(t)):
				LUT.append( [float(i) for i in t[j]] )


	################################################################
	################################################################
	## Simulation and calculations
	################################################################
	################################################################


	def simulate(self):

		curr_TB_id = -1

		curr_nbr_ret = 0

		curr_nbr_acks_acum = self.nbr_acks_acum[-1] 

		while len(self.TBSs) > 0:
			
			# Get TBS and TB id
			curr_TBS, curr_TB_id = self.getTBS()
			self.curr_TBS = curr_TBS
			self.curr_TB_id = curr_TB_id

			# Get number of needed RUs
			curr_RUs = self.getRUs(curr_TBS)

			# Calc. current repetition number, ITBS level and estimated BLER
			# Only update those values if no retransmission is required
			if( curr_nbr_ret == 0 ):
				curr_nbr_rep, curr_ITBS, curr_BLER = \
					self.scheduler.schedule(self)

			# Update number of repetitions
			self.nbr_repetitions.append(curr_nbr_rep)

			# Update ITBS level
			self.ITBS.append(curr_ITBS)

			# Update BLER estimated by the scheduling algorithm
			self.BLER.append(curr_BLER)

			# Update TB ids
			self.TB_ids.append(curr_TB_id)

			# Update HARQ_feedback (ACKs/NACKs)
			# It considers current chanel BLER
			curr_HARQ_feedback = self.getHARQFeedback()
			self.HARQ_feedback.append(curr_HARQ_feedback)

			# Update number of transmissions and number of successful transmissions
			if curr_HARQ_feedback == 'ACK':
				self.nbr_succ_TB_trans = self.nbr_succ_TB_trans + 1
				curr_nbr_ret = 0
			elif self.retransmit:
				curr_nbr_ret += 1
				self.TBSs.insert(0, curr_TBS )
				self.TB_ids.insert(0, curr_TB_id)
				#self.TB_ids.insert(0, 0) # self.TB_ids.insert(0, curr_TB_id) ??
				
			# Calculate chanel BLER for the next iteration
			curr_BLER_CHANEL = self.getBLER(self.snr,curr_TBS,curr_ITBS,
											curr_nbr_rep,curr_nbr_ret)
			self.BLER_CHANEL.append(curr_BLER_CHANEL)

			# Update SNR
			self.snr = self.SNR_t[self.nbr_transmission]
			self.filtered_SNR_t.append(self.snr)

			# Update time
			curr_time = self.time[-1] + self.RU_time * curr_nbr_rep * curr_RUs
			self.time.append(curr_time)

			# Update RUs acum. 
			curr_RUs_acum = self.RU_acum[-1] + curr_nbr_rep * curr_RUs
			self.RU_acum.append( curr_RUs_acum )

			# Update successful bits acum
			if curr_HARQ_feedback == 'ACK':
				curr_nbr_acks_acum = self.nbr_acks_acum[-1] + 1
			self.nbr_acks_acum.append( curr_nbr_acks_acum )

			# Update number of transmissions
			self.nbr_transmission += 1


		self.BLER.append(curr_BLER_CHANEL)

		self.filtered_SNR_t.append(self.snr)



	################################################################
	################################################################
	## Getters
	################################################################
	################################################################

	def getBLER(self, curr_SNR, curr_TBS, curr_ITBS, curr_nbr_rep, curr_nbr_ret):
		#################################################################
		# This function get BLER ( BLER = #NACKS / ( #NACKS + #ACKS ) )
		# from a table
		#################################################################

		if curr_nbr_ret == 0:
			effective_SNR =  curr_SNR
		else:
			effective_SNR =  curr_SNR + 10. * log10(curr_nbr_ret)
			
		i = 0
		n = len(self.LUT)
		
		while i < n and self.LUT[i][0] < effective_SNR :
			i += 1

		while i < n and self.LUT[i][1] < curr_TBS :
		 	i += 1
		
		while i < n and self.LUT[i][2] < curr_ITBS :
			i += 1

		while i < n and self.LUT[i][3] < curr_nbr_rep :
			i += 1

		#print(effective_SNR,curr_TBS,curr_ITBS,curr_nbr_rep)

		return self.LUT[i][4]


	def getTBS(self):

		# Get TBS to be send
		curr_TBS = self.TBSs.pop(0)
		curr_TBS_id = self.TB_ids.pop(0)

		# If the tranmission block size (TBS) is too big, split it
		# and update TBSs and TB_ids
		# curr_MSC_level = int(self.ITBS[-1])
		# curr_max_TBS = max(self.ITBS_IRU_TBS[curr_MSC_level])

		# if curr_TBS > curr_max_TBS:
		# 	curr_TBS_aux = curr_TBS
		# 	i = 0	
		# 	while curr_TBS_aux > curr_max_TBS:
		# 		curr_TBS_aux = curr_TBS_aux - curr_max_TBS
		# 		self.TBSs.insert(i,curr_max_TBS)
		# 		self.TB_ids.insert(i,curr_TBS_id)
		# 		i = i + 1
		# 	if curr_TBS_aux > 0:
		# 		self.TBSs.insert(i,curr_max_TBS)
		# 		self.TB_ids.insert(i,curr_TBS_id)
		# 	curr_TBS = self.TBSs.pop(0)
		# 	curr_TBS_id = self.TB_ids.pop(0)

		return curr_TBS, curr_TBS_id


	def getITBS(self):
		return int(self.ITBS[-1])

	def getNREP(self):
		return self.nbr_repetitions[-1]

	def getRUs(self, curr_TBS):
		################################################################
		# Calc. how many RUs are needed in order to send curr_TBS 
		################################################################
		i = 0

		curr_ITBS = int(self.ITBS[-1])
		n = len(self.ITBS_IRU_TBS[curr_ITBS])
		while i < n and self.ITBS_IRU_TBS[curr_ITBS][i] < curr_TBS:
			i = i + 1
		curr_RUs = self.I_RU[i]

		return curr_RUs

	def getHARQFeedback(self):
		#################################################################
		# Feedback signal gives information about
		# successful block arrival (ACK) or 
		# unsuccessful block arrival (NACK)
		#################################################################
		if random.uniform(0,1) > self.BLER_CHANEL[-1]:
			curr_HARQ_feedback = 'ACK'
		else:
			curr_HARQ_feedback = 'NACK'
		return curr_HARQ_feedback

		# if self.curr_ITBS == 1:
		# 	IMCS = 2
		# elif self.curr_ITBS == 2:
		# 	IMCS = 1
		# else:
		# 	IMCS = self.curr_ITBS
		
		# n = self.ITBS_IRU_TBS[self.curr_ITBS][0]
		# j = 0
		# while j < n and self.ITBS_IRU_TBS[self.curr_ITBS][j] != 256:
		# 	j = j + 1
		# if self.ITBS_IRU_TBS[self.curr_ITBS][j] == 256:
		# 	IRU = j
		# else:
		# 	IRU = -1

		# IREP = self.curr_nbr_rep
		# SNR = self.SNR_t[-1]
		# MONO = 1
		# result=eng.pysimu(IMCS,IRU,IREP,SNR,MONO)

		# if result['bler'] == 1:
		# 	curr_HARQ_feedback = 'ACK'
		# else:
		# 	curr_HARQ_feedback = 'NACK'
		# return curr_HARQ_feedback


	def getFinalTime(self):
		return self.time[-1]

	def getNbrRUs(self):
		return self.RU_acum[-1]

	def getNbrTransmission(self):
		return self.nbr_transmission

	def getTBLoss(self):
		return ( self.nbr_blocks - self.nbr_succ_TB_trans ) / self.nbr_blocks * 100


	################################################################
	################################################################
	## Prints, plots and savings
	################################################################
	################################################################

	def print_results(self):
		print('Total time:', self.getFinalTime(), "ms")
		print('Total resource units:', self.getNbrRUs())
		print('Total TB loss:', self.getTBLoss(), "%")
		print('Total number of transmissions:', self.getNbrTransmission())


	def plot_results(self,out_file):

		plt.style.use('seaborn-dark')

		plt.rcParams.update({'font.size': 15})
		plt.rcParams.update({"font.family": "Times New Roman"})

		RU_acum_min = self.RU_acum[0] 
		RU_acum_max = self.RU_acum[-1]
		h = [0, 1]

		if not self.retransmit:
			RU_acum_max = 3500
			self.nbr_blocks = 5
		else:
			RU_acum_max = 8000

		i_max = 0
		while i_max < len(self.RU_acum) and self.RU_acum[i_max] < RU_acum_max :
				i_max = i_max + 1
		i_max = i_max - 1


		if not self.retransmit:
			i_max = 3
		else:
			i_max = 8
		


		fig = plt.figure()

		n = 4

		color = 'Red'

		id_subplot = n * 100 + 11
		ax = plt.subplot(id_subplot)
		plt.plot(self.RU_acum, self.ITBS, 'r--')
		plt.scatter(self.RU_acum, self.ITBS, c=color, alpha=0.3)
		plt.ylabel("I$_{TBS}$", rotation=0, ha='right')
		plt.xlabel('No. of transfers')
		iterations = list(range(len(self.RU_acum)))
		plt.xticks(self.RU_acum, iterations)
		plt.yticks([self.ITBS_min,self.ITBS_max])
		plt.xlim(RU_acum_min,RU_acum_max)
		plt.ylim(self.ITBS_min-1,self.ITBS_max+1)
		ax.xaxis.tick_top()
		ax.xaxis.set_label_position('top')

		id_subplot += 1
		ax = plt.subplot(id_subplot)
		plt.plot(self.RU_acum, self.nbr_repetitions, 'r--')
		plt.scatter(self.RU_acum, self.nbr_repetitions, c=color, alpha=0.3)
		plt.ylabel('NR', rotation=0, ha='right')
		plt.ylim(-1,self.nbr_rep_max+10)
		plt.xlim(RU_acum_min,RU_acum_max)
		plt.yticks([self.nbr_rep_min,self.nbr_rep_max])
		plt.xticks([], [])

		id_subplot += 1
		plt.subplot(id_subplot)
		plt.plot(self.RU_acum, self.BLER_CHANEL, 'r--')
		plt.scatter(self.RU_acum, self.BLER_CHANEL, c=color, alpha=0.3)
		plt.ylabel('BLER', rotation=0, ha='right')
		plt.ylim(-0.1,1.1)
		plt.xlim(RU_acum_min,RU_acum_max)
		plt.yticks([0,1])
		plt.xticks([], [])
		
		id_subplot += 1
		ax = plt.subplot(id_subplot)
		#plt.plot(self.RU_acum, self.nbr_acks_acum, 'r--')
		ax.fill_between(self.RU_acum, 0,self.nbr_acks_acum, facecolor="red", alpha=.3)
		plt.scatter(self.RU_acum, self.nbr_acks_acum, c=color, alpha=0.3)
		plt.ylabel('Succ.\narrivals', rotation=0, ha='right')
		plt.xlabel('NPUSCH resource usage \ RUs')
		#plt.ylim(-2,self.nbr_blocks+2)
		plt.ylim(0,i_max)
		plt.xlim(RU_acum_min,RU_acum_max)
		#plt.yticks([0,self.nbr_blocks])
		plt.yticks([0,i_max])

		# id_subplot += 1
		# ax = plt.subplot(id_subplot)
		# X, Y = np.meshgrid(self.RU_acum, h)

		# plt.pcolor(X,Y,[self.TB_ids], cmap='Spectral')
		# plt.ylabel('TB Ids', rotation=0, ha='right')
		# plt.xlabel('NPUSCH resource usage \ RUs')
		# plt.xlim(RU_acum_min,RU_acum_max)
		# plt.yticks([], [])

		i = 1
		while i < len(self.TB_ids):
			if self.TB_ids[i-1] != self.TB_ids[i] and self.RU_acum[i] <= RU_acum_max :
				ax.axvline(x=self.RU_acum[i], ymin=0, ymax=4.55, c='gray', 
				lw=1, zorder=1000, clip_on=False)
			i = i + 1
		
		if self.scheduler.getLabel() != 'ITBS-NR' or not self.retransmit:
			i = 1
			while i < len(self.BLER_CHANEL) and self.BLER_CHANEL[i] > 0.05 :
				i = i + 1
			if i < len(self.BLER_CHANEL):
				ax.axvline(x=self.RU_acum[i], ymin=0, ymax=4.55, c='k', lw=3,
				 zorder=1000, clip_on=False)


		fig.set_size_inches(10, 5)
		plt.tight_layout()
		plt.subplots_adjust(wspace=0, hspace=0.18)
		plt.savefig(out_file, dpi=500)
		plt.close(fig)
