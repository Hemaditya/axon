import ThinkBCI
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from pyOpenBCI import OpenBCICyton
import threading
np.set_printoptions(threshold=np.inf)
raw_data = []
uVolts_per_count = (4.5)/24/(2**23-1)*1000000
sample_count = 0
window_size = 500
n_shift = 100
i = 0


# # Initialize
EEG = ThinkBCI.ThinkBCI()
EEG.plot = 'show'


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
counter = 0
previous_data = []

def acquire_raw(sample):
	global sample_count , window_size, raw_data, counter, previous_data
	sample_count+= 1
	sample.channels_data = uVolts_per_count * np.array(sample.channels_data)
	raw_data.append(list(sample.channels_data))
	if counter == 0 and sample_count == window_size:
		counter = 1
		raw_data = np.array(raw_data)
		previous_data = raw_data[n_shift:]
		raw_data = []
		sample_count = 0

	if sample_count ==  n_shift and counter == 1:
		print('inside window')
		sample_count = 0
		raw_data = np.array(raw_data)
		raw_data = np.concatenate((previous_data,raw_data),axis=0)
		#print(previous_data == raw_data[:window_size-n_shift])
		previous_data = np.array(raw_data[n_shift:])
		process_raw()
		raw_data = []
		
	

def process_raw():
	EEG.load_data(raw_data)
	EEG.load_channel(1)
	EEG.remove_dc_offset()
	#EEG.notch_mains_interference()
	EEG.signalplot()
	#EEG.pyqtplot()
# Returns bandpassed data
# (uses scipy.signal butterworth filter)
#	start_Hz = 1
##	EEG.data = EEG.bandpass(start_Hz,stop_Hz)

# Make Spectrogram
#	EEG.spectrogram()

# Line graph of amplitude over time for a given frequency range.
# Arguments are start frequency, end frequency, and label
#	EEG.plot_band_power(8,12,"Alpha")

# Power spectrum plot
#	EEG.plot_spectrum_avg_fft()

t1 = []


print("AFTER PYQT")
	
board = OpenBCICyton(port='/dev/ttyUSB1', daisy=False)
board.start_stream(acquire_raw)
#t1 = threading.Thread(target=board.start_stream, args=(acquire_raw,))
#board.start_stream(acquire_raw)



