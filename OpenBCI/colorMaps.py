# Trial - Error color Maps for random data

import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui 
import numpy as np
import time
import matplotlib.pyplot as plt

win = pg.GraphicsWindow(title='color maps')

p1 = win.addPlot()
pos = np.array([0.0,1.0,0.5])
colors = np.array([[255,0,0,255],[255,255,0,255],[0,255,255,255]], dtype=np.ubyte)

cmap = pg.ColorMap(pos, colors)
lut = cmap.getLookupTable(0.0,1.0,256)

item = pg.ImageItem()
p1.addItem(item)
item.setLookupTable(lut)

l = [np.arange(0,256) for i in range(3)]
l = np.array(l)

#x = np.array([lut for i in range(1)]).reshape(10,1,3)
item.setImage(l)
#print(x.shape)
#plt.imshow(x)
#plt.show()
##print(item.getHistogram())



if __name__ == '__main__':
	import sys
	if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()

