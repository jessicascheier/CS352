import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from math import ceil
from numpy import mean
from scapy.all import *
from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse
from scapy.layers.inet import TCP, IP

pcap = rdpcap("pcap1.pcap")
print(pcap)

sessions = pcap.sessions()
print(sessions)
print(sessions["Other"])
for p in sessions["Other"]:
    print(p)