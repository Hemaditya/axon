import time
import psutil
import matplotlib.pyplot as plt

fig1 = plt.figure(1)
ax1 = fig1.add_subplot(111)
fig1.show()

fig2 = plt.figure(2)
ax2 = fig2.add_subplot(111)
fig2.show()

i = 0
x1,x2,y1,y2 = [], [], [], []

def plot1():
	global i
	x1.append(i)
	y1.append(psutil.cpu_percent())
    
 	ax1.plot(x1, y1, color='b')
	fig1.canvas.draw()
	ax1.set_xlim(left=max(0, i-50), right=i+50)
	#time.sleep(0.1)
	

def plot2():
	global i
	x2.append(i)
	y2.append(psutil.cpu_percent())

	ax2.plot(x2, y2, color='b')
	fig2.canvas.draw()
	ax2.set_xlim(left=max(0, i-50), right=i+50)
	#time.sleep(0.1)

while True:
    plot1()
    plot2()
    i += 1

plt.close()