import numpy as np
from pyOpenBCI import OpenBCICyton
import queue
from scipy import signal 
import time

uVolts_per_count = (4.5)/24/(2**23-1)*1000000
q = queue.Queue(maxsize=1000)
board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)

rawBuffer = queue.Queue(maxsize=4096)
filterBuffer = queue.Queue(maxsize=320)
plotBuffer = queue.Queue(maxsize=100000)
call_count = 0

sample_count = 0
val = []
def remove_dc_offset():
	global filterBuffer
	listFilter = list(filterBuffer.queue)
	hp_cutoff_Hz = 1.0

	#print("Highpass filtering at: " + str(hp_cutoff_Hz) + " Hz")

	b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
	#print(b)
	#print(a)
	#print(self.data)
	data = signal.lfilter(b, a, listFilter, 0)
	return data[-64:]

def createFilterBuffer():
	global rawBuffer, filterBuffer, call_count
	listRaw = list(rawBuffer.queue)
	for each in listRaw:
		if(filterBuffer.full() == True):
			_ = filterBuffer.get()
		filterBuffer.put(each)
	last64Bytes = remove_dc_offset()
	for each in last64Bytes:
		plotBuffer.put(each)

def acquire_raw(sample):
	global val, sample_count, rawBuffer,call_count, plotBuffer
	#print("CALL COUNT: ",call_count)
	call_count = call_count+1
	#if(rawBuffer.full() == True):
	#		_ = rawBuffer.get()
	#rawBuffer.put(uVolts_per_count*sample.channels_data[0])
	val.append(uVolts_per_count*sample.channels_data[0])
	sample_count += 1

	time.sleep(0.001)

	if(sample_count == 64):
		sample_count = 0
		#createFilterBuffer()
		if(plotBuffer.full() == True):
			plotBuffer.get()
		for each in val:
			plotBuffer.put(each)
			print(each)
		val = []
	
def start():
	board.start_stream(acquire_raw)



