import ThinkBCI
import numpy as np
from pyOpenBCI import OpenBCICyton
raw_data = []
uVolts_per_count = (4.5)/24/(2**23-1)*1000000
sample_count = 0
window_size = 128
# Required settings #

# Data source. Options:
# 'muse' for data from Muse headsets.
# 'muse-lsl' for data from Muse headsets recorded with Lab Streaming Layer.
# 'openbci' for OpenBCI Cyton data recorded with the OpenBCI GUI;
# 'openbci-ganglion' for OpenBCI Ganglion data recorded with the OpenBCI GUI;
# 'openbci-openvibe' for Cyton data recorded with OpenViBE's csv writer
# 'openbci-ganglion-openvibe' for Ganglion data recorded with OpenViBE's csv writer

#source = 'openbci'

# Path to EEG data file
#path = '/home/hemaditya/BCI/EEGrunt/data/'

# EEG data file name
#filename = 'eegrunt-obci-ovibe-test-data.csv'

# Session title (used in some plots and such)
# session_title = "OpenBCI Data"

# # Channel
# channel = 1

# # Initialize
EEG = ThinkBCI.ThinkBCI()

# # Here we can set some additional properties
# # The 'plot' property determines whether plots are displayed or saved.
# # Possible values are 'show' and 'save'
# EEG.plot = 'show'

# # Load the EEG data
# EEG.load_data()

# EEG.load_channel(channel)

# print("Processing channel "+ str(EEG.channel))

# # Removes OpenBCI DC offset
# EEG.remove_dc_offset()

# # Notches 60hz noise (if you're in Europe, switch to 50Hz)
# EEG.notch_mains_interference()

# # Make signal plot
# EEG.signalplot()

# # Calculates spectrum data and stores as EEGrunt attribute(s) for reuse
# EEG.get_spectrum_data()

# # Returns bandpassed data
# # (uses scipy.signal butterworth filter)
# start_Hz = 1
# stop_Hz = 50
# EEG.data = EEG.bandpass(start_Hz,stop_Hz)

# # Make Spectrogram
# EEG.spectrogram()

# # Line graph of amplitude over time for a given frequency range.
# # Arguments are start frequency, end frequency, and label
# EEG.plot_band_power(8,12,"Alpha")

# # Power spectrum plot
# EEG.plot_spectrum_avg_fft()

# # Plot coherence fft (not tested recently...)
# # s1 = bandpass(seginfo["data"][:,1-1], config['band'])
# # s2 = bandpass(seginfo["data"][:,8-1], config['band'])
# # plot_coherence_fft(s1,s2,"1","8")

# EEG.showplots()

def acquire_raw(sample):
	global sample_count , window_size, raw_data
	sample_count+= 1
	sample.channels_data = uVolts_per_count * np.array(sample.channels_data)
	for x in xrange(0,7):
		raw_data.append(sample.channels_data[x])
	if sample_count == window_size:
		sample_count = 0
		process_raw()
		raw_data = []
	# xs.append(time)
	# sample_count += 1
	# time +=1
	# 
	# 	plot1()
	# 	bandpass(1,50)
	# 	plot2()

def process_raw():
	EEG.load_data(raw_data)



	
board = OpenBCICyton(port='/dev/ttyUSB5', daisy=False)

board.start_stream(acquire_raw)