import time
from pyOpenBCI import OpenBCICyton
import matplotlib.pyplot as plt

fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111)
fig1.show()

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111)
fig2.show()


i = 0
x1,x2,y1,y2 = [], [], [], []

def plot1(x,y):
	global i
	x1.append(x)
	y1.append(y)
    
 	ax1.plot(x1, y1, color='b')
	fig1.canvas.draw()
	ax1.set_xlim(left=max(0, i-50), right=i+50)
	#time.sleep(0.1)

def plot2(x,y):
	global i
	x2.append(x)
	y2.append(y)

	ax2.plot(x2, y2, color='b')
	fig2.canvas.draw()
	ax2.set_xlim(left=max(0, i-50), right=i+50)
	#time.sleep(0.1)

def print_raw(sample):
	global i
	#print(sample.channels_data[0] * (4.5)/24/(2**23-1))
	plot1(i,(sample.channels_data[0] * ((4.5)/24/(2**23-1))))
	plot2(i,(sample.channels_data[1] * ((4.5)/24/(2**23-1))))
	i += 1

board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)

board.start_stream(print_raw)
