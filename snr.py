#Usage: calculate the SNR of a signal
#Date: MAY 31 2021
#Author: Jun ZHU
#Email: Jun__Zhu@outlook.com


from math import log10
import numpy as np


def SNR(
		trace,
		peak,
		win=3,
		tol=.5):
	"""The SNR is calculated by the ratio of standard deviations of two 3
	(optional) sec windows following and preceding the P arrival.
		params:
				1. trace
				2. peak
				3. win
				4. tol
		output: SNR
		see more: https://en.wikipedia.org/wiki/Signal-to-noise_ratio#Definition
	"""


	Mean = trace.data.mean()
	npeak = int(peak * trace.stats.sampling_rate)
	nwin = int(win * trace.stats.sampling_rate)
	#tolerance resilient to pick uncertainty
	ntol = int(tol * trace.stats.sampling_rate)
	noise_e = np.sum((trace.data[npeak-nwin-ntol: npeak-ntol] - Mean) ** 2)
	signal_e = np.sum((trace.data[npeak+ntol: npeak+nwin+ntol] - Mean) ** 2)
	return 10 * log10(signal_e / noise_e)


if __name__ == "__main__":
	from obspy import read
	from obspy.taup.tau_model import TauModel
	from obspy.taup import TauPyModel
	from obspy.taup.taup_create import build_taup_model
	import ttime


	stream = read("tmp/benchmark/*.sac")
	build_taup_model('tmp/SoCal.nd', output_folder='tmp/')
	model = TauPyModel()
	model.model = TauModel.from_file("tmp/SoCal.npz")
	#peaks in the trace (theoretical arrival - begining time)
	peaks = [ttime.tt(trace, model)-trace.stats.sac['b'] for trace in stream]
	snr = [SNR(trace, peaks[i]) for i,trace in enumerate(stream)]
	snr = np.array(snr)
	print(snr)
	print('mean',np.mean(snr),'max',np.max(snr),'min',np.min(snr),'std',np.std(snr))
