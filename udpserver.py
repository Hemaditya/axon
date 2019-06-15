import socket
import string
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim
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

xdata = []



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



    fig.canvas.draw()
    # if len(xdata) > 22:
    #     axs.set_xlim(left=xdata[len(xdata)-20], right= xdata[-1])




ani = anim.FuncAnimation(fig, update_data, interval = 50)
plt.xlabel('Time (sec)')
plt.ylabel('Power (uV)')
fig.suptitle('Signal Plot')
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
