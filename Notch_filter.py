import time
import numpy as np
from scipy import signal
from pyOpenBCI import OpenBCICyton
import matplotlib.pyplot as plt

time = 0
sample_count = 0
xs = []
raw_data = []
filtered = []
fs_Hz = 250

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
 	ax2.plot(xs, filtered, color='b')
	fig2.canvas.draw()
	ax2.set_xlim(left=max(0, time-50), right=time+50)
	
def process_raw(sample):
	global sample_count , time
	raw_data.append(sample.channels_data[0] * (4.5)/24/(2**23-1))
	xs.append(time)
	sample_count += 1
	time +=1
	if sample_count == 128:
		sample_count = 0
		plot1()
		bandpass(1,50)
		plot2()

def bandpass(start,stop):
	global filtered
	bp_Hz = np.zeros(0)
	bp_Hz = np.array([start,stop])
	b, a = signal.butter(3, bp_Hz/(fs_Hz / 2.0),'bandpass')
	filtered = signal.lfilter(b, a, raw_data, 0)

board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)

board.start_stream(process_raw)

plt.close()
