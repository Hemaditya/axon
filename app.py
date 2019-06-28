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

q = queue.Queue(maxsize=1000)

np.set_printoptions(threshold=np.inf)
raw_data = []
uVolts_per_count = (4.5)/24/(2**23-1)*1000000
sample_count = 0
window_size = 64 
n_shift = 64
i = 0


counter = 0
previous_data = []
rawBuffer = []
filterBuffer = [0 for i in range(320)]
filterOutput = [0 for i in range(320)]
notchOutput = [0 for i in range(320)]
plotBuffer = [0 for i in range(4096)]
x = [i+1 for i in range(0,4096)]
# For bandpass
start = 8
stop = 13

def plot(raw,filtered):
	plt.plot(x,raw,color='green')
	plt.plot(x,filtered,color='red')
	plt.draw()

def plot2():
	global x
	plt.plot(x, plotBuffer, color='red')
	plt.draw()

def bandpass():
	global plotBuffer, notchOutput, start, stop
	bp_Hz = np.zeros(0)
	bp_Hz = np.array([start,stop])
	b, a = signal.butter(3, bp_Hz/(250 / 2.0),'bandpass')
	last64Bytes = signal.lfilter(b, a, notchOutput, 0)
	last64Bytes = last64Bytes[-64:]
	plotBuffer[:-window_size] = plotBuffer[window_size:]
	plotBuffer[-window_size:] = last64Bytes

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
	rawBuffer.append(sample.channels_data[0]*uVolts_per_count)
	if(sample_count == window_size):
		sample_count = 0
		process_raw()
		rawBuffer = []
		
	

def process_raw():
	global rawBuffer,filterBuffer
	#print(rawBuffer)
	filterBuffer[:-window_size] = filterBuffer[window_size:]
	filterBuffer[-window_size:] = rawBuffer

	last64 = remove_dc_offset()
	notch_filter()
	bandpass()
	#plot(rawBuffer, last64)	
	plot2()
	plt.pause(0.001)
	#time.sleep(1)
	plt.clf()

plt.ion()
plt.ylim(-3000,3000)
plt.legend()
plt.show()
print("AFTER PYQT")
	
board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)
board.start_stream(acquire_raw)
#t1 = threading.Thread(target=board.start_stream, args=(acquire_raw,))
#board.start_stream(acquire_raw)
#t1.start()




