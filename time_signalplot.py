from pyOpenBCI import OpenBCICyton
import numpy as np

import matplotlib.pyplot as plt
import time

# from tkinter import TclError
    

# %matplotlib tk
uVolts_per_count = (4.5)/24/(2**23-1)*1000000
CHUNK = 255             # samples per frame\n",
#FORMAT = pyaudio.paInt16     # audio format (bytes per sample?)\n",
CHANNELS = 1                 # single channel for microphone\n",
RATE = 255                 # samples per second"
sample_count = 0
window_size = 255
raw_data = []
# fig, ax = plt.subplots(1, figsize=(15, 7))



#  line, = ax.plot(x, np.random.rand(CHUNK), '-', lw=2)

# ax.set_title('AUDIO WAVEFORM')
# ax.set_xlabel('samples')
# ax.set_ylabel('volume')
# ax.set_ylim(0, 255)
# ax.set_xlim(0, 2 * CHUNK)
# plt.setp(ax, xticks=[0, CHUNK, 2 * CHUNK], yticks=[0, 128, 255])
fig, ax = plt.subplots()


x = np.arange(0, 2 * CHUNK, 2)
line, = ax.plot(x, np.random.rand(CHUNK))
ax.set_xlim(0, CHUNK)
ax.set_ylim(100000,-100000)

def acquire_raw(sample):
	global sample_count , window_size, raw_data
	sample_count+= 1
	raw_data.append(uVolts_per_count * sample.channels_data[0])
	if sample_count == window_size:
		sample_count = 0
		line.set_ydata(raw_data) 
		fig.canvas.draw()
		# fig.canvas.flush_events()
		# ax.plot(raw_data,'-')
		plt.show(block=False)
		# print(raw_data)
		raw_data = []

	# xs.append(time)
	# sample_count += 1
	# time +=1
	#     
	# 	plot1()
	# 	bandpass(1,50)
	# 	plot2()


	
board = OpenBCICyton(port='/dev/ttyUSB4', daisy=False)

board.start_stream(acquire_raw)


