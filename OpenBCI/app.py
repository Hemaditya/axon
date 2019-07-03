import pyOpenBCI as p #For pyOpenBCI
import re # to match ttyUSB
import os # to get files in /dev
import time # to set up timestamps
import numpy as np # for operations on buffers
import matplotlib.pyplot as plt # to ppppppppplot
import scipy.signal as signal # to signal
from scipy.fftpack import fft
from matplotlib import mlab

class DataStream():
	def __init__(self,port=None,daisy=False,chunk_size=250,b_times=32,n_channels=8,spec_analyse=3, NFFT=512):
		if(port == None):
			self.get_port()
		else:
			self.port = port
		self.daisy = daisy
		self.n_channels=n_channels
		self.stream = p.OpenBCICyton(self.port,self.daisy)
		self.chunk_size = chunk_size
		self.window_size = chunk_size
		self.buffer_size = self.chunk_size*b_times
		self.data_buffer = []
		self.raw_buffer = np.zeros(shape=(self.buffer_size))
		self.uVolts_per_count = (4.5)/24/(2**23-1)*1000000
		self.channels_to_process = []
		self.filter_outputs = {}
		self.plot_buffer = {}
		self.spec_analyse = spec_analyse
		self.spec_True = 0
		self.NFFT = NFFT
		# Plotting and filter buffers
		self.filter_outputs['dc_offset'] = np.zeros(shape=(self.buffer_size))
		self.filter_outputs['notch_filter'] = np.zeros(shape=(self.buffer_size))
		self.filter_outputs['bandpass'] = np.zeros(shape=(self.buffer_size))
		self.filter_outputs['spec_analyser'] = np.array([])
		self.plot_buffer['dc_offset'] = np.array([])
		self.plot_buffer['notch_filter'] = np.array([])
		self.g = 0
		self.plot_buffer['bandpass'] = np.array([])
		self.plot_buffer['spec_analyser'] = np.zeros(shape=(self.window_size*self.chunk_size))
		self.plot_buffer['spec_freqs'] = np.zeros(shape=(self.window_size*self.chunk_size))
		self.plot_buffer['spectrogram'] = np.zeros(shape=(100,self.NFFT/2 +1))

	def read_chunk(self,n_chunks=1):
		all_chunks = []
		for i in range(n_chunks):
			all_chunks.append(self.stream.start_stream(self.chunk_size))
		self.data_buffer = np.array(all_chunks)*self.uVolts_per_count
		#self.plot_buffer['raw_data'] = self.data_buffer

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
			#self.plot_buffer['notch_filter'] = np.append(self.filter_outputs['notch_filter'],notchOutput)
			self.filter_outputs['notch_filter'][:-self.window_size] = self.filter_outputs['notch_filter'][self.window_size:]
			self.filter_outputs['notch_filter'][-self.window_size:] = notchOutput

	def bandpass(self):
		start = 1
		stop = 60
		bp_Hz = np.zeros(0)
		bp_Hz = np.array([start,stop])
		b, a = signal.butter(3, bp_Hz/(250 / 2.0),'bandpass')
		bandpassOutput = signal.lfilter(b, a, self.filter_outputs['notch_filter'], 0)[-self.window_size:]
		#self.plot_buffer['bandpass'] = np.append(self.filter_outputs['bandpass'],bandpassOutput)
		self.filter_outputs['bandpass'][:-self.window_size] = self.filter_outputs['bandpass'][self.window_size:]
		self.filter_outputs['bandpass'][-self.window_size:] = bandpassOutput

	def remove_dc_offset(self):
		hp_cutoff_Hz = 1.0

		b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
		dcOutput = signal.lfilter(b, a, self.raw_buffer, 0)[-self.window_size:]
		self.filter_outputs['dc_offset'][:-self.window_size] = self.filter_outputs['dc_offset'][self.window_size:]
		self.filter_outputs['dc_offset'][-self.window_size:] = dcOutput

	def get_spectrum_data(self):
		NFFT = 512
		overlap  = NFFT - int(0.25 * 250)
		spec_PSDperHz, spec_freqs, spec_t  = mlab.specgram(np.squeeze(self.filter_outputs['spec_analyser']),
									   NFFT=NFFT,
									   window=mlab.window_hanning,
									   Fs=250,
									   noverlap=overlap
									   ) # returns PSD power per Hz
		#print('PSDHERZ: ',spec_PSDperHz.shape)
		#print('spec_freqs: ',spec_freqs.shape)
		#print('t: ',spec_t.shape)
		#x = raw_input("SAD")
		spectrum_PSDperHz = np.mean(spec_PSDperHz,1)
		self.plot_buffer['spec_analyser'] = np.copy(10*np.log10(spectrum_PSDperHz))
		self.plot_buffer['spec_freqs'] = np.copy(spec_freqs)

		#self.plot_buffer['spectrogram'][:,:-1] = self.plot_buffer['spectrogram'][:,1:]
		self.plot_buffer['spectrogram'] = np.roll(self.plot_buffer['spectrogram'],-1,0)
		self.plot_buffer['spectrogram'][-1:] = 10*np.log10(spectrum_PSDperHz).reshape(-1)
		self.spec_True = 1

	def process_raw(self,channels=[3],meth='live'):
		if(channels=='all'):
			self.channels_to_process = [i+1 for i in range(self.n_channels)]
			pass
		else:
			self.channels_to_process = [int(i) for i in channels]

		for channel in self.channels_to_process:
			#if(meth == 'static'):
			#	self.filter_outputs['dc_offset'] = np.zeros(shape=(self.buffer_size))
			#	self.filter_outputs['notch_filter'] = np.zeros(shape=(self.buffer_size))
			#	self.filter_outputs['bandpass'] = np.zeros(shape=(self.buffer_size))
			#	self.plot_buffer['dc_offset'] = np.array([])
			#	self.plot_buffer['notch_filter'] = np.array([])
			#	self.plot_buffer['bandpass'] = np.array([])
						
			for _n in range(self.data_buffer.shape[0]):
				# shift window_size bytes from raw_buffer and add new bytes
				self.raw_buffer[:-self.window_size] = self.raw_buffer[self.window_size:]
				self.raw_buffer[-self.window_size:] = self.data_buffer[_n,:,channel]
				
				# remove the dc offset from the raw_buffer data
				self.remove_dc_offset()
				#apply notch_filter
				self.notch_filter()
				#apply bandpass
				self.bandpass()
				# handle spec analyser
				self.filter_outputs['spec_analyser'] = np.append(self.filter_outputs['spec_analyser'], self.filter_outputs['bandpass'][-self.window_size:])
				if(self.filter_outputs['spec_analyser'].reshape(-1).shape[0] == self.window_size*self.spec_analyse):
					self.g= 1
					self.get_spectrum_data()
					self.filter_outputs['spec_analyser'] = np.array([])
						

