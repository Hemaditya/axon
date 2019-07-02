import ThinkBCI
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
from pyOpenBCI import OpenBCICyton
import threading
import queue
import time
from scipy import signal
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

q = queue.Queue(maxsize=1000)

np.set_printoptions(threshold=np.inf)
raw_data = []
uVolts_per_count = (4.5)/24/(2**23-1)*1000000
sample_count = 0
window_size = 64 
n_shift = 64
i = 0
spectrogramData = [[0 for i in range(39)] for i in range(257)]
spectrogramData = np.array(spectrogramData)


counter = 0
previous_data = []
rawBuffer = []
filterBuffer = [0 for i in range(512)]
filterOutput = [0 for i in range(512)]
notchOutput = [0 for i in range(512)]
bandpassOutput = [0 for i in range(512)]
plotBuffer = [0 for i in range(4096)]
specBuffer = [0 for i in range(1024)]
specCount = 0
x = [i+1 for i in range(0,4096)]
# For bandpass
start = 1
stop = 50

fig1,ax1 = plt.subplots()
fig2,ax2 = plt.subplots()
#fig3,ax3 = plt.subplots()

spec_PSDperBin = 0
spec_t = 0
spec_PSDperHz = 0
spec_freqs = 0

# 39 values 
spec_time = np.arange(0.512,10,0.248)
plt.figure(figsize=(10,5))
ax = plt.subplot(1,1,1)

def spectrogram():
	global notchOutput,specBuffer, spec_PSDperHz, spec_freqs, spec_t, spec_PSDperBin,spec_time,spectrogramData
	f_lim_Hz = [0, 50]   # frequency limits for plotting
	#print("SPEC_T")
	print(spec_t.shape)
	#print(spectrogramData.shape)
	plt.pcolormesh(spec_t, spec_freqs, 10*np.log10(spec_PSDperBin))  # dB re: 1 uV
	#plt.imshow(spectrogramData)
	plt.clim([-25,26])
	plt.xlim(spec_t[0], spec_t[-1])
	plt.ylim(f_lim_Hz)
	plt.xlabel('Time (sec)')
	plt.ylabel('Frequency (Hz)')
	plt.title("XYA")
	# add annotation for FFT Parameters
	ax.text(0.025, 0.95,
		"NFFT = " + str(512) + "\nfs = " + str(int(250)) + " Hz",
		transform=ax.transAxes,
		verticalalignment='top',
		horizontalalignment='left',
		backgroundcolor='w')
	plt.draw()

def get_spectrum_data():
	global notchOutput,specBuffer, spec_PSDperHz, spec_freqs, spec_t,spec_PSDperBin,spectrogramData,spec_time
	NFFT = 256
	overlap  = NFFT - int(0.25 * 250)
	spec_PSDperHz, spec_freqs, spec_t  = mlab.specgram(np.squeeze(specBuffer),
								   NFFT=NFFT,
								   window=mlab.window_hanning,
								   Fs=250,
								   noverlap=overlap
								   ) # returns PSD power per Hz
	#plt.imshow(spec_im)
	#print("JAJA"*20)
	#print(len(spec_t))
	# convert the units of the spectral data
	#spec_time = spec_t
	#print(spec_t.shape)
	#print(spec_t)
	spec_PSDperBin = spec_PSDperHz * 250 / float(NFFT)
	#print(spec_PSDperBin.shape)
	#toShift = spec_PSDperBin.shape[1]
	#tempBuffer = list(spec_PSDperBin)
	#spectrogramData[:,:-toShift] = spectrogramData[:,toShift:]
	#spectrogramData[:,-toShift:] = np.array(tempBuffer)
	#print(spec_PSDperBin.shape)
	#time.sleep(100)
	#print("="*60)
	#print(spec_PSDperBin)
	
	spectrum_PSDperHz = np.mean(spec_PSDperHz,1)
	ax2.plot(spec_freqs, 10*np.log10(spectrum_PSDperHz))  # dB re: 1 uV
	ax2.set_xlim((0,60))
	ax2.set_ylim((-30,50))
	plt.draw()
	#plotname = 'Channel '+str(0)+' Spectrum Average FFT Plot'
	#plt.set_xlabel('Frequency (Hz)')
	#plt.ylabel('PSD per Hz (dB re: 1uV^2/Hz)')

	#plt.title("Power Spectrum")
	#self.plotit(plt, self.plot_filename("Power Spectrum"))


def plot(raw,filtered):
	plt.plot(x,raw,color='green')
	plt.plot(x,filtered,color='red')
	plt.draw()

def makePlot():
	plt.draw()

def plot2():
	global x
	ax1.plot(x, plotBuffer, color='red')

def bandpass():
	global plotBuffer, notchOutput, start, stop, bandpassOutput, specBuffer, specCount, ax2
	bp_Hz = np.zeros(0)
	bp_Hz = np.array([start,stop])
	b, a = signal.butter(3, bp_Hz/(250 / 2.0),'bandpass')
	bandpassOutput = signal.lfilter(b, a, notchOutput, 0)
	last64Bytes = bandpassOutput[-64:]
	specBuffer = specBuffer + list(last64Bytes)
	specCount += 1
	print(specCount)
	if(specCount == 8):
		#ax3.clear()
		ax2.clear()
		#ax.clear()
		plt.clf()
		get_spectrum_data()
		spectrogram()
		specCount = 0
		specBuffer = []
	plotBuffer[:-window_size] = plotBuffer[window_size:]
	plotBuffer[-window_size:] = last64Bytes
	plot2()
	makePlot()
	#return last64Bytes

def notch_filter():
	global filterOutput,plotBuffer, notchOutput
	notch_freq_Hz = np.array([50.0])  # main + harmonic frequencies
	for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each target freq
		bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
		b, a = signal.butter(3, bp_stop_Hz/(250 / 2.0), 'bandstop')
		notchOutput	= signal.lfilter(b, a, filterOutput, 0)

def remove_dc_offset():
	global filterBuffer,filterOutput
	hp_cutoff_Hz = 1.0

	b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
	filterOutput = signal.lfilter(b, a, filterBuffer, 0)
	last64Bytes = filterOutput[-64:]
	return last64Bytes

def acquire_raw(sample):
	global sample_count , window_size, raw_data, counter, previous_data, rawBuffer
	sample_count+= 1
	rawBuffer.append(sample[0]*uVolts_per_count)
	if(sample_count == window_size):
		sample_count = 0
		process_raw()
		rawBuffer = []
		#x = raw_input("JAJAJA:")
		time.sleep(1)
		
	

def process_raw():
	global rawBuffer,filterBuffer
	#print(rawBuffer)
	filterBuffer[:-window_size] = filterBuffer[window_size:]
	filterBuffer[-window_size:] = rawBuffer

	last64 = remove_dc_offset()
	notch_filter()
	bandpass()
	#plot(rawBuffer, last64)	
	#plot2()
	#get_spectrum_data()
	#makePlot()
	plt.pause(0.0001)
	ax1.clear()
	#time.sleep(1)

plt.ion()
plt.show()
print("AFTER PYQT")
	
board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)
while(True):
	data = board.start_stream(1)
	print(data)
	acquire_raw(data[0])

#t1 = threading.Thread(target=board.start_stream, args=(acquire_raw,))
#board.start_stream(acquire_raw)
#t1.start()




