
import numpy as np
import matplotlib.pyplot as plt
from random import randint
import random
from math import log10
import csv


class RadSched_FCMRSA:

	def __init__(self):
		self.label = "LUTS"
		self.BLER_updated_time = 0
		self.BLER_T = 320
		self.LUT = []
		self.last_BLER = -1

	def getLabel(self):
		return self.label

	def load_LUT(self,table):
		with open('../src/LUT/LUT1.csv', 'r') as f:
			next(f)
			reader = csv.reader(f)
			t = list(reader)
			for j in range(1,len(t)):
				table.append( [float(i) for i in t[j]] )
	
	def schedule( self, simulator):
	
		# Table: TBS,BLER,SNR,ITBS,NR,NRU
		if self.LUT == [] :
			self.load_LUT(self.LUT)

		curr_time = simulator.time[-1]

		# SNR estimation
		e = simulator.measured_SNR_error
		err = int(random.uniform(-e,e))
		estimated_SNR = simulator.snr + err
		if estimated_SNR > simulator.snr_max:
			estimated_SNR = simulator.snr_max
		elif estimated_SNR < simulator.snr_min:
			estimated_SNR = simulator.snr_min

		# Retrieve the row whose BLER and SNR values are
		# less or equal to BLER_{tol} and the estimated
		# SNR, respectively, with the addition of minimum
		# RU cost.

		i = 0
		i_min = -1
		nrus = float("inf")
		n = len(self.LUT)
		stop = False

		while i < n and not stop :

			if	self.LUT[i][0] == simulator.curr_TBS and \
				abs( estimated_SNR - self.LUT[i][1] ) < 0.1 :

				if i_min == -1 :
					i_min = i
					nrus = self.LUT[i_min][5]

				if	self.LUT[i][2] <= simulator.target_BLER and \
					self.LUT[i][5] < nrus :
					i_min = i
					nrus = self.LUT[i_min][5]

				if	self.LUT[i][2] > simulator.target_BLER :
					stop = True
					i -= 1

			i += 1

		ITBS = self.LUT[i_min][3]
		REP = self.LUT[i_min][4]

		return REP, ITBS, -1
