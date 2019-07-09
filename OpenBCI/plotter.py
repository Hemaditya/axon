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

a = QtGui.QApplication([])
# Channels to be plotted
# if only one channel to be plotted , channels = [0]
channels = [0,1,2,3,4,5,6,7]
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
mode = 1
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

def create_plots(channels):
	plots = []
	curves = []
	win = pg.GraphicsWindow()
	gb_windows.append(win)
	for c in channels:
		plot = win.addPlot(title="Channel "+str(c))
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
		item.setLookupTable(lut)
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
if mode == 1:
	all_plots, all_curves = create_plots(channels)


# Initialize the processing stream
appObj = app.DataStream(chunk_size=250,b_times=1,spec_analyse=1,spectrogramWindow=300,NFFT=512)
# The below function will be run by thread t1
def runApp(count=None):
	if(count == None):
		while(True):
			appObj.read_chunk()
			appObj.process_raw(channels=channels)


# A thread to start processing of data
t1 = threading.Thread(target=runApp)
t1.start()
time.sleep(0.1)

# Main plotting function
def update():
	global channels, all_items

	if(mode == 1):
		for i in channels:
			all_curves[i].setData(appObj.plot_buffer['bandpass'][i])

	if(mode == 0):
		for i in channels:
			if(appObj.spec_True[i] == 1):
				all_items[i].setImage(appObj.plot_buffer['spectrogram'][i],autoLevels=False)
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
