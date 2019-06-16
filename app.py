import ThinkBCI
import numpy as np
from pyOpenBCI import OpenBCICyton
np.set_printoptions(threshold=np.inf)
raw_data = []
uVolts_per_count = (4.5)/24/(2**23-1)*1000000
sample_count = 0
window_size = 1000
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

def acquire_raw(sample):
	global sample_count , window_size, raw_data
	sample_count+= 1
	sample.channels_data = uVolts_per_count * np.array(sample.channels_data)
	for x in xrange(0,8):
		raw_data.append(sample.channels_data[x])
	if sample_count == window_size:
		# print(len(raw_data))
		sample_count = 0
		raw_data = np.array(raw_data)
		# print(len(raw_data))
		raw_data = raw_data.reshape(window_size,8)
		# print(raw_data)
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
	EEG.load_channel(1)
	EEG.remove_dc_offset()
	EEG.notch_mains_interference()
	EEG.signalplot()
# Returns bandpassed data
# (uses scipy.signal butterworth filter)
	start_Hz = 1
	stop_Hz = 50
	EEG.data = EEG.bandpass(start_Hz,stop_Hz)

# Make Spectrogram
	EEG.spectrogram()

# Line graph of amplitude over time for a given frequency range.
# Arguments are start frequency, end frequency, and label
	EEG.plot_band_power(8,12,"Alpha")

# Power spectrum plot
	EEG.plot_spectrum_avg_fft()



	
board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)

board.start_stream(acquire_raw)