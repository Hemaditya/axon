import pyOpenBCI as p #For pyOpenBCI
import re # to match ttyUSB
import os # to get files in /dev
import time # to set up timestamps
import numpy as np # for operations on buffers
import matplotlib.pyplot as plt # to ppppppppplot
import scipy.signal as signal # to signal


class DataStream():
	def __init__(self,port=None,daisy=False,chunk_size=250,n_channels=8):
		if(port == None):
			self.get_port()
		else:
			self.port = port
		self.daisy = daisy
		self.n_channels=n_channels
		self.stream = p.OpenBCICyton(self.port,self.daisy)
		self.chunk_size = chunk_size
		self.window_size = chunk_size
		self.buffer_size = chunk_size*4
		self.data_buffer = []
		self.raw_buffer = np.zeros(shape=(self.buffer_size))
		self.uVolts_per_count = (4.5)/24/(2**23-1)*1000000
		self.channels_to_process = []
		self.filter_outputs = {}
		self.plot_buffer = {}
		pass

	def read_chunk(self,n_chunks=1):
		all_chunks = []
		for i in range(n_chunks):
			print("READING_CHUNK: "+str(i+1))
			all_chunks.append(self.stream.start_stream(self.chunk_size))
		self.data_buffer = np.array(all_chunks)*self.uVolts_per_count
		self.plot_buffer['raw_data'] = self.data_buffer

	def get_port(self):
		files = os.listdir('/dev')
		for i in files:
			obj = re.match('ttyUSB.$',i)
			if(obj != None):
				self.port = '/dev/'+obj.group()

	def notch_filter(self):
		notch_freq_Hz = np.array([50.0])  # main + harmonic frequencies
		for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each target freq
			bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
			b, a = signal.butter(3, bp_stop_Hz/(250 / 2.0), 'bandstop')
			notchOutput	= signal.lfilter(b, a, self.filter_outputs['dc_offset'], 0)[-self.window_size:]
			self.plot_buffer['notch_filter'] = np.append(self.filter_outputs['notch_filter'],notchOutput)
			self.filter_outputs['notch_filter'][:-self.window_size] = self.filter_outputs['notch_filter'][self.window_size:]
			self.filter_outputs['notch_filter'][-self.window_size:] = notchOutput

	def bandpass(self):
		start = 8
		stop = 13
		bp_Hz = np.zeros(0)
		bp_Hz = np.array([start,stop])
		b, a = signal.butter(3, bp_Hz/(250 / 2.0),'bandpass')
		bandpassOutput = signal.lfilter(b, a, self.filter_outputs['notch_filter'], 0)[-self.window_size:]
		self.plot_buffer['bandpass'] = np.append(self.filter_outputs['bandpass'],bandpassOutput)
		self.filter_outputs['bandpass'][:-self.window_size] = self.filter_outputs['bandpass'][self.window_size:]
		self.filter_outputs['bandpass'][-self.window_size:] = bandpassOutput
		
	def remove_dc_offset(self):
	
		hp_cutoff_Hz = 1.0

		b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
		dcOutput = signal.lfilter(b, a, self.raw_buffer, 0)[-self.window_size:]
		self.plot_buffer['dc_offset'] = np.append(self.filter_outputs['dc_offset'],dcOutput)
		self.filter_outputs['dc_offset'][:-self.window_size] = self.filter_outputs['dc_offset'][self.window_size:]
		self.filter_outputs['dc_offset'][-self.window_size:] = dcOutput

	def plot(self,c=0,outputs=None):
		if(outputs != None):
			for o in outputs:
				plt.plot(self.plot_buffer[o].reshape(-1),label=o)
			plt.legend()
			plt.show()		
	
	def process_raw(self,channels=[0]):
		if(channels=='all'):
			self.channels_to_process = [i+1 for i in range(self.n_channels)]
			pass
		else:
			self.channels_to_process = [int(i) for i in channels]

		for channel in self.channels_to_process:
			self.filter_outputs['dc_offset'] = np.zeros(shape=(self.buffer_size))
			self.filter_outputs['notch_filter'] = np.zeros(shape=(self.buffer_size))
			self.filter_outputs['bandpass'] = np.zeros(shape=(self.buffer_size))
			self.plot_buffer['dc_offset'] = np.array([])
			self.plot_buffer['notch_filter'] = np.array([])
			self.plot_buffer['bandpass'] = np.array([])
			for n in range(self.data_buffer.shape[0]):
				# shift window_size bytes from raw_buffer and add new bytes
				self.raw_buffer[:-self.window_size] = self.raw_buffer[self.window_size:]
				self.raw_buffer[-self.window_size:] = self.data_buffer[n,:,channel]
				
				# remove the dc offset from the raw_buffer data
				self.remove_dc_offset()
				# apply notch_filter
				self.notch_filter()
				# apply bandpass
				self.bandpass()



s = DataStream()
print("STARTED READING")
s.read_chunk(n_chunks=1)
t1 = time.time()
s.process_raw()
t2 = time.time()
print(t2-t1)
