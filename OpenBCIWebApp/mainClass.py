import sys
import app
from matplotlib.pyplot import cla
import pickle
import numpy as np
import json
import os
import time
import matplotlib.pyplot as plt
from scipy import signal
import learner

class BCIWebApp(app.DataStream):
	
	def __init__(self,port=None,daisy=False,chunk_size=250,b_times=1,n_channels=8,spec_analyse=1, NFFT=512, filters=None, channels='all', spectrogramWindow=1000):
		app.DataStream.__init__(self, port=port, chunk_size=chunk_size,b_times=b_times,n_channels=n_channels,spec_analyse=spec_analyse,NFFT=NFFT,channels=channels)
		self.ELECTRODE_THRESHOLD = 50000
		self.path = "Sessions/"
		self.max = np.array([-999999999999])
		self.randomSessions = "RandomSessions/"
		self.userInfoFile = "UserInformation.pickle"
		self.lastSession = ""
		self.LState = {}


	def check_electrode_connectivity(self):
		# Since there is only one chunk in each buffer use only the first element from data_buffer
		avg = self.check_average_of_each_electrode()
		avg = (abs(avg) <= self.ELECTRODE_THRESHOLD)
		return avg

	def check_average_of_each_electrode(self):
		data = self.data_buffer[0]
		data = np.average(data,axis=0)
		return data

	def createNewUserId(self, obj):
		newId = str(hash(obj['email']))
		if('-' in newId):
			newId = newId.replace('-','0')
		
		obj['dir'] = self.path + obj['email']+'-'+newId + '/'
		with open("UserInformation.pickle",'rb') as f:
			data = pickle.load(f)
		data[newId] = obj
		with open("UserInformation.pickle",'wb') as f:
			pickle.dump(data, f)

		# Create a folder for the user
		os.mkdir(obj['dir'])	

		return obj

	def user_exists(self, email):
		with open(self.userInfoFile,'rb') as f:
			data = pickle.load(f)
		Id = str(hash(email)).replace('-','0')
		if(Id in data.keys()):
			return data[Id]
		else:
			return False
			
	def GenerateUserDict(self,name,age,gender,email):
		obj = {}
		obj['name'] = name
		obj['age'] = age
		obj['gender'] = gender
		obj['email'] = email
		return obj
	

	def recordEyeBlinkSession(self,iterations,obj=None):
		if(obj != None):
			path = obj['dir']+'EYE_BLINK/'
			if os.path.exists(path) == False:
				os.mkdir(path)
			else:
				pass

			timestr = time.strftime("%d%m%Y-%H%M%S")
			path = path+timestr+"/"
			os.mkdir(path)

		dataBuffer = []
		print("Wait 3 seconds")
		for i in range(3):	
			self.read_chunk()	
		print("Data recording is starting")
		j = 0
		for i in range(iterations):
			if(i >= iterations/2):
				#print("BLINK PLEASE!!!!!!!!!")
				pass
			else:
				#print("DONT BLINK!!!!!!!!!!!!")
				pass
			j = (j+1)%5
			self.read_chunk()	
			dataBuffer.append(self.data_buffer)	
		dataBuffer = np.squeeze(np.array(dataBuffer))
		if(obj == None):
			return dataBuffer
		np.save(path+"rawData",dataBuffer)
		self.lastSession = path

		#def normalization(self,

	def pureFFT(self,arr,NFFT=256):
		fftOutput = abs(np.fft.rfft(arr))
		#m = np.max(fftOutput)
		#if(m > self.max):
		#	self.max = m
		#fftOutput = fftOutput/self.max
		#return np.square(fftOutput)/np.sum(np.square(fftOutput))
		return fftOutput/25000.0

	def seperateBands(self,fftOutput,NFFT=250):
		x = np.fft.rfftfreq(250) * 250.0
		delta = np.sum(fftOutput[np.where(np.logical_and(x>=1,x<=3))])
		theta = np.sum(fftOutput[np.where(np.logical_and(x>=4,x<=8))])
		alpha = np.sum(fftOutput[np.where(np.logical_and(x>=8,x<=14))])
		beta = np.sum(fftOutput[np.where(np.logical_and(x>=15,x<=25))])
		gamma = np.sum(fftOutput[np.where(np.logical_and(x>=30,x<=45))])
		
		bandValues = np.array([delta,theta,alpha,beta,gamma])
		print(bandValues)
		#plt.plot(delta)
		#plt.plot(theta)
		#plt.plot(alpha)
		#plt.plot(beta)
		#plt.plot(gamma)
		#plt.show()
		
		return bandValues
			
	def notchFilter(self,arr,state):
		# This is to remove the AC mains noise interference	of frequency of 50Hz(India)
		notch_freq_Hz = np.array([50.0])  # main + harmonic frequencies
		for freq_Hz in np.nditer(notch_freq_Hz):  # loop over each target freq
			bp_stop_Hz = freq_Hz + 3.0*np.array([-1, 1])  # set the stop band
			b, a = signal.butter(3, bp_stop_Hz/(250 / 2.0), 'bandstop')
			notchOutput, state = signal.lfilter(b, a, arr, zi=state)
			return notchOutput, state

	def removeDCOffset(self,arr,state):
	# This is to Remove The DC Offset By Using High Pass Filters
		hp_cutoff_Hz = 1.0 # cuttoff freq of 1 Hz (from 0-1Hz all the freqs at attenuated)
		b, a = signal.butter(2, hp_cutoff_Hz/(250 / 2.0), 'highpass')
		dcOutput, state = signal.lfilter(b, a, arr, zi=state)
		return dcOutput, state
		

	def applyFilters(self, session=None,Data=None,r=False):
		# Here since the data being loaded is for an entire 
		if(session != None):
			data = np.load(self.lastSession+"/rawData"+".npy")
		else:
			data = Data
		notchFilterOutput = []
		dcOffsetOutput = []
		Zstate = {}
		Zstate['notch'] = {}
		Zstate['dc_offset'] = {}
		for c in range(self.n_channels):
			Zstate['notch'][c] = [0,0,0,0,0,0]
			Zstate['dc_offset'][c] = [0,0]
			dcOutputPerChannel = []
			notchOutputPerChannel = []
			for	i in range(data.shape[0]):
				rawData = data[i,:,c].reshape(-1)
				dcOutput, Zstate['dc_offset'][c] = self.removeDCOffset(rawData,Zstate['dc_offset'][c])
				dcOutputPerChannel.append(dcOutput)
				notchOutput, Zstate['notch'][c]  = self.notchFilter(dcOutput,Zstate['notch'][c])
				notchOutputPerChannel.append(notchOutput)
			notchFilterOutput.append(notchOutputPerChannel)	
			dcOffsetOutput.append(dcOutputPerChannel)
		notchFilterOutput = np.array(notchFilterOutput)
		dcOffsetOutput = np.array(dcOffsetOutput)
		if(r==True):
			return(notchFilterOutput, dcOffsetOutput)
		print(notchFilterOutput.shape)
		print(dcOffsetOutput.shape)
		np.save(self.lastSession+"notchFilterOutput",notchFilterOutput)
		np.save(self.lastSession+"dcOffsetOutput",dcOffsetOutput)
			

	def plotData(self,session=None,Data=None,channel=0,dataType="rawData"):
		if(session != None):
			data = np.load(self.lastSession+"/"+dataType+".npy")
			plotData = []
			if(dataType == "rawData"):
				plotData = data[:,:,channel].reshape(-1)
			else:
				plotData = data[channel,:,:].reshape(-1)
			plt.plot(plotData)
			plt.show()


	def start_session(self,iterations=60,action="EYE_BLINK",plot=False,randomData=False):

		obj = {}
		if randomData == False:
			# First get Credentials
			email = raw_input("Enter email: ")
			Id = None

			# Check if the Id exists
			check = self.user_exists(email)
			if(check != False):
				obj = check
			else:
				name = raw_input("enter your name: ")
				age = int(raw_input("enter your age: "))
				gender = raw_input("enter gender (m/f): ")
				obj = self.GenerateUserDict(name,age,gender,email)
				obj = self.createNewUserId(obj)

		else:
			obj['dir'] = self.randomSessions
		self.recordEyeBlinkSession(iterations,obj)
		self.applyFilters(True)

		notchData = np.load(self.lastSession+"notchFilterOutput.npy")[0]
		print(notchData.shape)
		#fftData = []
		#for each in notchData:
		#	fftOutput = self.pureFFT(each)	
		#	fftData.append(self.seperateBands(fftOutput))
		#fftData = np.array(fftData[1:])
		##print(fftData.shape)
		#plt.ion()
		#plt.show()
		#
		##plt.plot(fftData[:,0])
		#plt.plot(fftData[:,1])
		##plt.plot(fftData[:,2])
		##plt.plot(fftData[:,3])
		##plt.plot(fftData[:,4])
		#plt.draw()


		#timestr = time.strftime("%Y%m%d_%H%M%S")
		#newPath = "./FFT/"+timestr
		#x = raw_input("Do you want to save data: ")
		#if(x == 'y'):
		#	np.save(newPath,fftData)	
		#else:
		#	pass

		#if(plot == True):
		#	self.plotData(True,dataType="notchFilterOutput")

def checkElectrodeConnectivity(x):
	i = 0
	while(True):
		_ = x.read_chunk(ck=50)
		conn = x.check_electrode_connectivity()
		if(conn.all() == True):
			i = i+1
			print("All Connected")
		else:
			i = 0
			indices = np.array(np.nonzero(conn == False))
			print("Channels: ",np.array2string(indices,separator=',').strip('[]')," are not connected")
		if(i >= 15):
			break


blinkPath = "completeNewSession/BLINK_DATA/"
nbPath = "completeNewSession/NB_DATA/"
ImageBlinkPath = "ImageData/BLINK_DATA/"
ImageNbPath = "ImageData/NB_DATA/"

def startDataCollection(x,iterations=60,localData=False,uniform=False):
	plt.ion()
	plt.show()
	plt.hold(False)
	timestr = time.strftime("%Y%m%d_%H%M%S")
	path = timestr+"-"+"notchOutput"

	if localData == False:
		rawData = x.recordEyeBlinkSession(iterations,obj=None)
		nO,dO = x.applyFilters(Data=rawData,r=True)

		if(uniform == True):
			for i in range(iterations):
				plt.plot(nO[0,i,:].reshape(-1))
				plt.draw()	
				x = raw_input("Enter choice: ")
				if(x.lower() == 'y'):
					np.save(blinkPath+path+"-"+str(i),nO[:,i,:])
					plt.savefig(ImageBlinkPath+path+str(i)+".png")
				elif(x.lower() == 'n'):
					np.save(nbPath+path+"-"+str(i),nO[:,i,:])
					plt.savefig(ImageNbPath+path+str(i)+".png")
				plt.clf()

		else:
			fig, (ax1,ax2) = plt.subplots(2,1)
			nData = nO[0,:,:].reshape(-1)
			ax1.plot(nData)
			plt.draw()
			print(nData)
			x1 = 0
			x2 = 0
			eyeBlinkData = []
			nbData = []
			k = None
			#plt.clf()
			while(k != 'q'):
				ax1.plot(nData)
				plt.draw()
				k = raw_input("Enter (y/n/d/q): ")
				if(k == 'q'):
					break
				elif(k == 'd'):
					continue
				elif(k == 'y'):
					x1,x2 = map(int,raw_input("Enter two points: ").split())
					ax1.axvline(x=x1)
					ax1.axvline(x=x2)
					ax2.plot(nData[x1:x2+1])
					plt.draw()

					k = raw_input("Confirm: ")
					if(k == 'n'):
						plt.cla()
						continue
					eyeBlinkData.append(nData[x1:x2+1])
					nData = np.delete(nData,np.array(range(x1,x2+1)))
					ts = time.strftime("%Y%m%d_%H%M%S")
					ja = ts+"-"+"notchOutput"
					plt.savefig(ImageBlinkPath+ja+".png")

				elif(k == 'n'):
					x1,x2 = map(int,raw_input("Enter two points: ").split())
					ax1.axvline(x=x1)
					ax1.axvline(x=x2)
					ax2.plot(nData[x1:x2+1])
					plt.draw()
					k = raw_input("Confirm: ")
					if(k == 'n'):
						plt.cla()
						continue
					nbData.append(nData[x1:x2+1])
					np.delete(nData,np.array(range(x1,x2+1)))
					ts = time.strftime("%Y%m%d_%H%M%S")
					ja = ts+"-"+"notchOutput"
					plt.savefig(ImageNbPath+ja+".png")
					
				plt.cla()
			
			np.save(blinkPath+path,np.array(eyeBlinkData))
			np.save(nbPath+path,np.array(nbData))

	else:
		folder = "RandomSessions/EYE_BLINK/"
		dirs = os.listdir(folder)
		for d in dirs:
			files = os.listdir(folder+d+"/")
			for f in files:
				if "notch" in f:
					nO = np.load(folder+d+"/"+f)
					iterations = nO.shape[1]
					for i in range(iterations):
						plt.plot(nO[0,i,:].reshape(-1))
						plt.draw()	
						x = raw_input("Enter choice: ")
						if(x.lower() == 'y'):
							np.save(blinkPath+path+"-"+str(i),nO[:,i,:])
							plt.savefig(ImageBlinkPath+path+str(i)+".png")
						elif(x.lower() == 'n'):
							np.save(nbPath+path+"-"+str(i),nO[:,i,:])
							plt.savefig(ImageNbPath+path+str(i)+".png")
						else:
							#Discard
							pass
						plt.clf()

	#	else:
	#		fig, (ax1,ax2) = plt.subplots(2,1)
	#		nData = nO[0,:,:].reshape(-1)
	#		x1 = 0
	#		x2 = 0
	#		eyeBlinkData = []
	#		nbData = []
	#		k = None
	#		while(k != 'q'):
	#			ax1.plot(nData)
	#			plt.draw()
	#			k = raw_input("Enter (y/n/d/q): ")
	#			if(k == q):
	#				break
	#			elif(k == 'd'):
	#				continue
	#			elif(k == 'y'):
	#				x1,x2 = map(int,raw_input("Enter two points: ").split())
	#				ax1.axvline(x=x1)
	#				ax1.axvline(x=x2)
	#				ax2.plot(nData[x1:x2+1])
	#				plt.draw()

	#				k = raw_input("Confirm: ")
	#				if(k == 'n'):
	#					continue
	#				eyeBlinkData.append(nData[x1:x2+1])
	#					np.delete(nData,np.array(range(x1,x2+1)))
	#				ts = time.strftime("%Y%m%d_%H%M%S")
	#				ja = ts+"-"+"notchOutput"
	#				plt.savefig(ImageBlinkPath+ja+".png")

	#			elif(k == 'n'):
	#				x1,x2 = map(int,raw_input("Enter two points: ").split())
	#				ax1.axvline(x=x1)
	#				ax1.axvline(x=x2)
	#				ax2.plot(nData[x1:x2+1])
	#				plt.draw()
	#				k = raw_input("Confirm: ")
	#				if(k == 'n'):
	#					continue
	#				nbData.append(nData[x1:x2+1])
	#					np.delete(nData,np.array(range(x1,x2+1)))
	#				ts = time.strftime("%Y%m%d_%H%M%S")
	#				ja = ts+"-"+"notchOutput"
	#				plt.savefig(ImageNbPath+ja+".png")
	#				
	#		
	#		
	#		np.save(blinkPath+path,np.array(eyeBlinkData))
	#		np.save(nbPath+path,np.array(nbData))
			
			


x = BCIWebApp(chunk_size=250)
if(os.path.exists('UserInformation.pickle')):
	pass
else:
	with open('UserInformation.pickle','wb') as f:
		data = {}
		pickle.dump(data,f)

#checkElectrodeConnectivity(x)
print("Starting the session in 5 seconds")
#time.sleep(5)
x.start_session(iterations=10,plot=False,randomData=True)
#startDataCollection(x,iterations=10,uniform=False)
os._exit(0)
