import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
import matplotlib
import numpy as np
from matplotlib.ticker import OldScalarFormatter, ScalarFormatter
from matplotlib.lines import Line2D
import sys

rcParams.update({'figure.autolayout': True})


markers = []
for m in Line2D.markers:
	try:
		if len(m) == 1 and m != ' ':
			markers.append(m)
	except TypeError:
		pass

global_font = 22

# markers = markers[1:]
# markers[4] = markers[11]
# markers = ['o', 'D', '|']
# colors = ('r', 'b', 'g', 'c', 'm', 'y', 'k')
# colors = ('black', 'black', 'black', 'c', 'm', 'y', 'k')
colors = ('r', 'b', 'g', 'c', 'm', 'y', 'k', 'b')
t = np.arange(10, 205, 10)

def end2end_chart():

	N = 1
	g1 = [226.7]
	g2 = [18.9]
	g3 = [12.5]
	g4 = [8.1]
	g5 = [2.1]

	g6 = [16.6]
	g7 = [3.3]
	g8 = [1.6]
	g9 = [1.1]
	g10 = [0.5]
	groups_1 = [g1, g2, g3, g4, g5]
	groups_2 = [g6, g7, g8, g9, g10]
	labels = ('NO_OPT', 'RND', 'MAB', 'MAB+', 'COMB')
	colors = ('lightblue', 'steelblue', 'lightgreen', 'green', 'cadetblue', 'k', 'b')


	ind = 0.15 + 2 * np.arange(N)
	width = 0.35
	# init_space = 0.15

	fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
	ax1.set_title('Yelp', x=0.5, y=0.92, fontsize=20)
	ax2.set_title('News', x=0.5, y=0.92, fontsize=20)
	

	# fig, ax = plt.subplots()
	print ind

	rectss = []
	for idx, group in enumerate(groups_1):
		rects = ax1.bar(ind + idx * width, group, width, color=colors[idx], edgecolor = "none", log=True)
		autolabel(rects, ax1)
		rectss.append(rects)
	for idx, group in enumerate(groups_2):
		rects = ax2.bar(ind + idx * width, group, width, color=colors[idx], edgecolor = "none", log=True)
		autolabel(rects, ax2)
		# rectss.append(rects)
	# rects1 = ax.bar(ind, g1, width, color='r', edgecolor = "none")
	# rects2 = ax.bar(ind + width, g2, width, color='r', edgecolor = "none")
	# rects3 = ax.bar(ind + width * 2, g3, width, color='r', edgecolor = "none")
	# rects4 = ax.bar(ind + width * 3, g4, width, color='r', edgecolor = "none")
	# rects5 = ax.bar(ind + width * 4, g5, width, color='r', edgecolor = "none")

	# ax.legend((rects1, rects2, rects3, rects4, rects5), labels)
	plt.legend(rectss, labels, fontsize=12, loc='upper center', bbox_to_anchor=(-0.03, 1.1), ncol=5, fancybox=True, shadow=True)

	# rects = ax.bar(ind[idx] + idx * width, group, width, color=colors[idx], edgecolor = "none")

	# fig_size = plt.rcParams["figure.figsize"]
	# fig_size[0] = 10
	# fig_size[1] = 6
	# plt.rcParams["figure.figsize"] = fig_size
	# plt.subplots_adjust(top=0.8)

	# ax1 = fig.add_subplot(gs1[0])
	# ax2 = fig.add_subplot(gs1[1])

	plt.rc("font", size=17)
	# ax.spines['top'].set_visible(True)
	# ax.spines['top'].set_position('zero')

	# ax.spines['right'].set_visible(False)
	# ax.spines['bottom'].set_visible(False)
	# # ax.spines['bottom'].set_position('center')
	# ax.spines['left'].set_visible(True)
	# ax.ticklabel_format(style='', axis='y', scilimits=(0,0))
	# ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
	ax1.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))


	ax1.set_ylabel('latency (s)')

	ax1.tick_params(
	axis='x',          # changes apply to the x-axis
	which='both',      # both major and minor ticks are affected
	bottom='off',      # ticks along the bottom edge are off
	top='off',         # ticks along the top edge are off
	labelbottom='off')

	ax2.tick_params(
	axis='x',          # changes apply to the x-axis
	which='both',      # both major and minor ticks are affected
	bottom='off',      # ticks along the bottom edge are off
	top='off',         # ticks along the top edge are off
	labelbottom='off')
	# ax.set_xlabel('')
	# ax.set_title('Scores by group and gender')
	# ax1.set_xticks(ind + width)
	# ax.set_yscale("log")
	# ax.set_xticklabels(labels)

	# group_names = ('FULL', 'LEAF', 'GREEDY', 'UTILITY 2', 'UTILITY 4')
	# ax.legend(rectss, group_names, fontsize=14)
	ax1.grid(True)
	ax2.grid(True)
	plt.show()




def autolabel(rects, ax):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., 1.05*height,
                '%.1f' % float(height),
                ha='center', va='bottom')

def get_plt(ss, labels, tt, axis=[('', 'linear', False), ('', 'linear', False)]):
	fig = plt.figure()
	ax = fig.add_subplot(111)
	for idx, s in enumerate(ss):
		ax.plot(tt, s, '-' + markers[idx], color=colors[idx], markersize=10, label=labels[idx],  mew=1)
	
	plt.xlabel(axis[0][0])
	plt.ylabel(axis[1][0])

	plt.xscale(axis[0][1])
	plt.yscale(axis[1][1])

	if axis[0][2]:
		ax.xaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))
	if axis[1][2]:
		ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1e'))

	plt.rc("font", size=14)
	plt.legend(loc=0, fontsize=14)
	plt.grid(True)

	return plt, ax


def draw_chart(chart_name, curves):
	ss = []
	labels = []
	colors = ('r', 'g', 'c', 'm', 'y', 'k', 'b')
	markers = []
	for m in Line2D.markers:
		try:
			if len(m) == 1 and m != ' ':
				markers.append(m)
		except TypeError:
			pass

	ll = []
	ss1 = []
	ss2 = []

	start = 0
	end = -1
	
	# ll.append(([220], [1]))

	for curve in curves:
		x_dots = []
		y_dots = []
		for point in curve:
			x_dots.append(point[0])
			y_dots.append(point[1])
		ss1.append(x_dots[start:end])
		ss2.append(y_dots[start:end])


	ylim  = [0.6, 1]

	for idx, ts in enumerate(ss1):
		ll.append((ss1[idx], ss2[idx]))

	f, ax = plt.subplots()

	lines = ()
	for idx, x in enumerate(ll):
		l = []
		l.append(x[0])
		l.append(x[1])
		lines = lines + (ax.scatter(l[0], l[1], s=40, marker=markers[idx], color=colors[idx]),)
		# ax2.scatter(l[0], l[1], s=40, marker=markers[idx], color=colors[idx])
		ax.plot(l[0], l[1], color=colors[idx])
		# ax2.plot(l[0], l[1], color=colors[idx])

	plt.rc("font", size=19)
	ax.set_xscale("log")
	ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))
	ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))

	ax.legend(lines,
		   ('Full', 'Random', 'MAB', 'MAB+'),
		   scatterpoints=1,
		   loc=4,
		   ncol=2,
		   fontsize=18)

	# ax.ticklabel_format(style='plain', axis='x', offset=True)
	# ax.xaxis.set_major_formatter(ScalarFormatter(useMathText=True))

	ax.set_xlabel('Wallclock Time (s)')
	ax.set_ylabel('Average NDCG')
	
	ax.set_ylim(ymin=0.35, ymax=1.05)
	ax.set_xlim(xmin=0.3)
	

	ax.grid(True)

	# plt.gca().tight_layout()

	chart_file = '../../charts/' + chart_name + '.png'
	plt.savefig(chart_file)
	# plt.show()


def efficiency_charts():
	result_f = '../../efficiency_result.txt'
	factor = 0.2
	read_time_total = 220.0 * factor
	configs = {}

	dim_options = set()
	k_options = set()

	with open(result_f, 'r+') as f:
		first_line = True
		for line in f:
			if first_line:
				first_line = False
				continue
			elems = line.strip('\r\n').split('\t')
			sample_option = int(elems[0])
			dim = int(elems[1])
			k = int(elems[2])
			alpha = float(elems[3])
			run_time = float(elems[5])
			if sample_option == 3:
				run_time /= 5
			ndcg = float(elems[6])
			time = run_time + read_time_total * alpha + 0.3
			config = '_'.join([str(sample_option), str(dim), str(k)])
			dim_options.add(dim)
			k_options.add(k)
			if config not in configs:
				configs[config] = []
			configs[config].append((time, ndcg))

	for config in configs:
		configs[config] = sorted(configs[config], key=lambda pair : pair[0])

	for dim in [1, 5, 10]:
		for k in [5, 10, 20]:
			chart_name = 'dim_' + str(dim) + '_k_'+ str(k) 
			print chart_name
			curves = []
			for sample_option in [1, 2, 3]:
				config = '_'.join([str(sample_option), str(dim), str(k)])
				curves.append(configs[config])
			draw_chart(chart_name, curves)
			# sys.exit(1)

	# sort all the lines

def conc_chart():
	xs = [0, 1, 2, 3, 4, 5]
	topic_c = [0.693830747, 0.747037688, 0.78304411, 0.786254873, 0.78655, 0.78655]
	topic_ce = [0.734729761, 0.787554468, 0.795734271, 0.794511123, 0.794052442, 0.793975996]

	loc_c = [0.338354577, 0.360660487, 0.416998841, 0.426998841, 0.427, 0.427]
	loc_ce = [0.347263, 0.377172654, 0.413673233, 0.440511008, 0.4435, 0.4435]
	# k5s = [19, 25, 42, 50, 132, 200, 379, 915, 1176]
	# k10s = [24, 43, 74, 80, 191, 272, 566, 1390, 1861]
	# k20s = [39, 64, 117, 144, 271, 400, 963, 1930, 2356]
	# k5s = [1 - float(k5s[i])/alls[i] for i in range(0, len(xs))]
	# k10s = [1 - float(k10s[i])/alls[i] for i in range(0, len(xs))]
	# k20s = [1 - float(k20s[i])/alls[i] for i in range(0, len(xs))]

	ss1 = []
	labels = []

	T = xs

	# y_min = 0.68
	# y_max = 0.8
	# ss1.append(topic_c)
	# ss1.append(topic_ce)

	y_min = 0.33
	y_max = 0.45
	ss1.append(loc_c)
	ss1.append(loc_ce)
	
	
	# labels = ['FULL', 'LEAF', 'GREEDY', 'UTILITY 1', 'UTILITY 2', 'UTILITY 3', 'UTILITY 4', 'UTILITY 5']
	labels = ['JE+DF', 'Ours']


	axis = [('Number of Iterations', 'linear', False), ('Micro-F1', 'linear', False)]
	my_plt, ax = get_plt(ss1, labels, T, axis)
	my_plt.rc("font", size=26)
	ax.set_ylim(ymin=y_min, ymax=y_max)
	my_plt.legend(loc=0, fontsize=24)	
	ax.grid(True)

	my_plt.savefig('../charts/df_loc.png')


def expan_chart():
	xs = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
	expan_topic = [0.693830747, 0.696186071, 0.697516627, 0.722651173, 0.734729761, 0.609120098, 0.492913386]
	expan_loc = [0.338354577, 0.343173, 0.367263,0.328078818,0.293595,0.24044,0.124904]
	
	ss1 = []
	labels = []

	T = xs

	y_min = 0
	y_max = 0.9
	ss1.append(expan_topic)
	ss1.append(expan_loc)
	
	
	# labels = ['FULL', 'LEAF', 'GREEDY', 'UTILITY 1', 'UTILITY 2', 'UTILITY 3', 'UTILITY 4', 'UTILITY 5']
	labels = ['Topic Dim.', 'Loc Dim.']


	axis = [('Expansion Threshold', 'linear', True), ('Micro-F1', 'linear', False)]
	my_plt, ax = get_plt(ss1, labels, T, axis)
	my_plt.rc("font", size=26)
	ax.set_xticklabels(list(reversed(xs)))
	ax.set_ylim(ymin=y_min, ymax=y_max)
	my_plt.legend(loc=0, fontsize=24)	
	ax.grid(True)
	ax.invert_xaxis()

	my_plt.savefig('../charts/expan.png')
	



# conc_chart()
expan_chart()
# efficiency_charts()
# end2end_chart()

