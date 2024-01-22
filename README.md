# ddos_gcn_mininet
This file is to record the difference from previous design.
update list:
1. The data format should be updated.

Our previous data format is:
[BEGIN_DATE	END_DATE	NUM_NODES	ATTACK_RATIO	ATTACK_START_TIME	ATTACK_DURATION	ATTACK_PARAMETER	NODE	LAT	LNG	TIME	TIME_FEATURE	ACTIVE	PACKET	ATTACKED	PACKET_160	NODE_160	PACKET_159	NODE_159]

The new inference data format is:
['TIME', 'BEGIN_DATE', 'END_DATE', 'NUM_NODES', 'ATTACK_RATIO',
       'ATTACK_START_TIME', 'ATTACK_DURATION', 'ATTACK_PARAMETER', 'NODE',
       'LAT', 'LNG', 'TIME_HOUR', 'ACTIVE', 'PACKET', 'ATTACKED',
       'PACKET_30_MIN', 'PACKET_1_HOUR', 'PACKET_2_HOUR', 'PACKET_4_HOUR',
       'EDGES_CONNECTION_RATIO']
