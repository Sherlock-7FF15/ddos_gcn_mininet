#!/usr/bin/env python3
import argparse

import tkinter as tk
from tkinter import ttk

import random
import time
import pandas as pd
import socket
import pickle
from datetime import datetime, timedelta
import paramiko
import threading
import requests
import os
import csv
from shared_variable.parameter_config import ip_list, victim_ip, sleep_time, start_min, active_time, attack_start, experiment_id, interface_url, credentials
from database_management import upload_control
from shared_variable.port_number import PROCESS_END_PROT


def ddos_experiment(k, attack_ratio, duration, memo, if_collect_data):
    node_number = len(ip_list)
    end_min = start_min + duration
    duration_delta = timedelta(seconds=duration * 60)
    # send boot up information to nodes
    for ip in ip_list:
        if ip == victim_ip:
            continue
        active_control_client(ip, active_time, sleep_time, k, False, False, victim_ip, 0, node_number, attack_ratio,
                              attack_start, duration_delta, ip_list)
        
    print('Start Tracking')
    treads_dic = dict()
    # db_manage = threading.Thread(target=upload_control)
    # db_manage.daemon = True
    # db_manage.start()
    # treads_dic['udp_client'] = db_manage
    
    print('Start Experiment')
    node_time_control(active_time, start_min, end_min, attack_ratio, k, sleep_time, victim_ip, node_number,
                      attack_start, duration_delta, ip_list, if_collect_data)

    for key in treads_dic:
        treads_dic[key].join()

    current_time = datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S.%f')
    print('Ending Time', formatted_time)
    print('Experiments End')
    # comment this line if use the control panel
    if if_collect_data:
        final_data_processing(victim_ip, ip_list, k, attack_ratio, active_time, duration, memo)
    print('Data Integration Ends')
    


def node_time_control(active_time, start_min, end_min, prec, k, sleep, victim_ip, node_number, attack_start,
                      duration, ip_list, if_collect_data):
    act_dic = dict()
    folder_path = "./dataFile"
    all_files = os.listdir(folder_path)
    file_path_list = []
    for file in all_files:
        if file.endswith('.csv'):
            file_path_list.append('./dataFile/{}'.format(file))
    start_min = start_min * 60 / active_time
    end_min = end_min * 60 / active_time
    selected_nodes = []
    nums = random.sample(range(len(ip_list)), int(prec * len(ip_list)))
    for i in nums:
        if ip_list[i] != victim_ip:
            selected_nodes.append(ip_list[i])
    
    # hardcode_ip = ['192.168.1.109', '192.168.1.110', '192.168.1.114', '192.168.1.131', '192.168.1.133', '192.168.1.137', '192.168.1.143', '192.168.1.144']
    # nums = random.sample(range(len(hardcode_ip)), int(prec * len(hardcode_ip)))
    # for i in nums:
    #     if hardcode_ip[i] != victim_ip:
    #         selected_nodes.append(hardcode_ip[i])

    print('Selected Botnet: ', selected_nodes)
    i = 0
    for node in ip_list:
        data_frame = pd.read_csv(file_path_list[i])
        act_list = data_frame['ACTIVE'].to_list()
        act_dic[node] = act_list
        i += 1
    # record data for inference reference
    with open('./inference/inference_ref.csv', 'w') as file:
        field = ['time']
        for ip in ip_list:
            field.append(int(ip.split(".")[-1]))
        writer = csv.DictWriter(file,
                                    fieldnames=field)
        writer.writeheader()

    start_time = time.time()
    clk = 0
    with open('./inference/inference_ref.csv', 'a') as file:
        while True:
            if clk > 50: #438:
                break
            clk += 1
            inf_data = {'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}
            for ip in ip_list:
                inf_data[int(ip.split(".")[-1])] = 0
            if start_min <= clk < end_min:
                print('attack start', clk, datetime.now())
                if attack_start == 0:
                    attack_start = datetime.now()
                ddos_attack_control(ip_list, prec, active_time, sleep, k, victim_ip, clk, node_number, act_dic,
                                    selected_nodes, attack_start, duration)
                for node in ip_list:
                    inf_data[int(node.split(".")[-1])] = 1
            else:
                for node in ip_list:
                    if act_dic[node][clk] == 1:
                        active_control_client(node, active_time, sleep, 0, False, False, victim_ip, clk, node_number, prec,
                                            attack_start, duration, ip_list)
                        print(node, ' is active.')
                print(clk)
            writer = csv.DictWriter(file,
                                    fieldnames=field)
            writer.writerow(inf_data)
            print('----------------------------')
            time.sleep(active_time)
    for node in ip_list:
        print('Sending End Signal to {}'.format(node))
        active_control_client(node, active_time, sleep, 0, False, True, victim_ip, clk, node_number, prec,
                              attack_start, duration, ip_list)


def active_control_client(ip, active_time, sleep, k, is_ddos, is_end, victim_ip, clk, node_number, attack_ratio,
                          attack_start, duration, ip_list):
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # arr = [active_time, sleep, k, is_ddos, is_end]
    data_dic = {'active_time': active_time,
                'sleep': sleep,
                'k': k,
                'is_ddos': is_ddos,
                'is_end': is_end,
                'victim_ip': victim_ip,
                'clk': clk,
                'node_ip': ip,
                'node_number': node_number,
                'attack_ratio': attack_ratio,
                'attack_start': attack_start,
                'duration': duration,
                'ip_list': ip_list
                }
    c_socket.sendto(pickle.dumps(data_dic), (ip, 9565))


def ddos_attack_control(ip_list, perc, active_time, sleep, k, victim_ip, clk, node_number, act_dic, selected_nodes,
                        attack_start, duration):
    for node in selected_nodes:
        if node != victim_ip:
            active_control_client(node, active_time, sleep, k, True, False, victim_ip, clk, node_number, perc,
                                  attack_start, duration, ip_list)
    for node in ip_list:
        if node not in selected_nodes and act_dic[node][clk] == 1:
            print(node, ' is active.')
            active_control_client(node, active_time, sleep, 0, False, False, victim_ip, clk, node_number, perc,
                                  attack_start, duration, ip_list)


def file_transferring_and_generating(host, port, username, password, remote_file_path, local_file_path):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.get(remote_file_path, local_file_path)

    sftp.close()
    transport.close()


def get_ip_address():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip_address = sock.getsockname()[0]
        return ip_address
    except socket.error:
        return None
    finally:
        sock.close()


def final_data_processing(victim_ip, ip_list, k, ratio, active_time, duration, memo):
    port = 22
    username = 'pi'
    password = 'anrgrpi'
    remote_file_path = '/home/pi/Documents/MiniTest/dataFile/packet_volume/packet_volume_info_{}.csv'
    local_file_path = '/home/pi/Documents/MiniTest/dataFile/final_data/packet_volume_info_{}.csv'
    final_data = pd.DataFrame()
    recv_ip = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ctrl_ip = get_ip_address()
    sock.bind((ctrl_ip, PROCESS_END_PROT))
    while True:
        if len(recv_ip) >= len(ip_list):
            break
        data, address = sock.recvfrom(1024)
        received_data = pickle.loads(data)
        if address[0] not in recv_ip and received_data[0]:
            recv_ip.append(address[0])
            print('receive ending signal from :', address[0])
            recv_ip.sort()
            print(set(ip_list)-set(recv_ip), ' not received.')
    print('All nodes finished processing data, start requesting...')
    for host in ip_list:
        if host == victim_ip:
            continue
        print('Processing data from', host)
        try:
            file_transferring_and_generating(host, port, username, password, remote_file_path.format(host[-3:]),
                                             local_file_path.format(host[-3:]))
        except FileNotFoundError:
            print('No such file')
            continue
        except Exception as e:
            print(f"Error: {e}")
            continue
        df = pd.read_csv(local_file_path.format(host[-3:]))
        final_data = pd.concat([final_data, df], ignore_index=True)
    final_data.to_csv('/home/pi/Documents/MiniTest/dataFile/final_data/{}_{}_{}_{}_data.csv'.format(k, ratio, duration,
                                                                                                    memo), index=False)


    
def authenticate():
    response = requests.post(interface_url+"/authenticate", json=credentials)
    if response.status_code == 200:
        print("Log in successful!")
        return response.json()['token']
    else:
        raise ValueError("Unabke to login: ", response.status_code)


def get_info(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(interface_url+"/get-info", headers=headers)
    
    
    if response.status_code == 200:
        data = response.json()
        # Check the latest data
        executed_data_raw = requests.get(interface_url+"/executed/get-info", headers=headers)
        executed_data = executed_data_raw.json()
        if (executed_data["id"] == data["id"]):
            print("No new data!")
            return
        post_execute_data = requests.post(interface_url+"/executed/update-info", headers=headers, json={'id': data["id"], 'finished': False})
        print(f"Executing: {data}")
        ddos_experiment(data["k"], data["ratio"], data["duration"], 'training', False)
        post_executed_data = requests.post(interface_url+"/executed/update-info", headers=headers, json={'id': data["id"], 'finished': True})
        print("Experiment end")
    elif response.status_code == 403:
        print("Error code 403, waiting...")
        time.sleep(5)
        get_info(token)
    else:
        print(f"Error: {response.status_code}")
      

def experiment_control():
    db_manage = threading.Thread(target=upload_control)
    db_manage.daemon = True
    db_manage.start()
    try:
        token = authenticate()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(e)
    while True:
        try:
            get_info(token)
        except:
            print("Something error happened!")
            continue
        time.sleep(5)
    db_manage.join()


if __name__ == '__main__':
    experiment_control()
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--t", type=float, default=1)
    # parser.add_argument("--name", type=str, default='traffic')
    # args = parser.parse_args()
    # k_para = [4]
    # Ratio = [0.5]
    # duration = [10]
    # for k in k_para:
    #     for perc in Ratio:
    #         for t in duration:
    #             ddos_experiment(k, perc, t, 'training', True)
    #             time.sleep(120)
    #             ddos_experiment(k, perc, t, 'testing', True)
    #             time.sleep(120)
    #             ddos_experiment(k, perc, t, 'validation', True)
