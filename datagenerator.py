#Usage: preprocess & generate datasets for CNN model
#Date: JUN 3 2021
#Author: Jun ZHU
#Email: Jun__Zhu@outlook.com


import os
import pickle
import numpy as np
from obspy import read
from obspy import UTCDateTime
import seis_routine
import config


def cut(
		stream,
		pick,
		window=35):
	"""cut a stream according to the pick
		pick: UTCDateTime of the begining of the window
		return:
			1. ENcomp: (boolean) whether EN component can be cut
				(in case that any EN-component recording is missing)
			2. wf (remove mean & normalized waveform)
	"""


	wf = []
	trace_std = []
	ENZcomp = True
	for trace in stream:
		n_start = int((pick - trace.stats.starttime) * trace.stats.sampling_rate)
		n_end = n_start + int(window * trace.stats.sampling_rate)
		#make sure 3 components coexist in the given window
		if n_start >= 0 and n_end < len(trace.data):
			wf.append(trace.data[n_start: n_end])
		else:
			ENZcomp = False
			break
	if ENZcomp:
		wf = np.array(wf)
		#normalized by maximum std of the traces
		wf /= np.max(np.std(wf, axis=1))
	return ENZcomp, wf


def dump(
		snr_thd,
		filelist,
		output,
		log,
		error=5):
	"""dump the waveform and corresponding ticks && record the waveform
		params:
				1. snr threshold
				2. file list
				3. output directory
				4. log the dump
				5. how many seconds you want to preserve before the pick
		output:
				1. four pickle files
				2. log of the dump
	"""


	with open(filelist, 'r') as f:
		data = [x.split() for x in f.readlines()[1:]]
		PATHs = [x[0] for x in data]
		EvIDs = [x[1] for x in data]
		LABELs = [x[19] for x in data]
		ARRs = [float(x[20]) for x in data]
		SNRs = [float(x[21]) for x in data]
		IDs = [x[22] for x in data]

	log_dump =  open(log, 'w')
	log_dump.write("path evid eventtype arr snr id\n")

	wf_pkl = []
	label_pkl = []
	ID_pkl = []
	EvID_pkl = []
	for i, path in enumerate(PATHs):
		if SNRs[i] < snr_thd:
			continue
		stream = read(path)
		if len(stream) < 3:
			continue
#		stream.detrend(); stream.taper(max_percentage=0.05)
		stream = seis_routine.Process(stream)
		pick = stream[2].stats.starttime + ARRs[i] - error
		ENZcomp, wf = cut(stream, pick)
		if ENZcomp:
			wf_pkl.append(wf)
			label_pkl.append(LABELs[i])
			ID_pkl.append(IDs[i])
			EvID_pkl.append(EvIDs[i])
			log_dump.write("%s %s %s %.4f %.4f %s\n"%(PATHs[i], EvIDs[i],
				LABELs[i], ARRs[i], SNRs[i], IDs[i]))
		print('YOU HAVE DUMPED %.2f%% RECORDINGS (%d)'%((i+1)/len(PATHs)*100,i+1))
	if not os.path.exists(output):
		os.makedirs(output)
	pickle.dump(np.array(wf_pkl), open(output+'wf.pkl', 'wb'))
	pickle.dump(np.array(label_pkl), open(output+'label.pkl', 'wb'))
	pickle.dump(np.array(ID_pkl), open(output+'id.pkl', 'wb'))
	pickle.dump(np.array(EvID_pkl), open(output+'eventid.pkl', 'wb'))
	return


if __name__ == "__main__":
	flist = config.QClist
	output = config.pkl_dir
	log = config.log_pkl
	thd = config.snr_thd
	dump(thd, flist, output, log, error=5)
	#test for dump
	f1 = 'label.pkl'
	f2 = 'wf.pkl'
	f3 = 'id.pkl'
	f4 = 'eventid.pkl'
	tick = pickle.load(open(output+f1, 'rb'))
	wf = pickle.load(open(output+f2, 'rb'))
	ID = pickle.load(open(output+f3, 'rb'))
	EvID = pickle.load(open(output+f4, 'rb'))
	print(tick.shape, wf.shape, ID.shape, EvID.shape)
