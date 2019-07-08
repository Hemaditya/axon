# This file is runs the main thread. Is responsible for plotting data
import app
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import time


win = pg.GraphicsWindow(title='Plot')
win.resize(1000,600)
view = win.addPlot()
# Spectrogram Initialization
pos = np.array([0., 1., 0.5, 0.25, 0.75])
color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
cmap = pg.ColorMap(pos, color)
lut = cmap.getLookupTable(0.0, 1.0, 256)
item = pg.ImageItem()
view.addItem(item)
item.setLookupTable(lut)
item.setLevels([-50,40])
# The below 4 lines are for plotting filter_outputs
#p1.setClipToView(True)
#p1.setRange(xRange=[0,60])
#p1.setRange(yRange=[-50,50])
#curve = p1.plot(pen='y')

# Initialize the processing stream
appObj = app.DataStream(chunk_size=50,b_times=8,spec_analyse=5)
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
	# The below 4 lines are for plotting filter_outputs
	#if(appObj.plot_buffer['spectral_analysis'].shape[0] == appObj.window_size * appObj.spec_analysis):
	#	curve.setData(appObj.plot_buffer['spectral_analysis']
	#if appObj.g == 1:
	#	curve.setData(appObj.plot_buffer['spec_freqs'],appObj.plot_buffer['spec_analyser'])

	if(appObj.spec_True == 1):
		item.setImage(appObj.plot_buffer['spectrogram'],autoLevels=False)
		appObj.spec_True = 0
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
