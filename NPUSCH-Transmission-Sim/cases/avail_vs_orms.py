import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# plt.style.use('seaborn-darkgrid')
plt.rcParams.update({'font.size': 15})
plt.rcParams.update({"font.family": "Times New Roman"})

line_style = [ 'r:',  'r-.' , 'r--', 'r-' ]

# density
n_orms = np.array(range(1,10))
alpha = np.array([1,2,4,8])

# plots
fig, ax = plt.subplots()
for i in range(len(alpha)):
	n_avail_rus = 10000 - n_orms * 1024 / alpha[i] 
	for j in range(len(n_avail_rus)):
		if 10000 - n_avail_rus[j] < 1024:
			n_avail_rus[j] = 10000 - 1024
	ax.plot(n_orms, n_avail_rus, line_style[i],label=r'$\alpha$: {0}'.format(alpha[i]), linewidth=2)

ax.set(xlabel='N. of ORMs', ylabel='Available RUs')
ax.grid()
plt.legend(loc='lower left')
plt.xlim(min(n_orms),max(n_orms))
plt.ylim(0,10000)
plt.tight_layout()
fig.savefig("avail_vs_orms.pdf")
plt.show()
