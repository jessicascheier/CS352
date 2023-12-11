# author: Jessica Scheier

from scapy.all import *
from scapy.layers.http import HTTP, HTTPRequest, HTTPResponse
from scapy.layers.inet import TCP, IP
import sys

def main():
    file = sys.argv[1]
    ip = sys.argv[2]
    port = int(sys.argv[3])
    pcap = rdpcap(file)

    sessions = pcap.sessions()
    latencies = []
    requests = {} # get requests, use this dictionary to match pairs
    counter = 0
    sum = 0.0
    
    for session in sessions:
        for packet in sessions[session]:
            if packet.haslayer(TCP):
                source_ip = packet[IP].src
                dest_ip = packet[IP].dst
                source_port = packet[TCP].sport
                dest_port = packet[TCP].dport
                if packet.haslayer(HTTP):
                    if HTTPRequest in packet:
                        if dest_ip == ip and dest_port == port:
                            arrival_time = packet.time
                            request_key = (source_ip, source_port, dest_ip, dest_port)
                            # print("request:", request_key)
                            requests[request_key] = arrival_time
                    if HTTPResponse in packet:
                        if source_ip == ip and source_port == port:
                            response_key = (dest_ip, dest_port, source_ip, source_port)
                            # print("response: ", response_key)
                            if response_key in requests:
                                arrival = requests[response_key]
                                departure = packet.time
                                if departure > arrival:
                                    latency = departure - arrival
                                    latencies.append(latency)
                                    sum += latency
                                    counter += 1
    
    # counter starts at 0 so must add one
    print(f"AVERAGE LATENCY: {round(sum/(counter+1), 5)}")
    
    sorted_list = sorted(latencies)
    length = len(latencies)
    twentyfive = int(.25 * length)
    fifty = int(.50 * length)
    seventyfive = int(.75 * length)
    nintyfive = int(.95 * length)
    ninetynine = int(.99 * length)

    print(f"PERCENTILES: {round(sorted_list[twentyfive], 5)} {round(sorted_list[fifty], 5)} {round(sorted_list[seventyfive], 5)} {round(sorted_list[nintyfive], 5)} {round(sorted_list[ninetynine], 5)}")

main()