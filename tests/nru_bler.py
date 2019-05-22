import matplotlib.pyplot as plt
from collections import OrderedDict
from math import log10
import csv

#plt.style.use('fivethirtyeight')
plt.style.use('seaborn-darkgrid')
plt.rcParams.update({'font.size': 13})

line_style = [ 'r-', 'r--' , 'r-.' , 'r:', 'r-' ]
#snrs = [-24,-22,-20,-18,-16]
snrs = [-24,-20,-16]
comm_overhead = 0.012
comm_init_overhead = 3 * 0.012
ru_time = 0.008

##################################################
# Load LUT: tbs,snr,bler,itbs,nr,nru
##################################################
LUT = []
with open('../src/LUT/LUT1.csv', 'r') as f:
	reader = csv.reader(f)
	t = list(reader)
	for j in range(1,len(t)):
		LUT.append( [float(i) for i in t[j]] )


##################################################
# Non retransmission
##################################################

	# Calculate NRU vs BLER for different SNRs
	
	b_result = []
	n_result = []
	l_result = []
	
	blers = [x * .1 for x in range(11)]

	for tbs in [256]:

		for snr in snrs:

			bler_result = []
			nru_result = []
			lat_result = []

			n = len( LUT )
			for i in range(n) :
				if LUT[i][0] == tbs and LUT[i][1] == snr:
					bler_result.append( LUT[i][2] * 100 )
					nru_result.append( LUT[i][5] )
					lat_result.append( LUT[i][5] * ru_time + comm_overhead + comm_init_overhead )

			b_result.append(bler_result)
			n_result.append(nru_result)
			l_result.append(lat_result)

	# Plot graphics

	fig = plt.figure()
	fig.set_size_inches(8, 4)

	n = len(n_result)

	for i in range(n):
		plt.plot(b_result[i],n_result[i],line_style[i],label="SNR {0} dB".format(snrs[i]), linewidth=1.5)
		plt.scatter(b_result[i], n_result[i], c='r', s=70, alpha=0.3)
		
		#print( 'Non-retransmission, SNR:', snrs[i], ', nru-decrease:', 100 - n_result[i][1] * 100 / n_result[i][0])
		# l = 0
		# while b_result[i][l] < 4 : 
		# 	print( b_result[i][l] , n_result[i][l] )
		# 	l += 1

	legend = plt.legend(loc='upper right', ncol=3)
	plt.ylabel('NPUSCH resource usage \ RUs')
	plt.xlabel('% block losses')
	plt.ylim(100,1500) 
	plt.xlim(-1,30)
	#plt.yscale('log')
	plt.tight_layout()
	plt.savefig("nru_bler_nonret.pdf", dpi=500)
	plt.close()

	# n = len(n_result)
	# for i in range(n):
	# 	plt.plot(b_result[i],l_result[i], line_style[i],label="SNR {0} dB".format(snrs[i]), linewidth=1.5)
	# 	plt.scatter(b_result[i],l_result[i], c='r', s=70, alpha=0.3)
	# plt.legend()
	# plt.ylabel('Delay \ s')
	# plt.xlabel('BLER')
	# plt.ylim(0,12) 
	# plt.xlim(-1,105)
	# plt.tight_layout()
	# plt.savefig("del_bler_nonret.pdf", dpi=500)
	# plt.close()


##################################################
# Retransmission
##################################################


	# Calculate NRU vs BLER for different SNRs
	
	b_result = []
	n_result = []
	r_result = []
	l_result = []

	for tbs_base in [256]:

		for snr_base in snrs:

			# Calc. BLERS
			n = len( LUT )
			blers = []
			for i in range(n) :
				if LUT[i][0] == tbs_base and LUT[i][1] == snr_base:
					blers.append( LUT[i][2] )
			blers = list(OrderedDict.fromkeys(blers))
					
			# Calc. 
			bler_result = []
			nru_result = []
			ret_result = []
			lat_result = []

			for bler_base in blers:

				n = len( LUT )
				ret = 1
				snr_e = snr_base
				p = 1
				expect_nru = 0
				expect_lat = 0
				nru_base = 0 
				bler_i = 9999

				i = 0
				while tbs_base != LUT[i][0] or snr_e != LUT[i][1] or bler_base != LUT[i][2]:
					i = i + 1

				itbs_base = LUT[i][3]
				nr_base = LUT[i][4]

				while i < n and bler_i > 0:

					if 	tbs_base == LUT[i][0] and ( abs( LUT[i][1] - snr_e )  <= 0.5 ) and \
						itbs_base == LUT[i][3] and nr_base ==  LUT[i][4]:

						if nru_base == 0 :
							nru_base = LUT[i][5]
							bler_i = bler_base
							p = 1
						else:
							p = p * bler_i
							bler_i = LUT[i][2]

						expect_nru = expect_nru + ret * nru_base * p * ( 1. - bler_i )
						expect_lat = expect_lat + ret * ( nru_base * ru_time + comm_overhead ) * p * ( 1. - bler_i )

						# if snr_base == -27. and bler_base == 1.:
						# 	print(	"snr_base:",snr_base,"snr_e:", snr_e, ", bler_base:",bler_base, \
						# 			"bler_i", bler_i,", LUT: ",LUT[i])

						ret = ret + 1

						snr_e = snr_base + 10 * log10(ret)

					else:

						i = i + 1

										
				bler_result.append( bler_base * 100)
				nru_result.append( expect_nru )
				lat_result.append( expect_lat )
				ret_result.append( ret )

			b_result.append(bler_result)
			n_result.append(nru_result)
			l_result.append(lat_result)
			r_result.append(ret_result)


	# Plot graphics

	fig = plt.figure()
	fig.set_size_inches(8, 4)
	
	n = len(n_result)
	for i in range(n):
		plt.plot(b_result[i],n_result[i], line_style[i], label="SNR: {0} dB".format(snrs[i]), linewidth=1.5)
		plt.scatter(b_result[i], n_result[i], c='r', s=70, alpha=0.3)
		#print( 'Retransmission, SNR:', snrs[i], ', nru-decrease:', 100 - n_result[i][1] * 100 / n_result[i][0])
		#l = 0
		#while b_result[i][l] < 4 : 
		#	print( b_result[i][l] , n_result[i][l] )
		# 	l += 1


	plt.legend(loc='upper right', ncol=3)
	plt.ylabel('NPUSCH resource usage \ RUs')
	plt.xlabel('% block losses')
	plt.ylim(0,1800) 
	plt.xlim(-1,30) 
	plt.tight_layout()
	plt.savefig("nru_bler_ret.pdf", dpi=500)
	plt.close()

	# n = len(l_result)
	# for i in range(n):
	# 	plt.plot(b_result[i],l_result[i], line_style[i], label="TBS: 256 bits, SNR: {0} dB".format(snrs[i]), linewidth=1.5)
	# 	plt.scatter(b_result[i],l_result[i], c='r', s=70, alpha=0.3)
	# plt.legend(loc='upper left')
	# # plt.legend()
	# plt.ylabel('Delay \ s')
	# plt.xlabel('BLER')
	# plt.ylim(0,30) 
	# plt.xlim(-1,30) 
	# plt.tight_layout()
	# plt.savefig("del_bler_ret.pdf", dpi=500)
	# plt.close()

	n = len(r_result)
	for i in range(n):
		plt.plot(b_result[i],r_result[i], line_style[i], label="TBS: 256 bits, SNR: {0} dB".format(snrs[i]), linewidth=1.5)
		plt.scatter(b_result[i], r_result[i], c='r', s=70, alpha=0.3)
	
	plt.legend(loc='upper left')
	plt.ylabel('Number of retransmissions')
	plt.xlabel('BLER')
	plt.ylim(1,4)
	plt.xlim(-1,30) 
	plt.tight_layout()
	plt.savefig("nret_bler_ret.pdf", dpi=500)
	plt.close()
