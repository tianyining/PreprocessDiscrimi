#Usage: plot the phase picking with a zoom-in
#Date: JUN 1 2021
#Author: Jun ZHU
#Email: Jun__Zhu@outlook.com


import os
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import (
				inset_axes,
				zoomed_inset_axes,
				mark_inset)
import numpy as np
from obspy import read
import seis_routine


def plot(
		trace,
		arr_b,
		snr,
		Xarr_b = -1,
		output="tmp/image/"):
	"""plot and save the figure of picking
		params:
				1. trace
				2. arr_b = (picking arrival - begining time)
				3. snr
				4. Xarr_b, a custom type of arrival time
				5. output folder of your images
		notes:
				1. the o_time and b_time must have been encoded
	"""


	plt.switch_backend('agg')
	trace.normalize()
	#shift
	shift = trace.stats.sac['o'] - trace.stats.sac['b']
	sample_rate = trace.stats.sampling_rate
	t = np.arange(len(trace.data)) / sample_rate - shift
	#(arrival time - origin time)
	arr_o = arr_b - shift
	#configurations of inset
	onset = 0.3 #0.3 second as the onset of the pick
	inset_duration = 1 #1 seconds inset
	n_onset = int((shift + arr_o - onset)*sample_rate)
	t_inset = np.arange(int(inset_duration*sample_rate)) / sample_rate + (arr_o - onset)
	#major figure
	fig = plt.figure()
	name = "_".join(("snr", "%.2f"%snr, "evid",	str(trace.stats.sac['nevid']),
		trace.stats.network, trace.stats.station,trace.stats.channel))
	ax0 = fig.add_subplot(1,1,1)
	ax0.set_title(name)
	ax0.plot(t, trace.data, 'gray', lw=0.5, alpha=0.5)
	ax0.axvline(x=0, color='gray', lw=1, ls='-')
	ax0.axvline(x=arr_o, color='r', lw=1, ls='-', label='STA/LTA')
	if Xarr_b!=-1:
		Xarr_o = Xarr_b - shift
		ax0.axvline(x=Xarr_o, color='b', lw=1, ls='-', label='theoretical')
		ax0.text(Xarr_o, 0.9*min(trace.data), "dt: %.2f"%(Xarr_b - arr_b))
	#enlong the height of the figure to 1.2 times max_amplitude 
	ax0.set_ylim([min(trace.data), 1.2*max(trace.data)])
	ax0.set_xlabel("Time/s")
	ax0.set_ylabel("Normalized Amplitude")
	ax0.set_xticks([0,35])
	ax0.set_xticklabels(["origin","35"])
	ax0.set_yticks([-0.5,0,0.5])
	ax0.set_yticklabels(["-0.5","0","0.5"])
	ax0.legend(loc='upper left')
	#zoom-in inset
	#avoid out of index
	if len(trace.data) > n_onset+len(t_inset):
		ax1 = inset_axes(ax0, width="30%", height="40%", loc="upper right")
		ax1.plot(t_inset, trace.data[n_onset: n_onset+len(t_inset)], c='black',
	lw=1, alpha=.9)
		ax1.axvline(x=arr_o, color='red', lw=1.5, ls='-')
		ax1.set_xticks([arr_o])
		ax1.set_xticklabels(["pick"+" %.1f s"%arr_o])
		ax1.set_yticks([0])
	#save the figure
	fname = output + name + ".png"
	if not os.path.isdir(output):
		os.makedirs(output)
	plt.savefig(fname, dpi=500)
	plt.close()
	return


if __name__ == "__main__":
	#read the trace
	trace = read("tmp/benchmark/*.sac")[-1]
	trace = seis_routine.Process(trace)
	plot(trace,30,-1,Xarr_b=32)
