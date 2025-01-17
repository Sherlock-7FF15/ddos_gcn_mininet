# ddos_gcn_mininet
This file is to record the difference from previous design.
update list:
1. The data format should be updated.

Our previous data format is:
[BEGIN_DATE	END_DATE	NUM_NODES	ATTACK_RATIO	ATTACK_START_TIME	ATTACK_DURATION	ATTACK_PARAMETER	NODE	LAT	LNG	TIME	TIME_FEATURE	ACTIVE	PACKET	ATTACKED	PACKET_160	NODE_160	PACKET_159	NODE_159 ...]

The new inference data format is:
['TIME', 'BEGIN_DATE', 'END_DATE', 'NUM_NODES', 'ATTACK_RATIO',
       'ATTACK_START_TIME', 'ATTACK_DURATION', 'ATTACK_PARAMETER', 'NODE',
       'LAT', 'LNG', 'TIME_HOUR', 'ACTIVE', 'PACKET', 'ATTACKED',
       'PACKET_30_MIN', 'PACKET_1_HOUR', 'PACKET_2_HOUR', 'PACKET_4_HOUR',
       'EDGES_CONNECTION_RATIO']

We can see here is that we don't need to share the packet volume information between each nodes, so the node_udp_client.py and node_udp_server.py should be deleted/changed.

2. Control server side
The inference only happens on control server side, so we only deploy models/inference code on CS. 
The system clock still exist, and features like PACKET_30_MIN should be determined by this clock. Or it need be set manually before the experiment.
The connection information should be determined by CS prior to the experiment. Or all clients send their location information proactively.

3. Client side
The conmmunication between clients should does not exist in the system. The only conmmunication should happen between CS and client.
Client should record their packet volume periodically, and report to the server. To decrease overhead within the network, the client only report their packet volume when receiving signal from CS.

Where does the inference happen? CS or Server? The CS should be an IoT node because it is within the network and it can distribute the signal efficiently.
I think the inference should happen on the server, but how and when?
How: how to connect between CS and Server?
Use TCP, the server act reactively and cs behave proactively.
When: when should the inference happen?
Once the Server received a data from CS, an inference happens.

import csv
from scapy.all import sniff
from scapy.layers.inet import IP, TCP, UDP

# 输出文件名
output_file = "packets.csv"

# 定义一个函数来处理捕获的数据包
def process_packet(packet):
    packet_info = {
        "timestamp": packet.time,
        "source_ip": "",  # 默认值
        "destination_ip": "",  # 默认值
        "protocol": "Unknown",
        "length": len(packet)
    }

    if IP in packet:
        ip_layer = packet[IP]
        packet_info["source_ip"] = ip_layer.src
        packet_info["destination_ip"] = ip_layer.dst

        if TCP in packet:
            packet_info["protocol"] = "TCP"
        elif UDP in packet:
            packet_info["protocol"] = "UDP"
        else:
            packet_info["protocol"] = "IP"

    # 将数据写入CSV文件
    with open(output_file, "a", newline="", encoding="utf-8") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow([
            packet_info["timestamp"],
            packet_info["source_ip"],
            packet_info["destination_ip"],
            packet_info["protocol"],
            packet_info["length"]
        ])

# 初始化CSV文件，写入表头
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Timestamp", "Source IP", "Destination IP", "Protocol", "Length"])

# 使用Scapy捕获来自eth0的数据包
sniff(iface="eth0", prn=process_packet, store=False)
