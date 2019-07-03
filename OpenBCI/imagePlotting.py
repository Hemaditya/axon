import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import QtCore, QtGui

app = QtGui.QApplication([])
win = QtGui.QMainWindow()
win.resize(800,800)
imv = pg.ImageView()
win.setCentralWidget(imv)
win.show()
win.setWindowTitle('pyqtgraph example: ImageView')

img = np.random.uniform(0,1, size=(28,28,3))
imv.setImage(img)


if __name__ == '__main__':
	QtGui.QApplication.instance().exec_()

