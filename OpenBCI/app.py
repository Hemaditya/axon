# This is for processing of data
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
	'''
	port = USB port number ex: /dev/ttyUSB0	
	daisy = daisy board
	chunk_size = BCI gives a sample with 8 valuesi for 8 channels. Chunk size defines how many such 
				samples to read in one iteration
	b_times = referes to the size of buffer w.r.t the chunk size
				if chunk size is 50, and b_times is 5, then buffer_size will be 5*50 = 250
	n_channels = no.of channels on BCI
	spec_analyse = no.of chunks to send to fft
	NFFT = bin number for fft
	filters =   future use
	channels = future use
	spectrogramWindow = buffer size for spectrogram
	'''
	def __init__(self,port=None,daisy=False,chunk_size=250,b_times=32,n_channels=8,spec_analyse=3, NFFT=512, filters=None, channels='all', spectrogramWindow=1000):
		if(port == None):
			self.get_port()
		else:
			self.port = port
		self.daisy = daisy
		self.n_channels=n_channels
		self.stream = p.OpenBCICyton(self.port,self.daisy)
		self.chunk_size = chunk_size
		self.window_size = chunk_size
		self.stateBand = [0,0,0,0,0,0]
		self.plot_size = 10
		self.state = [0,0]
		self.stateNotch = [0,0,0,0,0,0]
		self.prevDC = 0
		self.buffer_size = self.chunk_size*self.plot_size
		self.data_buffer = []
		self.raw_buffer = {}
		self.uVolts_per_count = (4.5)/24/(2**23-1)*1000000 # scalar factor to convert raw data into real world signal data
		if(channels == 'all'):
			self.channels_to_process = [i for i in range(n_channels)]	
		else:	
			self.channels_to_process = [i for i in channels]
		self.filter_outputs = {} # outputs of all filters 
		self.plot_buffer = {} # The data that needs to be plotted
		self.spec_analyse = spec_analyse
		self.spec_True = {} # to flag spectrogram plotting
		self.NFFT = NFFT
		
		self.prevFilterOutput = np.array([])
		# Plotting and filter buffers
		# Initialization of filter_outputs 
		self.filter_outputs['dc_offset'] = {}
		self.filter_outputs['notch_filter'] = {}
		self.filter_outputs['bandpass'] = {}
		self.filter_outputs['spec_analyser'] = {}
		self.plot_buffer['dc_offset'] = {}
		self.plot_buffer['notch_filter'] = {}
		self.plot_buffer['bandpass'] = {}
		self.plot_buffer['spec_analyser'] = {}
		self.plot_buffer['spec_freqs'] = {}
		self.plot_buffer['spectrogram'] = {}
		# First create 8 channels for all buffers
		for i in range(self.n_channels):
			self.spec_True[i] = 0
			self.raw_buffer[i] = np.zeros(shape=(self.window_size))
			self.filter_outputs['dc_offset'][i] = np.zeros(shape=(self.window_size))
			self.filter_outputs['notch_filter'][i] = np.zeros(shape=(self.window_size))
			self.filter_outputs['bandpass'][i] = np.zeros(shape=(self.window_size))
			self.filter_outputs['spec_analyser'][i] = np.array([])
			self.plot_buffer['dc_offset'][i] = np.zeros(shape=(self.buffer_size))
			self.plot_buffer['notch_filter'][i] = np.zeros(shape=(self.buffer_size))
			self.plot_buffer['bandpass'][i] = np.zeros(shape=(self.buffer_size))
			self.plot_buffer['spec_analyser'][i] = np.zeros(shape=(self.buffer_size))
			self.plot_buffer['spec_freqs'][i] = np.zeros(shape=(self.buffer_size))
			self.plot_buffer['spectrogram'][i] = np.zeros(shape=(spectrogramWindow,self.NFFT/2 + 1))

	def read_chunk(self,n_chunks=1):
		# n_chunks = number of chunks to read. Keep it 1 for live data
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
		# This is to remove the AC mains noise interference	of frequency of 50Hz(India)
		notch_freq_Hz = np.array([50.0])  # main + harmonic frequencies
		for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each target freq
			bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
			b, a = signal.butter(3, bp_stop_Hz/(250 / 2.0), 'bandstop')
#<<<<<<< HEAD
#			
#			notchOutput,self.stateNotch	= signal.lfilter(b, a, self.filter_outputs['dc_offset'][self.currentChannel], zi=self.stateNotch)[-self.window_size:]
#=======
			notchOutput	= signal.lfilter(b, a, self.filter_outputs['dc_offset'], 0)[-self.window_size:]
			#self.plot_buffer['notch_filter'] = np.append(self.filter_outputs['notch_filter'],notchOutput)
			# A = [6,7,8,9,1,2,3,4] = [7,8,9,1,2,3,4,4]
			# A[last value] = notchOutput
			# A[:num] = all values from start till index num
			# A[:-num] = all values from start to index num from the revers
#<<<<<<< HEAD
##<<<<<<< HEAD
			self.filter_outputs['notch_filter'][self.currentChannel][:-self.window_size] = self.filter_outputs['notch_filter'][self.currentChannel][self.window_size:]
			self.filter_outputs['notch_filter'][self.currentChannel][-self.window_size:] = notchOutput
##=======
#			self.filter_outputs['notch_filter'][self.currentChannel][:-self.window_size] = self.filter_outputs['notch_filter'][self.currentChannel][self.window_size:]
#			self.filter_outputs['notch_filter'][self.currentChannel][-self.window_size:] = notchOutput
#		
#			self.plot_buffer['notch_filter'][self.currentChannel][:-self.window_size] = self.plot_buffer['notch_filter'][self.currentChannel][self.window_size:]
#			self.plot_buffer['notch_filter'][self.currentChannel][-self.window_size:] = notchOutput
#=======

	def bandpass(self):
		# This is to allow the band of signal to pass with start frequency and stop frequency
		start = 1
		stop = 60
		self.prevDC = [0,0]
		bp_Hz = np.zeros(0)
		bp_Hz = np.array([start,stop])
		b, a = signal.butter(3, bp_Hz/(250 / 2.0),'bandpass')
		bandpassOutput = signal.lfilter(b, a, self.filter_outputs['dc_offset'][self.currentChannel], 0)[-self.window_size:]
		#self.plot_buffer['bandpass'] = np.append(self.filter_outputs['bandpass'],bandpassOutput)
		self.filter_outputs['bandpass'][:-self.window_size] = self.filter_outputs['bandpass'][self.window_size:]
		self.filter_outputs['bandpass'][-self.window_size:] = bandpassOutput

	def remove_dc_offset(self):
		# This is to Remove The DC Offset By Using High Pass Filters
		hp_cutoff_Hz = 1.0 # cuttoff freq of 1 Hz (from 0-1Hz all the freqs at attenuated)
		b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
		dcOutput = signal.lfilter(b, a, self.raw_buffer, 0)[-self.window_size:]
		self.filter_outputs['dc_offset'][:-self.window_size] = self.filter_outputs['dc_offset'][self.window_size:]
		self.filter_outputs['dc_offset'][-self.window_size:] = dcOutput

	def get_spectrum_data(self):
		# This is to generate spectrogram data
		NFFT = self.NFFT
		overlap  = NFFT - int(0.25 * 250)
		spec_PSDperHz, spec_freqs, spec_t  = mlab.specgram(np.squeeze(self.filter_outputs['spec_analyser']),
									   NFFT=NFFT,
									   window=mlab.window_hanning,
									   Fs=250,
									   noverlap=overlap
									   ) # returns PSD power per Hz
		spectrum_PSDperHz = np.mean(spec_PSDperHz,1)
		#self.plot_buffer['spec_analyser'] = np.copy(10*np.log10(spectrum_PSDperHz))
		self.plot_buffer['spec_freqs'] = np.copy(spec_freqs)

		#self.plot_buffer['spectrogram'][:,:-1] = self.plot_buffer['spectrogram'][:,1:]
		self.plot_buffer['spectrogram'] = np.roll(self.plot_buffer['spectrogram'],-1,0)
		spec_PSDperBin = spectrum_PSDperHz * 250.0 / float(NFFT)
		self.plot_buffer['spectrogram'][-1:] = 10*np.log10(spec_PSDperBin).reshape(-1)
		self.spec_True = 1

	def process_raw(self,channels=[0],meth='live'):
		if(channels=='all'):
			self.channels_to_process = [i+1 for i in range(self.n_channels)]
			pass
		else:
			self.channels_to_process = [int(i) for i in channels]

		for channel in self.channels_to_process:
			
			for _n in range(self.data_buffer.shape[0]):
				# shift window_size bytes from raw_buffer and add new bytes
				self.raw_buffer[:-self.window_size] = self.raw_buffer[self.window_size:]
				self.raw_buffer[-self.window_size:] = self.data_buffer[_n,:,channel]
				# remove the dc offset from the raw_buffer data
				self.remove_dc_offset()
				#apply notch_filter
				#self.notch_filter()
				#apply bandpass
				self.bandpass()
				# handle spec analyser
				self.filter_outputs['spec_analyser'] = np.append(self.filter_outputs['spec_analyser'], self.filter_outputs['bandpass'][-self.window_size:])
				if(self.filter_outputs['spec_analyser'].reshape(-1).shape[0] == self.window_size*self.spec_analyse):
					self.get_spectrum_data()
					self.filter_outputs['spec_analyser'] = np.array([])
						

