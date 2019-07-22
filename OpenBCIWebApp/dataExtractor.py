import os
from shutil import copyfile

pathFrom = "RandomSessions/EYE_BLINK/"
pathTo = "NotchOutputFiles/"

i = 0
for folder in os.listdir(pathFrom):
	i = i+1	
	for f in os.listdir(pathFrom+folder):
		if "notch" in f:
			copyfile(pathFrom+folder+"/"+f, pathTo+f+"_"+str(i))
