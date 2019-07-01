import pyqtgraph as pg
import PyQt4 as p
import sys
import time
import numpy as np
from pyOpenBCI import OpenBCICyton

win = pg.GraphicsWindow()
p1 = win.addPlot()
curve = p1.plot(pen='r')

x = 1
y = 256
p1.setRange(xRange=[x,y])

rawBuffer = [0 for i in range(256)]

def update():
	global x,y,curveData,rawBuffer
	curve.setData(rawBuffer)
	x = x+1
	y = y+1
	#p1.setRange(xRange=[x,y])

def callback(d):
	cd = float(d.channels_data[0])

	rawBuffer[:-1] = rawBuffer[1:]
	rawBuffer[-1] = cd
	update()

board = OpenBCICyton(port='/dev/ttyUSB1', daisy=False)

def f():
	board.start_stream(callback)

t = p.QtCore.QTimer()
t.timeout.connect(f)
t.start(1)


if __name__ == '__main__':
	if(sys.flags.interactive != 1) or not hasattr(QtCore,'PYQT_VERSION'):
		app = pg.QtGui.QApplication.instance()
		app.exec_()
