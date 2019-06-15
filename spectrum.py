import time
import numpy as np
from scipy import signal
from pyOpenBCI import OpenBCICyton
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

time = 0
sample_count = 0
xs = []
raw_data = []
filtered = []
dc_offset = []
notch_data = []
fs_Hz = 250
spec_PSDperHz=[]
spec_freqs=[]
spec_t=[]
NFFT = 512

sample_block = 11

overlap  = NFFT - int(0.25 * fs_Hz)

fig1 = plt.figure(1)
ax1 = fig1.add_subplot(1,1,1)
fig1.show()

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(1,1,1)
fig2.show()

def plot1():
	global time
 	ax1.plot(xs, raw_data, color='b')
	fig1.canvas.draw()
	ax1.set_xlim(left=max(0, time-50), right=time+50)

def plot2():
	global time
 	ax2.plot(xs, dc_offset, color='b')
	fig2.canvas.draw()
	ax2.set_xlim(left=max(0, time-50), right=time+50)
	
def process_raw(sample):
	global sample_count , time
	raw_data.append(sample.channels_data[0] * (4.5)/24/(2**23-1))
	xs.append(time)
	sample_count += 1
	time +=1
	if sample_count == 65535:
		sample_count = 0
		plot1()
		get_spectrum_data()
		# plot_spectrum_avg_fft()
		#notch_mains_interference()
		#plot2()

def bandpass(start,stop):
	global filtered
	bp_Hz = np.zeros(0)
	bp_Hz = np.array([start,stop])
	b, a = signal.butter(3, bp_Hz/(fs_Hz / 2.0),'bandpass')
	filtered = signal.lfilter(b, a, dc_offset, 0)

def remove_dc_offset():
	hp_cutoff_Hz = 1.0
	b, a = signal.butter(2, hp_cutoff_Hz/(fs_Hz / 2.0), 'highpass')
	dc_offset = signal.lfilter(b, a, raw_data, 0)

def notch_mains_interference():
	notch_freq_Hz = np.array([50.0])  # main + harmonic frequencies
	for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each target freq
		bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
		b, a = signal.butter(3, bp_stop_Hz/(fs_Hz / 2.0), 'bandstop')
		notch_data = signal.lfilter(b, a,dc_offset, 0)       
        
def get_spectrum_data():
        print("Calculating spectrum data...")
        spec_PSDperHz, spec_freqs, spec_t = mlab.specgram(np.squeeze(raw_data),
                                       NFFT,
                                       window=mlab.window_hanning,
                                       Fs=fs_Hz,
                                       noverlap=overlap
                                       ) # returns PSD power per Hz
        # convert the units of the spectral data
        spec_PSDperBin = spec_PSDperHz * fs_Hz / float(NFFT)

def plot_spectrum_avg_fft():

        # print("Generating power spectrum plot")

        spectrum_PSDperHz = np.mean(spec_PSDperHz,1)
        plt.figure(figsize=(10,5))
        plt.plot(spec_freqs, 10*np.log10(spectrum_PSDperHz))  # dB re: 1 uV
        plt.xlim((0,60))
        plt.ylim((-30,50))
        # plotname = 'Channel '+str(self.channel)+' Spectrum Average FFT Plot'
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('PSD per Hz (dB re: 1uV^2/Hz)')

        # plt.title(self.plot_title("Power Spectrum"))
        # self.plotit(plt, self.plot_filename("Power Spectrum"))


board = OpenBCICyton(port='/dev/ttyUSB2', daisy=False)

board.start_stream(process_raw)

plt.close()