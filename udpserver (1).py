import socket
import string
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
import matplotlib.mlab as mlab
from scipy import signal

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print('starting up on %s port %s' % server_address)
sock.bind(server_address)
# fig, ax = plt.subplots()
data_dict = {'channel1' : [], 'channel2': [], 'channel3': [], 'channel4': [], 'channel5': []
             , 'channel6': [], 'channel7': [], 'channel8': []}

fig, axs = plt.subplots(len(data_dict), sharex=True, sharey=False, gridspec_kw={'hspace': 0})
# fig1, axs1 = plt.subplots(len(data_dict), sharex=True, sharey=False, gridspec_kw={'hspace': 0})#for spectral plot
xdata = []
# spec_PSDperHz = []
# spec_freqs = []
# spec_t = []
# spec_PSDperBin = []
#
# def bandpass(data,start,stop,fs_Hz):
#     bp_Hz = np.zeros(0)
#     bp_Hz = np.array([start, stop])
#     b, a = signal.butter(3, bp_Hz / (fs_Hz / 2.0), 'bandpass')
#     print("Bandpass filtering to: " + str(bp_Hz[0]) + "-" + str(bp_Hz[1]) + " Hz")
#     return signal.lfilter(b, a, data, 0)
#
# def updateSpectogram(data,NFFT,fs_hz,overlap):
#     # start_Hz = 1
#     # stop_Hz = 50
#     # data1 = bandpass(data=data,start=start_Hz, stop=stop_Hz,fs_Hz=fs_hz)
#     spec_PSDperHz, spec_freqs, spec_t = mlab.specgram(np.squeeze(data),
#                                                                      NFFT=128,
#                                                                      window=mlab.window_hanning,
#                                                                      Fs=fs_hz,
#                                                                      noverlap=overlap
#                                                                      )  # returns PSD power per Hz
#     spec_PSDperBin = spec_PSDperHz * fs_hz / float(NFFT)
#
#
# def spectogram(data,index,nfft, fs_Hz, overlap):
#
#     # using specgram method
#     print()
#     Pxx, freqs, bins, im = axs1[index].specgram(data, NFFT=nfft, Fs=fs_Hz, noverlap=overlap)
#
#
#     # f_lim_Hz = [0, 50]
#     # axs1[index].pcolor(spec_t, spec_freqs, 10 * np.log10(spec_PSDperBin))  # dB re: 1 uV
#     # axs1[index].set_clim([-25, 26]) # plt.clim([-25, 26])
#     # axs1[index].set_xlim(spec_t[0], spec_t[-1] + 1)# plt.xlim(spec_t[0], spec_t[-1] + 1)
#     # axs1[index].set_ylim[f_lim_Hz]# plt.ylim(f_lim_Hz)
#     # plt.xlabel('Time (sec)')
#     # plt.ylabel('Frequency (Hz)')
#     # fig1.suptitle('Spectrogram')
#     # # add annotation for FFT Parameters
#     # axs1[index].text(0.025, 0.95,
#     #         "NFFT = " + str(nfft) + "\nfs = " + str(int(fs_Hz)) + " Hz",
#     #         transform=axs1[index].transAxes,
#     #         verticalalignment='top',
#     #         horizontalalignment='left',
#     #         backgroundcolor='w')
#
#
#     # original
#     # f_lim_Hz = [0, 50]  # frequency limits for plotting
#     # plt.figure(figsize=(10, 5))
#     # ax = plt.subplot(1, 1, 1)
#     # # plt.pcolor(spec_t, spec_freqs, 10 * np.log10(spec_PSDperBin))  # dB re: 1 uV
#     # # plt.clim([-25, 26])
#     # plt.xlim(spec_t[0], spec_t[-1] + 1)
#     # plt.ylim(f_lim_Hz)
#     plt.xlabel('Time (sec)')
#     plt.ylabel('Frequency (Hz)')
#     fig1.suptitle('Spectrogram')
#     # # add annotation for FFT Parameters
#     # ax.text(0.025, 0.95,
#     #         "NFFT = " + str(nfft) + "\nfs = " + str(int(fs_Hz)) + " Hz",
#     #         transform=ax.transAxes,
#     #         verticalalignment='top',
#     #         horizontalalignment='left',
#     #         backgroundcolor='w')
#     #
#
#
# def update_spectral_data(i):
#     nfft = 512
#     fs_hz = 250
#     overlap = nfft - int(0.25 * fs_hz)
#     start_Hz = 1
#     stop_Hz = 50
#     for channel in range(8):
#         if channel  == 0:
#             # updateSpectogram(data_dict['channel1'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel1'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 1:
#             # updateSpectogram(data_dict['channel2'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel2'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 2:
#             # updateSpectogram(data_dict['channel3'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel3'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 3:
#             # updateSpectogram(data_dict['channel4'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel4'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 4:
#             # updateSpectogram(data_dict['channel5'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel5'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 5:
#             # updateSpectogram(data_dict['channel6'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel6'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 6:
#             # updateSpectogram(data_dict['channel7'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel7'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#         elif channel == 7:
#             # updateSpectogram(data_dict['channel8'], NFFT=nfft, fs_hz=fs_hz, overlap=overlap)
#             spectogram(data_dict['channel8'],channel, nfft=nfft, fs_Hz=fs_hz, overlap=overlap)
#

def update_data(i):
    data, address = sock.recvfrom(4096)
    arr = data.decode().split(',')
    narr = np.array(arr)
    narr = narr.astype(np.float)
    # print(narr)
    xdata.append(narr[-1])
    for channel in range(len(narr)):
        if channel  == 0:
            data_dict['channel1'].append(narr[0])
            axs[channel].plot(xdata,data_dict['channel1'],color = 'red')
        elif channel == 1:
            data_dict['channel2'].append(narr[1])
            axs[channel].plot(xdata,data_dict['channel2'], color = 'blue')
        elif channel == 2:
            data_dict['channel3'].append(narr[2])
            axs[channel].plot(xdata,data_dict['channel3'], color = 'green')
        elif channel == 3:
            data_dict['channel4'].append(narr[3])
            axs[channel].plot( xdata,data_dict['channel4'], color = 'yellow')
        elif channel == 4:
            data_dict['channel5'].append(narr[4])
            axs[channel].plot(xdata, data_dict['channel5'], color = 'black')
        elif channel == 5:
            data_dict['channel6'].append(narr[5])
            axs[channel].plot( xdata,data_dict['channel6'], color = 'pink')
        elif channel == 6:
            data_dict['channel7'].append(narr[6])
            axs[channel].plot( xdata,data_dict['channel7'], color = 'gray')
        elif channel == 7:
            data_dict['channel8'].append(narr[7])
            axs[channel].plot(xdata, data_dict['channel8'], color = 'orange')

        if len(xdata) > 50:
            axs[0].set_xlim(left=xdata[len(xdata) - 50], right=xdata[-1])

        # change x limits
        # for ax in axs:
        #     if len(xdata) > 50:
        #         ax.set_xlim(left=xdata[len(xdata)-50], right=xdata[-1])
        #     else:
        #         pass
    fig.canvas.draw()
    # if len(xdata) > 22:
    #     axs.set_xlim(left=xdata[len(xdata)-20], right= xdata[-1])




ani = anim.FuncAnimation(fig, update_data, interval = 50)
plt.xlabel('Time (sec)')
plt.ylabel('Power (uV)')
fig.suptitle('Signal Plot')

# ani2 = anim.FuncAnimation(fig1, update_spectral_data, interval = 50)

plt.show()

# working code to decode udp channel msgs
# while True:
#     # print('\nwaiting to receive message')
#     data, address = sock.recvfrom(4096)
#     arr = data.decode().split(',')
#     print(len(arr))
#     narr = np.array(arr)
#     narr = narr.astype(np.float)
#
#     # narr = np.char.strip(narr,'[')
#     # narr = np.char.strip(narr, ']')
#     # narr = narr.astype(np.float)
#     # print(narr[0],type(narr[0]))
#
