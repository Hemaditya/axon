import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import threading
import time
import newApp as na

win = pg.GraphicsWindow(title='Plot')
win.resize(1000,600)
p1 = win.addPlot(title="Channel 0")
p1.setClipToView(True)
x = 1
y = 100
p1.setRange(xRange=[x,y])
curve = p1.plot(pen='y')
window_size=200
data = [0 for i in range(window_size)]

t1 = threading.Thread(target=na.start)
t1.start()
time.sleep(0.1)

def update():
	global curve, p1, win, data, ptr, x, y
	data[:-1] = data[1:]
	if(na.plotBuffer.empty() == True):
		data.append(0)
	else:
		#data.append((na.plotBuffer.get()))
		data.append(na.plotBuffer.get())	
		curve.setData(data)
	
	x = x+1
	y = y+1
	p1.setRange(xRange=[x,y])

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(5)

if __name__ == '__main__':
	import sys
	if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()

t1.join()
