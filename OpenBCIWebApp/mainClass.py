import sys
sys.path.append('../OpenBCI/')
import app
import pickle
import numpy as np
import json
import os
import time

class BCIWebApp(app.DataStream):
	
	def __init__(self,port=None,daisy=False,chunk_size=250,b_times=1,n_channels=8,spec_analyse=1, NFFT=512, filters=None, channels='all', spectrogramWindow=1000):
		app.DataStream.__init__(self, port=port, chunk_size=chunk_size,b_times=b_times,n_channels=n_channels,spec_analyse=spec_analyse,NFFT=NFFT,channels=channels)
		self.ELECTRODE_THRESHOLD = 50000
		self.path = "Sessions/"
		self.userInfoFile = "UserInformation.pickle"

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
		
		obj['dir'] = self.path + newId + '/'
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
	

	def recordEyeBlinkSession(self,iterations,obj):
		path = obj['dir']+'EYE_BLINK/'
		if os.path.exists(path) == False:
			os.mkdir(path)
		else:
			pass

		timestr = time.strftime("%d%m%Y-%H%M%S")
		path = path+timestr

		dataBuffer = []
		print("Wait 3 seconds")
		for i in range(3):	
			self.read_chunk()	
		print("Data recording is starting")
		j = 0
		with open(path, 'w') as f:
			for i in range(iterations):
				if(j == 4):
					print("BLINK PLEASE!!!!!!!!!")
				else:
					print("DONT BLINK!!!!!!!!!!!!")
				j = (j+1)%5
				time.sleep(0.1)
				self.read_chunk()	
				dataBuffer.append(self.data_buffer)	
		dataBuffer = np.array(dataBuffer)
		np.save(path,dataBuffer)
		

	def start_session(self,iterations=60,action="EYE_BLINK"):
		# First get Credentials
		email = raw_input("Enter email: ")
		Id = None
		obj = {}

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

		self.recordEyeBlinkSession(iterations,obj)

x = BCIWebApp()
if(os.path.exists('UserInformation.pickle')):
	pass
else:
	with open('UserInformation.pickle','wb') as f:
		data = {}
		pickle.dump(data,f)
i = 0
while(True):
	x.read_chunk(ck=50)
	conn = x.check_electrode_connectivity()
	#print(conn)
	if(conn.all() == True):
		i = i+1
		print("All Connected")
	else:
		i = 0
		indices = np.array(np.nonzero(conn == False))
		print("Channels: ",np.array2string(indices,separator=',').strip('[]')," are not connected")
	if(i >= 15):
		break
print("Starting the session in 5 seconds")
time.sleep(5)
x.start_session()
os._exit(0)
