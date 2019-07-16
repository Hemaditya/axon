# This file is runs the main thread. Is responsible for plotting data
import app
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import colot as ct
import matplotlib.pyplot as plt
from matplotlib import cm
import time
import math

a = QtGui.QApplication([])
# Channels to be plotted
# if only one channel to be plotted , channels = [0]
channels = [0]
#pos = np.array([0., 1., 0.5, 0.25, 0.75])
#color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
pos = np.arange(0,1,1/256.0)
cmap = pg.ColorMap(pos, ct.lut_cubehelix)
lut = cmap.getLookupTable(0.0, 1.0, 256)
colormap = cm.get_cmap('nipy_spectral')
colormap._init()
lookup = (colormap._lut * 255).view(np.ndarray)
gb_windows = []
# mode = 1, plot bandpass
# mode = 0, plot spectrogram
mode = 0
all_plots = []
all_curves = []
all_windows = []
all_items = []

# Test code
#x = pg.GraphicsWindow()
#plot = x.addPlot()
#i = pg.ImageItem()
#plot.addItem(item)
#i.setImage(lut)


def create_plots(channels, bandpass=False):
	plots = []
	curves = []
	win = pg.GraphicsWindow()
	gb_windows.append(win)
	for c in channels:
		plot = win.addPlot(title="Channel "+str(c))
		if(bandpass == True):
			plot.setLogMode(True,False)
			plot.setRange(yRange=[-50,40])
		curve = plot.plot()
		curves.append(curve)
		plots.append(plot)
		win.nextRow()
	return plots, curves	

def create_spectrogram(channels):
	global pos, color, cmap, lut
	windows = []
	imageItems = []
	win = pg.GraphicsWindow()
	gb_windows.append(win)
	for c in channels:
		if((c+1)%3 == 0):
			win.nextRow()
		plot = win.addPlot()
		windows.append(plot)
		item = pg.ImageItem()
		imageItems.append(item)
		item.setLevels([-50,40])
		windows[-1].addItem(item)
		item.setLookupTable(lookup)
		item.setLevels([-50,40])
	return windows,imageItems

def create_windows(channels):
	global pos, color, cmap, lut, gb_windows
	gb_windows
	windows = []
	imageItems = []
	for c in channels:
		win = pg.GraphicsWindow(title="Channel-"+str(c))
		gb_windows.append(win)
		plot = win.addPlot()
		windows.append(plot)
		item = pg.ImageItem()
		imageItems.append(item)
		windows[-1].addItem(item)
		item.setLookupTable(ct.lut_cubehelix)
	return windows,imageItems

if mode == 0:
	all_windows,all_items = create_spectrogram(channels)
if mode == 1 or mode == 2:
	all_plots, all_curves = create_plots(channels,bandpass=True)


# Initialize the processing stream
appObj = app.DataStream(chunk_size=125,b_times=1,spec_analyse=1,spectrogramWindow=100,NFFT=256)
# The below function will be run by thread t1
def runApp(count=None):
	if(count == None):
		while(True):
			x = 'y'
			if(x.lower() != 'y' and x.lower() != 'n'):
				print("Enter proper value")
			else:
				if(x.lower() == 'y'):
					appObj.actionVariables['EYE_BLINK'] = 1
				if(x.lower() == 'n'):
					appObj.actionVariables['EYE_BLINK'] = 0
				appObj.read_chunk()
				appObj.process_raw(channels=channels)
				x = appObj.record_buffer['EYE_BLINK'][appObj.currentChannel][-1][0]
				y = appObj.record_buffer['EYE_BLINK'][appObj.currentChannel][-2][0]
				dot = np.sum(np.dot(x,y))
				print(dot)
				sqrt1 = math.sqrt(np.sum(np.dot(x,x)))
				sqrt2 = math.sqrt(np.sum(np.dot(y,y)))
				cos = math.acos(dot/(sqrt1*sqrt2))
				print("The distance bewteen previous two data: ",np.linalg.norm(x-y))



# A thread to start processing of data
t1 = threading.Thread(target=runApp)
t1.start()
time.sleep(0.1)

# Main plotting function
def update():
	global channels, all_items

	if(mode == 2):
		for i in channels:
			if(appObj.spec_True[i] == 1):
				freqsIndices = np.argwhere(appObj.plot_buffer['spec_freqs'][i] <= 60)
				freqs = appObj.plot_buffer['spec_freqs'][i][freqsIndices].reshape(-1)
				amp = appObj.plot_buffer['spectrum'][i][freqsIndices].reshape(-1)
				
				all_curves[i].setData(freqs,amp)
				appObj.spec_True[i] = 0

	if(mode == 1):
		for i in channels:
			all_curves[i].setData(appObj.plot_buffer['bandpass'][i])

	if(mode == 0):
		for i in channels:
			if(appObj.spec_True[i] == 1):
				print(appObj.plot_buffer['spec_freqs'][i].shape)
				all_items[i].setImage(appObj.plot_buffer['spectrogram_last'][i],autoLevels=False)
				appObj.spec_True[i] = 0
		pass
	
# PyQTgraph initialization

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)

if __name__ == '__main__':
	import sys
	if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()

t1.join()
