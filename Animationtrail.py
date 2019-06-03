import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import psutil

style.use('fivethirtyeight')

fig = plt.figure()
ax1 = fig.add_subplot(111)
xs = []
ys = []

def animate(i):
	graph_data = open('example.txt','r').read()
	lines = graph_data.split('\n')
	xs.append(i)
	ys.append(psutil.cpu_percent())
	ax1.plot(xs,ys)
	fig.canvas.draw()
	ax1.set_xlim(left=max(0, i-50), right=i+50)

ani = animation.FuncAnimation(fig, animate,interval = 5)
plt.show()