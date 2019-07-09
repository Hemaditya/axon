import numpy as np
import pyqtgraph

from pyqtgraph import QtGui

from matplotlib import cm

QtGui.QApplication([])

glw = pyqtgraph.GraphicsLayoutWidget()
glw.show()

p = glw.addPlot(0, 0)

img = pyqtgraph.ImageItem()
p.addItem(img)

# Get the colormap
colormap = cm.get_cmap("nipy_spectral")  # cm.get_cmap("CMRmap")
colormap._init()
lut = (colormap._lut * 255).view(np.ndarray)  # Convert matplotlib colormap from 0-1 to 0 -255 for Qt

# Apply the colormap
img.setLookupTable(lut)

# dummy data
d = np.random.random_sample((1000, 1000))

img.updateImage(image=d, levels=(0, 1))

