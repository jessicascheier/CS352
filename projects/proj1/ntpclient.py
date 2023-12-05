#!/usr/bin/env python

'''
CS352 Assignment 1: Network Time Protocol
You can work with 1 other CS352 student

DO NOT CHANGE ANY OF THE FUNCTION SIGNATURES BELOW
'''

# authors: Jessica Scheier and Archisa Bhattacharya

from socket import socket, AF_INET, SOCK_DGRAM
import struct
from datetime import datetime

def getNTPTimeValue(server="time.apple.com", port=123) -> (bytes, float, float):
    t1_diff = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs1 = t1_diff.days * 24.0 * 60.0 * 60.0 + t1_diff.seconds
    T1 = secs1 + float(t1_diff.microseconds / 1000000.0)
    # print("T1 = % f " % T1) # t1 timestamp

    ntpClient = socket(AF_INET, SOCK_DGRAM)
    ntpPacket = '\x1b' + 47 * '\0'
    ntpClient.sendto(ntpPacket.encode('utf-8'), (server, port))
    pkt, address = ntpClient.recvfrom(1024)
    # print('Response received from:', address)

    t4_diff = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
    secs4 = t4_diff.days * 24.0 * 60.0 * 60.0 + t4_diff.seconds
    T4 = secs4 + float(t4_diff.microseconds / 1000000.0)
    # print("T4 = % f " % T4) # t4 timestamp

    return (pkt, T1, T4)


def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float) -> (float, float):
    TIME1970 = float(2208988800) # same as (70 * 365) + 17) * 86400)
    if pkt:
        # print('Data packet: ', pkt)
        t8 = struct.unpack('!12I', pkt)[8] # whole part for t2
        t8 -= TIME1970
        t9 = struct.unpack('!12I', pkt)[9] # fractional part for t2
        # t9 -= TIME1970
        T2 = float(t8) + (t9 / 2**32)
        t10 = struct.unpack('!12I', pkt)[10] # whole part for t3
        t10 -= TIME1970
        t11 = struct.unpack('!12I', pkt)[11] # fractional part for t3
        # t11 -= TIME1970
        T3 = float(t10) + (t11 / 2**32)

        # T2 = t8 + (float(t9 / 2**32))
        # T3 = t10 + (float(t11 / 2**32))
        # print("T2 = % f " % T2)
        # print("T3 = % f " % T3)

    # Calculate RTT and offset
    rtt = (T4 - T1) - (T3 - T2)
    offset = ((T2 - T1) + (T3 - T4)) / 2
    print(tuple([rtt, offset]))
    # print("rtt = % f " % rtt)
    # print("offset = % f " % offset)

    return (rtt, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20) -> float:
    offsets = []
    for _ in range(iters):
        pkt, T1, T4 = getNTPTimeValue(server, port)
        rtt, offset = ntpPktToRTTandOffset(pkt, T1, T4)
        time_diff = datetime.utcnow() - datetime(1970, 1, 1, 0, 0, 0)
        secsNow = time_diff.days * 24.0 * 60.0 * 60.0 + time_diff.seconds
        timeNow = secsNow + float(time_diff.microseconds / 1000000.0)
        # print('timeNow = % f' % timeNow)
        offsets.append(timeNow + offset + rtt)
    currentTime = float(sum(offsets) / len(offsets))

    # print('currentTime: % f' % currentTime)
    return currentTime #in Unix time as a Python float

if __name__ == "__main__":

    print(getCurrentTime())