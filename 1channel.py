import time
from pyOpenBCI import OpenBCICyton
import matplotlib.pyplot as plt


# ax1 = fig1.add_subplot(111)
.show()

i = 0
x1,x2,y1,y2 = [], [], [], []

def plot1(x,y):
	global i
	x1.append(x)
	y1.append(y)
 	plt.plot(x1, y1, color='b')
	fig1.canvas.draw()
	fig1.set_xlim(left=max(0, i-50), right=i+50)
	#time.sleep(0.1)



def print_raw(sample):
	global i
	# print(sample.channels_data[0]) * (4.5)/24/(2**23-1)
	plot1(i,(sample.channels_data[0] * ((4.5)/24/(2**23-1)*1000000)))
	#plot2(i,(sample.channels_data[1] * ((4.5)/24/(2**23-1))))
	i += 1

board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)

board.start_stream(print_raw)