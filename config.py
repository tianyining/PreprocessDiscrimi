import os


#data dir
data_dir = os.environ['HOME'] + '/Data/EqQbDiscrimi/'
blast_dir = data_dir + 'blast/'
quake_dir = data_dir + 'earthquakes/'
filelist = data_dir + 'flist' # file list
velocity_model = data_dir + 'velocitymodel/SoCal.nd'

#output dir
pkl_dir = '../../output/pickle/'
log_pkl = pkl_dir + "log_pkl.txt"
QC_dir = '../../output/QC/'
outputQC = QC_dir + 'QC.txt'
QClist = QC_dir + 'QClist'
good_SNR = QC_dir + 'snr10.txt'
image_dir = '../../image/'
plot_blast = image_dir + 'preview/waveform/qb/'
plot_quake = image_dir + 'preview/waveform/eq/'

#tmp dir for test
tmp_dir = 'tmp/'

#params
snr_thd = 10 #skip the recording whose snr < snr_thd
bp_low = 1
bp_high =15
