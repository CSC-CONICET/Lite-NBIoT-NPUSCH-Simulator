import sys
sys.path.append('../src')
from RadSchedSim import RadSchedSim

from RadSchedSim import RadSchedSim
from RadSched_ITBS_and_Rep import RadSched_ITBS_and_Rep
from RadSched_ITBS_Rep import RadSched_ITBS_Rep
from RadSched_Rep_ITBS import RadSched_Rep_ITBS
from RadSched_Rep import RadSched_Rep
from RadSched_ITBS import RadSched_ITBS
from RadSched_FCMRSA import RadSched_FCMRSA

#############################################################
## MAIN-SINGLE-SIM
#############################################################


#scheduler = RadSched_ITBS_and_Rep()
#scheduler = RadSched_ITBS_Rep()
#scheduler = RadSched_Rep_ITBS()
#scheduler = RadSched_Rep()
#scheduler = RadSched_ITBS()
#scheduler =  RadSched_NBLA()
scheduler = RadSched_FCMRSA()

retransmit = False

init_BLER = 1
target_BLER = 0.
error_BLER = 0.0 # 0.03
measured_BLER_error = 0.0 # 0.25

nbr_of_blocks = 20
TBSs = [256] * nbr_of_blocks
TB_ids = list(range(10,nbr_of_blocks+10))

SNR_t = [-27] * len(TB_ids) * 1280

sim = RadSchedSim()

sim.init(	scheduler, retransmit, init_BLER, target_BLER, error_BLER, \
			measured_BLER_error, TBSs, TB_ids, SNR_t)
sim.simulate()
sim.plot_results(	"SimpleTest_" + str(scheduler.getLabel()) + "_targetBLER_" 
					+ str(int(target_BLER*100)) + "_ret_" + str(retransmit) + ".pdf")
sim.print_results()
