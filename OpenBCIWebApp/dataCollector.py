import numpy as np
import matplotlib.pyplot as plt
import os

fig,(ax1,ax2) = plt.subplots(2,1)

notchPath = "NotchOutputFiles/"
blinkPath = "BlinkData/"
nbPath = "NBData/"
plt.ion()
plt.show()

blinkIndex = 0
nbIndex = 0

def plot_data(data):
	global blinkIndex,nbIndex,ax1,ax2
	while(True):
		print(data.shape)
		ax1.clear()
		ax2.clear()
		ax1.plot(data)	
		plt.draw()
		ques = raw_input("Enter your choice (x/d/q): ")
		if(ques == 'x'):
			x1 = int(raw_input("Enter Cutt: "))
			x2 = x1+125
			ax1.axvline(x1)
			ax1.axvline(x2)
			ax2.plot(data[x1:x2+1])
			plt.draw()
			newData = data[x1:x2+1].reshape(-1)
			cuttFor = raw_input("Enter choice(EYE_BLINK(e)/NOT_EYE_BLINK(n)): ")	
			if(cuttFor == "e"):
				confirm = raw_input("Enter choice(y/n): ")
				if(confirm == 'y'):
					np.save(blinkPath+"blink_"+str(blinkIndex),newData)
					blinkIndex = blinkIndex+1
					print("DATA SAVED")
				else:
					print("DATA NOT SAVED")
					continue
			elif(cuttFor == "n"):
				confirm = raw_input("Confirm?(y/n): ")
				if(confirm == 'y'):
					np.save(nbPath+"nb_"+str(nbIndex),newData)
					nbIndex = nbIndex + 1
					print("DATA SAVED")
				else:
					print("DATA NOT SAVED")
					continue
			data = np.delete(data,np.arange(x1,x2+1))

		elif(ques == 'q'):
			break
	pass

def preprocessData():
	for f in os.listdir(notchPath):	
		data = np.load(notchPath+f)
		data = data[0].reshape(-1)
		plot_data(data)

preprocessData()

