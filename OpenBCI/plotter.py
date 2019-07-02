import app
import threading
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import time

win = pg.GraphicsWindow(title='Plot')
win.resize(1000,600)
p1 = win.addPlot(title="LivePlot")
p1.setClipToView(True)
p1.setRange(yRange=[-1000,1000])
curve = p1.plot(pen='y')

appObj = app.DataStream(chunk_size=20)
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
	#	curve.setData(appObj.plot_buffer['spectral_analysis'])
	curve.setData(appObj.filter_outputs['dc_offset'])
	
	
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)

if __name__ == '__main__':
	import sys
	if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()

t1.join()
