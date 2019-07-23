import torch.nn as nn
import torch

class NN(nn.Module):
  def __init__(self):
    super(NN,self).__init__()
    
    self.conv1 = nn.Conv1d(129,20,1)
    self.conv2 = nn.Conv1d(20,10,1)
    self.lin1 = nn.Linear(10,2)
    
    self.relu = nn.ReLU()
    self.sig = nn.Sigmoid()
    self.softmax = nn.Softmax()
    
  def forward(self, x):
    x = self.sig(self.conv1(x))
    x = self.sig(self.conv2(x)).reshape(x.shape[0],-1)
    x = self.softmax(self.lin1(x))
    
    return x


