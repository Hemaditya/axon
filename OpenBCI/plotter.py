# This file is runs the main thread. Is responsible for plotting data
import app
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import matplotlib.pyplot
import time

channels = [0,1]
pos = np.array([0., 1., 0.5, 0.25, 0.75])
color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
cmap = pg.ColorMap(pos, color)
lut = cmap.getLookupTable(0.0, 1.0, 256)
gb_windows = []
mode = 0

all_windows = []
all_items = []
all_plots = []
all_curves = []

def create_plots(channels):
	plots = []
	curves = []
	win = pg.GraphicsWindow(title="Bandpass")
	gb_windows.append(win)
	for c in channels:
		plot = win.addPlot(title="Channel "+str(c))
		plots.append(plot)
		curve = plots[-1].plot()
		curves.append(curve)
		win.nextRow()
	return plots, curves

def create_spectrograms(channels):
	global pos, color, cmap, lut
	windows = []
	imageItems = []
	win = pg.GraphicsWindow(title="Giant Plot")
	gb_windows.append(win)
	for c in channels:
		if((c+1)%3 == 0):
			win.nextRow()
		plot = win.addPlot(title="Channel "+str(c))	
		windows.append(plot)
		item = pg.ImageItem()
		imageItems.append(item)
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
		item.setLookupTable(lut)
		item.setLevels([-50,40])
	return windows,imageItems

if(mode == 0):
	all_windows,all_items = create_spectrograms(channels)
if(mode == 1):
	all_plots, all_curves = create_plots(channels)

#Spectrogram Initialization
#item = pg.ImageItem()
#p1.addItem(item)
#item.setLookupTable(lut)
#item.setLevels([-50,100])
# The below 4 lines are for plotting filter_outputs
#p1.setClipToView(True)
#p1.setRange(xRange=[0,60])
#view.setRange(yRange=[0,100])
#curve = p1.plot(pen='y')

# Initialize the processing stream
#appObj = app.DataStream(chunk_size=50,b_times=8,spec_analyse=5,spectrogramWindow=300)
appObj = app.DataStream(chunk_size=250,b_times=1,spec_analyse=1,spectrogramWindow=300)
# The below function will be run by thread t1
def runApp(count=None):
	if(count == None):
		while(True):
			appObj.read_chunk()
			appObj.process_raw()


# A thread to start processing of data
t1 = threading.Thread(target=runApp)
t1.start()
time.sleep(0.1)

# Main plotting function
def update():
	global channels, all_items,all_curves
	# The below 4 lines are for plotting filter_outputs
	#if(appObj.plot_buffer['spectral_analysis'].shape[0] == appObj.window_size * appObj.spec_analysis):
	#	curve.setData(appObj.plot_buffer['spectral_analysis']
	#if appObj.g == 1:
	#	curve.setData(appObj.plot_buffer['spec_freqs'],appObj.plot_buffer['spec_analyser'])
	 #The below 4 lines are for plotting filter_outputs
#	if(appObj.plot_buffer['spectral_analysis'].shape[0] == appObj.window_size * appObj.spec_analysis):
#		curve.setData(appObj.plot_buffer['spectral_analysis']
#	if appObj.g == 1:
#		curve.setData(appObj.plot_buffer['spec_freqs'],appObj.plot_buffer['spec_analyser'])
	if(mode == 1):	
		for i in channels:
			all_curves[i].setData(appObj.plot_buffer['bandpass'][i])

	if(mode == 0):
		for i in channels:
			if(appObj.spec_True[i] == 1):
				all_items[i].setImage(appObj.plot_buffer['spectrogram'][i][:,:60],autoLevels=False)
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
