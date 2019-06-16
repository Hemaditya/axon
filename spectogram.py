from matplotlib.mlab import window_hanning,specgram
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LogNorm
import numpy as np
import time
from pyOpenBCI import OpenBCICyton
nfft = 512
samplingrate=250
fs_Hz = 250
overlap = nfft - int(0.25 * fs_Hz)
SAMPLES_PER_FRAME = 128
fig = plt.figure()
streamedData = []


def get_data(sample):
    streamedData = sample


"""
get_specgram:
takes the FFT to create a spectrogram of the given audio signal
input: audio signal, sampling rate
output: 2D Spectrogram Array, Frequency Array, Bin Array
see matplotlib.mlab.specgram documentation for help
"""
def get_specgram(data):
    arr2D, freqs, bins = specgram(data, window=window_hanning,
                                  Fs=fs_Hz, NFFT=nfft, noverlap=overlap)
    return arr2D, freqs, bins


def update_fig(n):
    arr2D, freqs, bins = get_specgram(streamedData.channels_data[0] * ((4.5) / 24 / (2 ** 23 - 1)))
    im_data = im.get_array()
    if n < SAMPLES_PER_FRAME:
        im_data = np.hstack((im_data, arr2D))
        im.set_array(im_data)
    else:
        keep_block = arr2D.shape[1] * (SAMPLES_PER_FRAME - 1)
        im_data = np.delete(im_data, np.s_[:-keep_block], 1)
        im_data = np.hstack((im_data, arr2D))
        im.set_array(im_data)
    return im,


#main program
arr2D, freqs, bins = get_specgram(streamedData.channels_data[0] * ((4.5)/24/(2**23-1)))
"""
   Setup the plot paramters
   """
extent = (bins[0], bins[-1] * SAMPLES_PER_FRAME, freqs[-1], freqs[0])
im = plt.imshow(arr2D, aspect='auto', extent=extent, interpolation="none",
                cmap='jet', norm=LogNorm(vmin=.01, vmax=1))
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')


plt.title('Real Time Spectogram')
plt.gca().invert_yaxis()
##plt.colorbar() #enable if you want to display a color bar

anim = animation.FuncAnimation(fig, update_fig, blit=False,interval=10)
                               # interval=mic_read.CHUNK_SIZE / 1000)
plt.show(block=False)

board = OpenBCICyton(port='/dev/ttyUSB0', daisy=False)
#call back fn
board.start_stream(get_data)
