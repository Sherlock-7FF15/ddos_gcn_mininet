#!/usr/bin/env python3

from datetime import datetime, timedelta
# from influxdb_client import InfluxDBClient, Point
# from influxdb_client.client.write_api import SYNCHRONOUS
import mysql.connector
from datetime import datetime
import socket
import pickle
import numpy
from utils.function_util import get_ip_address
from shared_variable.port_number import DATA_UPLOAD_PORT
from shared_variable.parameter_config import active_time, ip_list


global TP, FP, TN, FN, T_TP, T_FP, T_TN, T_FN, pre_time, table_name, traffic, packet_count
TP = 0.0
FP = 0.0
TN = 0.0
FN = 0.0
T_TP = 0.0
T_FP = 0.0
T_TN = 0.0
T_FN = 0.0
packet_count = 1
traffic = []
table_name = 'mydatabase.ddos_exp2'
pre_time = datetime.now()

def metric_cal(prediction, attacked):
    global TP, FP, TN, FN, T_TP, T_FP, T_TN, T_FN, pre_time
    if attacked == 1.0 and prediction == 1:
        TP += 1.0
        T_TP += 1.0
    elif attacked == 0.0 and prediction == 0.0:
        TN += 1.0
        T_TN += 1.0
    elif attacked == 1.0 and prediction == 0.0:
        FN += 1.0
        T_FN += 1.0
    elif attacked == 0.0 and prediction == 1.0:
        FP += 1.0
        T_FP += 1.0
    accuracy = (TP+TN)/(TP+TN+FP+FN)
    try:
        precision = TP/(TP+FP)
    except:
        precision = 0.0
    try:
        recall = TP/(TP+FN)
    except:
        recall = 0.0
    try:
        f1 = 2*accuracy*recall/(accuracy+recall)
    except:
        f1 = 0.0
    if (datetime.now()-pre_time > timedelta(seconds=active_time*3)):
        T_TP = 0.0
        T_FP = 0.0
        T_TN = 0.0
        T_FN = 0.0
        pre_time = datetime.now()
    return accuracy, precision, recall, f1

    
# def insert_data(point, client):
#     try:
#         client.write_api(write_options=SYNCHRONOUS).write(bucket="ddos_demo", record=[point])
#     except Exception as e:
#         print(f'Error: {e}')


# def query_data(sql, client):
#     sql = '''
#     from(bucket: "ddos_demo")
#     |> range(start: -1y)
#     |> filter(fn: (r) => r._measurement == "your_measurement")
#     '''
#     try:
#         table = client.query_api().query(sql)
#     except Exception as e:
#         print(f'Error: {e}')
#     return table


# def database_connection():
#     client = InfluxDBClient(
#         url='https://us-east-1-1.aws.cloud2.influxdata.com',
#         token="BU2z34bmc4UrZVY_qirEgvTp0Z_FrRXS8H2H4Pc_CZVVQ8LQKGyuwXUJj-2R6AFozlDXpZNDzJRL2h4TDb45Kw==",
#         org='USC'
#     )
#     return client


# def delete_data(client):
#     start = "1970-01-01T00:00:00Z"
#     stop = "2023-10-07T00:00:00Z"
#     client.delete_api().delete(start, stop, '_measurement="your_measurement"', bucket="ddos_demo", org = 'USC')


# def upload_control(experiment_id):
#     global TP, FP, TN, FN, T_TP, T_FP, T_TN, T_FN
#     s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     s_socket.bind((get_ip_address(), DATA_UPLOAD_PORT))
#     while True:
#         data, addr = s_socket.recvfrom(2048)
#         data_dict = pickle.loads(data)
#         point = Point(experiment_id)\
#             .time(data_dict['TIME'])\
#             .tag('NODE', data_dict['NODE'])\
#             .field('ATTACKED', data_dict['ATTACKED'])\
#             .field('PREDICTION', data_dict['PREDICTION'])\
#             .field('ACCURACY', data_dict['ACCURACY'])\
#             .field('PRECISION', data_dict['PRECISION'])\
#             .field('RECALL', data_dict['RECALL'])\
#             .field('F1', data_dict['F1'])
        
#         accuracy, precision, recall, f1 = metric_cal(data_dict['PREDICTION'], data_dict['ATTACKED'])
#         overall_point = Point(experiment_id+'_overall')\
#                 .tag('NODE', '140')\
#                 .field('ACCURACY', accuracy)\
#                 .field('PRECISION', precision)\
#                 .field('RECALL', recall)\
#                 .field('F1', f1)\
#                 .field('T_TP', T_TP/len(ip_list))\
#                 .field('T_FP', T_FP/len(ip_list))
#         client = database_connection()
#         insert_data(point, client)
#         insert_data(overall_point, client)
#         print('Upload ', data_dict['NODE'], ' to database.')


# if __name__ == '__main__':
#     data_dict = {'TIME': datetime.now(), 'NODE': 140, 'ATTACKED': 1, 'PREDICTION': 0, 'ACCURACY': 0.8, 'PRECISION':0.6, 'RECALL':0.66, 'F1': 0.8}
#     point = Point("test_exp6")\
#         .time(data_dict['TIME'])\
#         .tag('NODE', data_dict['NODE'])\
#         .field('ATTACKED', data_dict['ATTACKED'])\
#         .field('PREDICTION', data_dict['PREDICTION'])\
#         .field('ACCURACY', data_dict['ACCURACY'])\
#         .field('PRECISION', data_dict['PRECISION'])\
#         .field('RECALL', data_dict['RECALL'])\
#         .field('F1', data_dict['F1'])
#     # delete_data(database_connection())
#     insert_data(point, database_connection())
#     # table = query_data("", database_connection())
#     # print(table)
#     # upload_control('test_exp3')
#     print('start')

def database_connection():
    conn = mysql.connector.connect(
        host='ddos-demo.cksczbddcvbr.us-east-2.rds.amazonaws.com',
        user='admin',
        password='Zjh052500!'
    )
    return conn


def insert_data(data_dict, conn, table_name):
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO {} VALUES (
        %(TIME)s, %(NODE)s, %(ATTACKED)s, %(PREDICTION)s, %(ACCURACY)s, %(PRECISION)s, %(RECALL)s, %(F1)s, %(TRAFFIC)s
    );
    """.format(table_name)
    cursor.execute(insert_query, data_dict)
    conn.commit()
    cursor.close()


def upload_control():
    global TP, FP, TN, FN, T_TP, T_FP, T_TN, T_FN, table_name, traffic
    conn = database_connection()
    s_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s_socket.bind((get_ip_address(), DATA_UPLOAD_PORT))
    while True:
        data, addr = s_socket.recvfrom(2048)
        data_dict = pickle.loads(data)
        for key, value in data_dict.items():
            if isinstance(value, numpy.int64):
                data_dict[key] = int(value)
        data_dict['TIME'] = datetime.now()
        if len(traffic) > 5:
            traffic.pop(0)
        traffic.append(data_dict['TRAFFIC'])
        insert_data(data_dict, conn, table_name)
        accuracy, precision, recall, f1 = metric_cal(data_dict['PREDICTION'], data_dict['ATTACKED'])
        tra = 0
        if float(len(traffic)) != 0:
            tra = float(sum(traffic))/float(len(traffic))
        data_dict1 = {'NODE': 140, 'TIME': datetime.now(), 'ATTACKED': 0, 'PREDICTION': 0, 'ACCURACY': accuracy, 'PRECISION': precision, 'RECALL': recall, 'F1': f1, 'TRAFFIC': tra}
        insert_data(data_dict1, conn, table_name)


if __name__ == '__main__':
    # data_dict1 = {'NODE': 140, 'TIME': datetime.now(), 'ATTACKED': 0, 'PREDICTION': 0, 'ACCURACY': 0.2, 'PRECISION': 0.2, 'RECALL': 0.3, 'F1': 0.4}
    print(datetime.now())
    # insert_data(data_dict1, database_connection(), 'mydatabase.ddos_exp1')
    # print(datetime.now())
    upload_control()