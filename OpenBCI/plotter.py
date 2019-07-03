import app
import threading
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
import time

win = pg.GraphicsWindow(title='Plot')
win.resize(600,400)
view = win.addViewBox()
#p1.setClipToView(True)
#p1.setRange(xRange=[0,60])
#p1.setRange(yRange=[-50,50])
#curve = p1.plot(pen='y')
#pos = np.array([0., 1., 0.5, 0.25, 0.75])
#color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
##color = np.array([[0,0,255,255], [255,255,0,255], [0,0,0,255] ], dtype=np.ubyte)
#cmap = pg.ColorMap(pos, color)
#lut = cmap.getLookupTable(0.0, 1.0, 256)

pos = np.array([0., 1., 0.5, 0.25, 0.75])
color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
cmap = pg.ColorMap(pos, color)
lut = cmap.getLookupTable(0.0, 1.0, 256)
#
#        self.img.setLookupTable(lut)
#        self.img.setLevels([-50,40])
item = pg.ImageItem()
view.addItem(item)
item.setLookupTable(lut)
item.setLevels([-50,40])

#$imv.setLookupTable(lut)
#$imv.setLevels([-50,40])

appObj = app.DataStream(chunk_size=50,b_times=8,spec_analyse=5)
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
	#if appObj.g == 1:
	#	curve.setData(appObj.plot_buffer['spec_freqs'],appObj.plot_buffer['spec_analyser'])

	if(appObj.spec_True == 1):
		item.setImage(appObj.plot_buffer['spectrogram'],autoLevels=False)
		appObj.spec_True = 0
	pass
	
##class SpectrogramWidget(pg.PlotWidget):
#    read_collected = QtCore.pyqtSignal(np.ndarray)
#    def __init__(self):
#        super(SpectrogramWidget, self).__init__()
#
#        self.img = pg.ImageItem()
#        self.addItem(self.img)
#
#        self.img_array = np.zeros((1000, 512/2+1))
#
#        # bipolar colormap
#
#        pos = np.array([0., 1., 0.5, 0.25, 0.75])
#        color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
#        cmap = pg.ColorMap(pos, color)
#        lut = cmap.getLookupTable(0.0, 1.0, 256)
#
#        self.img.setLookupTable(lut)
#        self.img.setLevels([-50,40])
#
#        #freq = np.arange((CHUNKSZ/2)+1)/(float(CHUNKSZ)/FS)
#        #yscale = 1.0/(self.img_array.shape[1]/freq[-1])
#        #self.img.scale((1./FS)*CHUNKSZ, yscale)
#
#        self.setLabel('left', 'Frequency', units='Hz')
#
#        #self.show()
#
#	def update(self):
#		#if(appObj.plot_buffer['spectral_analysis'].shape[0] == appObj.window_size * appObj.spec_analysis):
#		#	curve.setData(appObj.plot_buffer['spectral_analysis']
#		#if appObj.g == 1:
#		#	curve.setData(appObj.plot_buffer['spec_freqs'],appObj.plot_buffer['spec_analyser'])
#
#		print("JAJAJAJ")
#		if(appObj.spec_True == 1):
#			self.img.setImage(appObj.plot_buffer['spectrogram'],autoLevels=False)
#			appObj.spec_True = 0
#		pass

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(1)

if __name__ == '__main__':
	import sys
	if(sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
		QtGui.QApplication.instance().exec_()

t1.join()
