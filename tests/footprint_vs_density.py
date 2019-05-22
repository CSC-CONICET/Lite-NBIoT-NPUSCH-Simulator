import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# plt.style.use('seaborn-darkgrid')
plt.rcParams.update({'font.size': 15})

line_style = [ 'r:',  'r-.' , 'r--', 'r-' ]

# density
d = np.array(range(1,2273))

# plots
fig, ax = plt.subplots()
fmin = 10000
fmax = 0
for i in range(0,4):
	f = np.sqrt( (10. * 4**i ) / ( np.pi * d ) ) * 1000
	ax.plot(d, f, line_style[i], label=r'$\alpha$: {0}'.format(4**i), linewidth=2)

	if min(f) < fmin:
		fmin = min(f)
	if max(f) > fmax:
		fmax = max(f)


ax.set(xlabel=r'$\rho_{HH}$ \ HHs $km^{-2}$', ylabel='$Fp_t$ \ m')
ax.grid()
plt.legend()
plt.xticks([50,350,1500,2272],['RU:50','SU:350','U:1500','DU:2272'])
plt.xlim(min(d),max(d))
plt.ylim(fmin,fmax)
plt.yscale('symlog')
# plt.xscale('log')
plt.tight_layout()
fig.savefig("footprint_vs_density.pdf")
plt.show()
