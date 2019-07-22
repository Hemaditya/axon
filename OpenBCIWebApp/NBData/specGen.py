import matplotlib.mlab as mlab
import numpy as np
import os

for j, i in enumerate(os.listdir('.')):
	if 'npy' in i:
		spec, f, t = mlab.specgram(np.load(i))
		spec = spec.reshape(1,-1)
		spec = np.repeat(spec,100,0)
		np.save('spectrogram/'+'nb_spec'+str(j),spec)
