import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# plt.style.use('seaborn-darkgrid')
plt.rcParams.update({'font.size': 15})
plt.rcParams.update({"font.family": "Times New Roman"})

line_style = [ 'r:',  'r-.' , 'r--', 'r-' ]

# density
rho = np.array([50,350,1500,2272])
alpha = np.array(range(1,65))

# plots
fig, ax = plt.subplots()
fmin = 10000
fmax = 0
for i in range(0,4):
	f = np.sqrt( (10. * alpha ) / ( np.pi * rho[i] ) ) * 1000
	ax.plot(alpha, f, line_style[i], label=r'$\rho_{{HH}}$: {0}'.format(rho[i]), linewidth=2)
	if min(f) < fmin:
		fmin = min(f)
	if max(f) > fmax:
		fmax = max(f)


ax.set(xlabel=r'$\alpha$', ylabel='$Fp_t$ \ m')
ax.grid()
plt.legend()
plt.legend(loc='lower right')
plt.xlim(min(alpha),max(alpha))
plt.ylim(fmin,fmax)
plt.yscale('symlog')
# plt.xscale('log')
plt.tight_layout()
fig.savefig("footprint_vs_alpha.pdf")
plt.show()
