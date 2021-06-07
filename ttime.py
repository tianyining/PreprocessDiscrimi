#Usage: first arrival travel time calculation based on taup
#Date: MAY 31 2021
#Author: Jun ZHU
#Email: Jun__Zhu@outlook.com


def tt(trace, model):
	"""calculate travel time of the fisrt arrival
		params:
				1. trace data in SAC format ('gcarc' and 'evdp' are required);
				2. your custom model
		output:
				1. travel time of the first arrival
		notes:
				1. If DEPTH of the event is less than 0 km, we set it to 0
				2. velocity model (TauPyModel class) is pre-defined;
	"""


	gcarc = trace.stats.sac['gcarc']
	#set depth to zero if it is less than 0
	dp = 0 if trace.stats.sac['evdp'] < 0 else trace.stats.sac['evdp']
	arr = model.get_travel_times(
								source_depth_in_km=dp,
								distance_in_degree=gcarc)
	return arr[0].time


if __name__ == "__main__":
	from obspy.taup.tau_model import TauModel
	from obspy.taup import TauPyModel
	from obspy.taup.taup_create import build_taup_model
	from obspy import read
	import numpy as np


	#build custom velocity model from a file with '.nd' extension
	build_taup_model('tmp/SoCal.nd', output_folder='tmp/')
	#generate a TayPyModel class
	Taupmodel = TauPyModel()
	#assign your custom velocity model to the TauPyModel's attribute
	Taupmodel.model = TauModel.from_file("tmp/SoCal.npz")
	#read stream
	stream = read('tmp/benchmark/*.sac')
	#calculate tt for each trace in the stream
	ttimes = [tt(trace, Taupmodel) for trace in stream]
	#read the manual picking arrival time of each trace
	manualtt = [x.stats.sac['a']-x.stats.sac['o'] for x in stream]
	#compare the difference
	diff = np.array(ttimes)-np.array(manualtt)
	absdiff = np.abs(diff)
	print(diff)
	print('absolute diff:\nmean',np.mean(absdiff),'max',np.max(absdiff),'min',np.min(absdiff),'std',np.std(absdiff))
	print('diff:\nmean',np.mean(diff),'max',np.max(diff),'min',np.min(diff),'std',np.std(diff))
