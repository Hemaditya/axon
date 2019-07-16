import sys
import numpy as np
sys.path.append('../OpenBCI/')

import app

class BCIWebApp(app.DataStream):
	
	def __init__(self,port=None,daisy=False,chunk_size=250,b_times=1,n_channels=8,spec_analyse=1, NFFT=512, filters=None, channels='all', spectrogramWindow=1000):
		app.DataStream.__init__(self, port=port, chunk_size=chunk_size,b_times=b_times,n_channels=n_channels,spec_analyse=spec_analyse,NFFT=NFFT,channels=channels)
	


	def calculate_channels_average_data(self):
	# This function wil calculate the average values from a channel for each chunk of data
	# Used to check if the electrodes are fit properly
		for _n in range(self.data_buffer.shape[0]):
					print(self.data_buffer[_n,:,:] <= -50000 )

x = BCIWebApp()
while True:
	x.read_chunk()
	x.calculate_channels_average_data()
