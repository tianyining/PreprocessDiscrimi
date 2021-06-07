#Usage: log the SNR and arrival time of the file list
#Date: JUN 6 2021
#Author: Jun ZHU
#Email: Jun__Zhu@outlook.com


import os
from obspy.taup.tau_model import TauModel
from obspy.taup import TauPyModel
from obspy.taup.taup_create import build_taup_model
from obspy import read
import config
import ttime, stalta, snr, show_picking, seis_routine


def ArrivalSnr(
				filelist,
				velocitymodel,
				outputQC,
				if_plot=False,
				imagepath='../../image/preview/'):
	"""log the arrival & SNR of the filelist
		notes:
			make sure that origin time has been encoded in the SAC file
	"""


	with open(filelist, 'r') as f:
		data = [x.split() for x in f.readlines()[1:]]
		path = [x[0] for x in data]
		evla = [x[4] for x in data]
		evlo = [x[5] for x in data]
		evdp = [x[6] for x in data]
		stla = [x[13] for x in data]
		stlo = [x[14] for x in data]
		stdp = [x[16] for x in data]

	# generate velocity model
	if not os.path.exists('tmp'):
		os.makedirs('tmp')
	build_taup_model(velocitymodel, output_folder="tmp/")
	Taupmodel = TauPyModel()
	npzfname = velocitymodel.split("/")[-1].split(".")[0] + ".npz"
	Taupmodel.model = TauModel.from_file("tmp/" + npzfname)

	# log the SNR &  arrival
	QC_traces = open(outputQC, "w")
	QC_traces.write("%s       %s         %s\n"%("arr", "SNR", "fpath"))
	for i,x in enumerate(path):
#	for i,x in enumerate(path[-1000:]):
#		i += -1000
		# read the Z-component trace and routinely process the data
		trace = seis_routine.Process(read(x)[0])
		# shift from o_time to b_time
		shift = trace.stats.sac['o'] - trace.stats.sac['b']
		# theoretical arrival time
		predict = ttime.tt(trace, Taupmodel)
		# in case of overflow
		tolerance = 5
		if predict > trace.stats.sac['e'] - trace.stats.sac['o'] - tolerance:
			continue
		if predict < trace.stats.sac['b'] - trace.stats.sac['o'] + tolerance:
			continue
		try:
			arr, quality = stalta.stalta(trace, predict)
		except:
			print(x, predict, "can't calculate stalta")
		SNR = snr.SNR(trace, arr)
		if str(SNR)=="nan":
			print(x, predict, "SNR == 'nan'")
			continue
		QC_traces.write("%.3f %.3f %s\n"%(arr, SNR, x))
		if if_plot:
			Xarr_b = predict + shift
			show_picking.plot(trace, arr, SNR, Xarr_b=Xarr_b, output=imagepath)
	QC_traces.close()
	return


if __name__ == "__main__":
	import config
	flist = config.filelist
	velofpath = config.velocity_model
	QCfpath = config.outputQC
	imagepath = config.plot_blast
	ArrivalSnr(
				flist, #waveform data file list
				velofpath,
				QCfpath, #path to save calculated QC
				if_plot=False, #whether plot the picking
				imagepath=imagepath, #path to save the images
				)
