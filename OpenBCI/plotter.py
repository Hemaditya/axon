import app
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import time

win = pg.GraphicsWindow(title='Plot')
win.resize(1000,600)
p1 = win.addPlot(title="LivePlot")
p1.setClipToView(True)
#p1.setRange(xRange=[0,60])
curve = p1.plot(pen='y')

appObj = app.DataStream(chunk_size=50,b_times=8,spec_analyse=20)
def runApp(count=None):
	if(count == None):
		while(True):
			appObj.read_chunk()
			appObj.process_raw()

t1 = threading.Thread(target=runApp)
t1.start()
time.sleep(0.1)

def update():
	#if(appObj.plot_buffer['spectral_analysis'].shape[0] == appObj.window_size * appObj.spec_analysis):
	#	curve.setData(appObj.plot_buffer['spectral_analysis']
	if appObj.g == 1:
		curve.setData(appObj.plot_buffer['spec_freqs'],appObj.plot_buffer['spec_analyser'])
	pass
	
	
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)

if __name__ == '__main__':
	import sys
	if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()

t1.join()
