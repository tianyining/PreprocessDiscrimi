#Usage: pick maximum STA/LTA around the theoretical travel time
#Author: Jun ZHU
#Email: Jun__Zhu@outlook.com


from obspy.signal.trigger import recursive_sta_lta
import numpy as np


def stalta(
			trace,
			predict,
			error=3,
			nsta=40,
			nlta=400):
	"""pick the P wave && pick quality
		params:
				1. trace
				2. theoretical travel time (unit: sec)
				3. error: tolerance time
				3. nsta, nlta
		output: 1. arr_b (arrival time - b_time)
		notes:
				1. predict time must be less than endtime of the file
				2. predict time must be larger than error time
	"""
	stalta = recursive_sta_lta(trace.data, nsta, nlta)
	shift = trace.stats.sac['o'] - trace.stats.sac['b']
	n_predict = int((shift + predict) * trace.stats.sampling_rate)
	n_tol = int(error * trace.stats.sampling_rate)
	n_diff_max = np.argmax(np.diff(stalta[n_predict - n_tol:n_predict + n_tol]))
	n_pick = n_predict - n_tol + n_diff_max
	#arrival time in the trace
	arr_b = n_pick / trace.stats.sampling_rate
	quality = max(stalta[n_predict - n_tol:n_predict + n_tol])
	return arr_b, quality


if __name__ == "__main__":
	from obspy import read
	import show_picking, ttime
	from obspy.taup.tau_model import TauModel
	from obspy.taup import TauPyModel
	from obspy.taup.taup_create import build_taup_model


	stream = read("tmp/benchmark/*.sac")
	stream.detrend()
	stream.taper(max_percentage=0.05)
	stream.filter('bandpass', freqmin=1, freqmax=15, corners=2, zerophase=True)
	shift = [trace.stats.sac['o'] - trace.stats.sac['b'] for trace in stream]
	manualtt = [trace.stats.sac['a'] for trace in stream]
	stalta = [stalta(trace, manualtt[i])[0] for i,trace in enumerate(stream)]

	print((np.array(shift)+np.array(manualtt)-np.array(stalta))*40)
	plot_manual = [trace.stats.sac['a']-trace.stats.sac['b'] for trace in stream]

	build_taup_model('tmp/SoCal.nd', output_folder='tmp/')
	model = TauPyModel()
	model.model = TauModel.from_file("tmp/SoCal.npz")
	peaks = [ttime.tt(trace,model) for trace in stream]
#	stalta = [stalta(trace,peaks[i],error=1)[0] for i,trace in enumerate(stream)]
#	plot_peaks = [peaks[i]-trace.stats.sac['b'] for i,trace in enumerate(stream)]

	#show picking performance
#	for i,trace in enumerate(stream):
#		show_picking.plot(trace, stalta[i], -1, plot_manual[i])
