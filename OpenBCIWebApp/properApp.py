import app
import numpy as np
import os
from scipy import signal
import learner
import torch
import matplotlib.pyplot as plt
model = learner.NN()
model.load_state_dict(torch.load('newModel'))
model = model.double()

import time
import matplotlib.mlab as mlab
import trainer


ds = app.DataStream(chunk_size=50)
plt.ion()
plt.show()

def notchFilter(arr,state):
	# This is to remove the AC mains noise interference	of frequency of 50Hz(India)
	notch_freq_Hz = np.array([50.0])  # main + harmonic frequencies
	for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each target freq
		bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
		b, a = signal.butter(3, bp_stop_Hz/(250 / 2.0), 'bandstop')
		notchOutput, state = signal.lfilter(b, a, arr, zi=state)
		return notchOutput, state

def removeDCOffset(arr,state):
# This is to Remove The DC Offset By Using High Pass Filters
	hp_cutoff_Hz = 1.0 # cuttoff freq of 1 Hz (from 0-1Hz all the freqs at attenuated)
	b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
	dcOutput, state = signal.lfilter(b, a, arr, zi=state)
	return dcOutput, state


iterations = 5
Zstate = {}
Zstate['notch'] = {}
Zstate['dc_offset'] = {}
for c in range(8):
	Zstate['notch'][c] = [0,0,0,0,0,0]
	Zstate['dc_offset'][c] = [0,0]
notchO = []
print("The recording starts in 3")
time.sleep(1)
print("The recording starts in 2")
time.sleep(1)
print("The recording starts in 1")
time.sleep(1)
#for i in range(iterations):	
while True:
	notch_0 = []
	notch_1 = []
	for k in range(2):
		if(k == 0):
			#print("Please Dont Blink for "+str(iterations)+" seconds")
			print("Please Blink")
			print("Start")
		if(k == 1):
			print("Please start Blinking")
			print("Start")
		for i in range(iterations):	
		#while True:
			rawData = ds.read_chunk()
			c = 0
			rawData = rawData[0,:,0].reshape(-1)
			dcOutput, Zstate['dc_offset'][c] = removeDCOffset(rawData,Zstate['dc_offset'][c])
			notchOutput, Zstate['notch'][c]  = notchFilter(dcOutput,Zstate['notch'][c])
			if(k == 0):
				notch_0.append(notchOutput)
			else:
				notch_1.append(notchOutput)
			spec = mlab.specgram(notchOutput)[0]
			spec = torch.from_numpy(spec).reshape(1,129,1)
			model = model.double()
			x = model(spec).argmax().item()
			if(x == 0):
				print("No Blink")
			else:
				print("Blink")
		
	x = np.array(notch_0).reshape(-1,250)
	y = np.array(notch_1).reshape(-1,250)
	d = np.vstack((x,y)).reshape(-1)
	plt.plot(d)
	for i in range(0,d.shape[-1],250):
		plt.axvline(i,color="red")
		plt.text(i+0.95,0.01,"HEllo",verticalalignment="bottom",horizontalalignment="left")
	plt.draw()
	inp = raw_input("trainData?: ")
	plt.clf()
	if(inp == 'y'):
		specOut = []
		for sample in x:
			spec = mlab.specgram(sample)[0].reshape(-1)
			spec = np.append(spec,np.array([0]))
			specOut.append(spec)
		for sample in y:
			spec = mlab.specgram(sample)[0].reshape(-1)
			spec = np.append(spec,np.array([1]))
			specOut.append(spec)
		specOut = np.array(specOut)
		trainer.train(specOut,1)
os._exit(0)
