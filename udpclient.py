import socket
import sys
import numpy as np
import EEGrunt
# Create a UDP socket

# print("Setting up UDP Client ...!")
# SOCK_DGRAM
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = ('localhost', 10000)
source = 'openbci'
filename  = 'eegrunt-obci-ovibe-test-data-default.csv'
path = ''
session_title = "OpenBCI EEGrunt Test Data"
ecg = EEGrunt.EEGrunt(path, filename, source, session_title)
ecg.load_data()
data_dict = {'channel1' : [], 'channel2': [], 'channel3': [], 'channel4': [], 'channel5': []
             , 'channel6': [], 'channel7': [], 'channel8': []}

for channel in ecg.channels:
    ecg.load_channel(channel)
    ecg.remove_dc_offset()
    if channel == 1:
        data_dict['channel1'] = ecg.data
    elif channel == 2:
        data_dict['channel2'] = ecg.data
    elif channel == 3:
        data_dict['channel3'] = ecg.data
    elif channel == 4:
        data_dict['channel4'] = ecg.data
    elif channel == 5:
        data_dict['channel5'] = ecg.data
    elif channel == 6:
        data_dict['channel6'] = ecg.data
    elif channel == 7:
        data_dict['channel7'] = ecg.data
    else:
        data_dict['channel8'] = ecg.data

time_data = ecg.t_sec
print("printing data in udpclient ...")
# print(len(data), len(time_data))
# print(data[0],time_data[0])



def sendmessage(message):
    sock.sendto(message.encode(), server_address)
#
#


while True:


    for i in range(len(data_dict['channel1'])):
        # msg = ''
        # msg += str(data[i])
        # msg += ','
        # msg += str(time_data[i])
        # for key in data_dict:
        msg = ''
        for key in data_dict:
            msg += str(data_dict[key][i])
            msg += ','
        msg += str(time_data[i])
        sendmessage(msg)



# while True:
#     nchannels = 8
#     msg = ''
#     for i in range(nchannels):
#         # print(str(np.random.rand(1)))
#         msg += str(np.random.rand(1))
#         if i != nchannels -1:
#             msg += ','
#     # print("sending message")
#     sendmessage(msg)
#

    # try:
    #
    #     # Send data
    #     print (sys.stderr, 'sending "%s"' % message)
    #     sent = sock.sendto(message.encode(), server_address)
    #
    #     # # Receive response
    #     # print (sys.stderr, 'waiting to receive')
    #     # data, server = sock.recvfrom(4096)
    #     # print (sys.stderr, 'received "%s"' % data)
    #
    # finally:
    #     print (sys.stderr, 'closing socket')
    #     sock.close()