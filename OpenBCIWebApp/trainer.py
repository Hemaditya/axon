import torch
from torch.utils.data import DataLoader as DL
import torch.nn as nn
from torch.optim import Adam
import learner
import os

model = learner.NN()
model = torch.load('myModel')
model = model.double()

def train(data,c):
	#if(data.reshape(-1).shape[0] % 250 != 0):
	#	print("Data set not compatible for training")
	#	os._exit(0)
	#else:
	optimizer = Adam(model.parameters(),lr=3e-3)
	criterion = nn.NLLLoss()
	epochs = 50
	data = torch.from_numpy(data)
	raw = DL(data,shuffle=True,batch_size=1)	
	model.train()

	for e in range(epochs):
		losses = []
		for sample in raw:
			sample = sample.reshape(-1)
			c = sample[-1].long()
			sample = sample[0:-1]
			sample = sample.reshape(1,129,1)
			optimizer.zero_grad()
			out = model(sample)
			loss = criterion(out,torch.tensor([c]))
			loss.backward()
			optimizer.step()
			losses.append(loss.item())
		total = sum(losses)/len(losses)
		print("Total loss: ",total)
	torch.save(model,'myModel')
