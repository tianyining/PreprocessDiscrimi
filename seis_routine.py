"""routine process for trace-like seismic data"""


def Process(trace, freqmin=1, freqmax=15):
	"""routine process for trace or stream
		bandpass
		detrend
		taper
	"""
	x = trace.copy()
	x.detrend()
	x.taper(max_percentage=0.05)
	x.filter(
			"bandpass",
			freqmin=freqmin, freqmax=freqmax,
			corners=2,
			zerophase=True)
	return x

if __name__ == "__main__":
	import config
	from obspy import  read
	raw_wf = read('tmp/benchmark/*.sac')[0]
	processed_wf = Process(raw_wf)
	print("raw_wf",raw_wf.data,"processed _wf",processed_wf.data)
	raw_wf.plot(outfile="tmp/test/raw.png")
	processed_wf.plot(outfile="tmp/test/processed.png")
