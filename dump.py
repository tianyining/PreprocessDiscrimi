import pickle
import numpy as np
import seis_routine
from obspy import read
from obspy import UTCDateTime
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
			2. wf: normalized (by std of the stream !!!) waveform
	"""
	wf = []
	trace_std = []
	ENZcomp = True
	for trace in stream:
		n_start = int((pick - trace.stats.starttime) * trace.stats.sampling_rate)
		n_end = n_start + int(window * trace.stats.sampling_rate)
		#make sure all channels coexist in the window
		if n_start >= 0 and n_end < len(trace.data):
			wf.append(trace.data[n_start:n_end])
		else:
			ENZcomp = False
			break
	if ENZcomp:
		wf = np.array(wf)
		#normalized by maximum std of the traces
		wf /= np.max(np.std(wf, axis=1))
	return ENZcomp, wf


def dump(
		filelist,
		output,
		error=3):
	"""dump the waveform and corresponding ticks && record the waveform
		params:
			filelist
			output
			error
		output:
			four pkl files
			wf.pkl
			tick.pkl
			id.pkl
			eventid.pkl
	"""
	with open(filelist, 'r') as f:
		data = [x.split() for x in f.readlines()[1:]]
		IDs = [x[22] for x in data]
		TICKs = [x[19] for x in data]
		ARRs = [float(x[20]) for x in data]
		PATHs = [x[0] for x in data]
		EvIDs = [x[1] for x in data]
	wf_pkl = []
	tick_pkl = []
	ID_pkl = []
	EvID_pkl = []
	for i,path in enumerate(PATHs):
		stream = seis_routine.Process(read(path))
		#!!! CHECK WHETER THE ALL ENZ COMPONENTS EXISTS
		#if False, just skip it
		if len(stream) < 3:
			continue
		pick = stream[2].stats.starttime + ARRs[i] - error
#		print(pick, IDs[i], TICKs[i], ARRs[i], PATHs[i], EvIDs[i])
		ENZcomp, wf = cut(stream, pick)
		if ENZcomp:
			wf_pkl.append(wf)
			tick_pkl.append(TICKs[i])
			ID_pkl.append(IDs[i])
			EvID_pkl.append(EvIDs[i])
		print('YOU HAVE DUMPED %.2f%% RECORDINGS (%d)'%((i+1)/len(PATHs)*100,i+1))
	pickle.dump(np.array(wf_pkl), open(output+'wf.pkl', 'wb'))
	pickle.dump(np.array(tick_pkl), open(output+'label.pkl', 'wb'))
	pickle.dump(np.array(ID_pkl), open(output+'id.pkl', 'wb'))
	pickle.dump(np.array(EvID_pkl), open(output+'eventid.pkl', 'wb'))
	return


if __name__ == "__main__":
	filelist = config.good_SNR
	output = config.pkl_dir
	dump(filelist, output, error=5)
	#test for dump
	f1 = 'label.pkl'
	f2 = 'wf.pkl'
	f3 = 'id.pkl'
	f4 = 'eventid.pkl'
	tick = pickle.load(open(output+f1, 'rb'))
	wf = pickle.load(open(output+f2, 'rb'))
	ID = pickle.load(open(output+f3, 'rb'))
	print(tick.shape, wf.shape, ID.shape)
