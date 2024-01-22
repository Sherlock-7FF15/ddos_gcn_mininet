#!/usr/bin/env python3

import sys
from datetime import datetime
import time
import socket
import csv
import argparse
import pandas as pd
from shared_variable.port_number import DATA_UPLOAD_PORT
from utils.function_util import send_udp_data
import socket
sys.path.append("./inference/source_code/nn_training/")
sys.path.append("./inference/source_code/")

from inference.source_code.nn_training.generate_results import load_model_weights, load_dataset, \
    get_dataset_input_output, find_best_threshold

global TP, FP, TN, FN
TP = 0.0
FP = 0.0
TN = 0.0
FN = 0.0

threshold_dic = {
  160: 0.6, 159: 0.5, 166: 0.8, 157: 0.5, 187: 0.6, 198: 0.5, 108: 0.7, 109: 0.4,
  110: 0.6, 111: 0.7, 112: 0.2, 113: 0.7, 114: 0.3, 115: 0.6, 116: 0.5, 117: 0.6,
  118: 0.5, 119: 0.5, 120: 0.7, 121: 0.7, 122: 0.7, 123: 0.6, 124: 0.7, 125: 0.6,
  126: 0.5, 127: 0.3, 129: 0.7, 130: 0.2, 131: 0.6, 132: 0.7, 133: 0.7, 134: 0.7,
  135: 0.4, 136: 0.7, 137: 0.5, 138: 0.4, 139: 0.8, 141: 0.3, 142: 0.7, 143: 0.6,
  144: 0.6, 145: 0.8, 146: 0.7, 147: 0.8, 148: 0.8, 149: 0.7, 150: 0.5, 151: 0.6,
  152: 0.9, 176: 0.7, 209: 0.6, 248: 0.4, 233: 0.7, 170: 0.4
}


def load_the_data(data_path, model_path, sleep_time, node_number, server_ip):
    global TP, FP, TN, FN
    node_number = get_node_number()
    model, scaler, selected_nodes_for_correlation = load_model(model_path, int(node_number))
    # selected_nodes_for_correlation.append(140)
    print(selected_nodes_for_correlation)
    while True:
        try:
            data = load_dataset(data_path)
            break
        except Exception as e:
            print("Waiting for data for inference...")
            time.sleep(1)

    threshold = threshold_dic[node_number]
    avg_pred = []
    avg_whole = []
    # with open('/home/pi/Documents/MiniTest/inference/{}_prediction_data.csv'.format(node_number), 'w') as file:
    #         writer = csv.DictWriter(file,
    #                                 fieldnames=['time', 'prediction'])
    #         writer.writeheader()
    while True:
        try:
            try:
                data = load_dataset(data_path)
                X_out, y_out, df_out, temp_columns = get_dataset_input_output(
                    "", "multiple_models_with_correlation",
                    data,
                    selected_nodes_for_correlation,
                    1,
                    10,
                    scaler,
                    False,
                    True
                )
            except Exception as e:
                print(f"Error in getting dataset input and output: {e}")
                continue

            t2 = datetime.now()
            if X_out.shape[1:] != model.input_shape[1:]:
                print(X_out, model.input_shape[1:])
                print("Skipping due to incompatible shape of X_out.")
                continue
            
            try:
                test_predictions_baseline = model.predict(X_out)
            except Exception as e:
                print(f"Error in model prediction: {e}")
                continue
            write_data = {'TIME': datetime.now(), 'PREDICTION': 0}
            if test_predictions_baseline >= threshold:
                write_data['PREDICTION'] = 1
                print('DDoS Botnet!')
            else:
                print('Benign')
            try:
                write_data['ATTACKED'] = get_ref_data(data_path)
            except:
                write_data['ATTACKED'] = 0
            write_data['NODE'] = node_number
            accuracy, precision, recall = metric_cal(write_data['PREDICTION'], write_data['ATTACKED'])
            write_data['ACCURACY'] = accuracy
            write_data['PRECISION'] = precision
            write_data['RECALL'] = recall
            try:
                df = pd.read_csv(data_path)
                traffic = df.iloc[-1, 13]
                write_data['TRAFFIC'] = traffic
            except:
                write_data['TRAFFIC'] = 0

            try:
                write_data['F1'] = 2*(precision*recall)/(precision+recall)
            except:
                write_data['F1'] = 0.0
            send_udp_data(write_data, server_ip, DATA_UPLOAD_PORT)
            # with open('/home/pi/Documents/MiniTest/inference/{}_prediction_data.csv'.format(node_number), 'a') as file:
            #     writer = csv.DictWriter(file,
            #                             fieldnames=['TIME', 'NODE', 'ATTACKED', 'PREDICTION', 'ACCURACY', 'PRECISION', 'RECALL', 'F1', 'TRAFFIC'])
            #     writer.writerow(write_data)
            # t3 = datetime.now()
            # avg_pred.append((t3-t2).total_seconds())
            # avg_whole.append((t3-t1).total_seconds())
            # print("start time: ", t1)
            # print("time to read data: ", t2-t1)
            # print("time just for prediction: ", t3-t2, " average: ", sum(avg_pred)/len(avg_pred))
            # print("time for the whole process: ", t3-t1, " average: ", sum(avg_whole)/len(avg_whole))
            # print("time getting the result: ", t3)
            
            print(test_predictions_baseline)
        except Exception as e:
            print(f"Some Errors Happened: {e}")
            continue
        time.sleep(sleep_time)


def load_model(model_path, node_number):
    model, scaler, selected_nodes_for_correlation = load_model_weights(
        model_path,
        node_number,
        "val_binary_accuracy",
        "max"
    )
    return model, scaler, selected_nodes_for_correlation


def get_node_number():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        ip_address = sock.getsockname()[0]
        return int(ip_address.split(".")[-1])
    except socket.error:
        return None
    finally:
        sock.close()
        

def get_ref_data(data_path):
    df = pd.read_csv(data_path)
    ref_data = df['ATTACKED'].iloc[-1]
    return ref_data
    

def metric_cal(prediction, attacked):
    global TP, FP, TN, FN
    if attacked == 1 and prediction == 1:
        TP += 1
    elif attacked == 0 and prediction == 0:
        TN += 1
    elif attacked == 1 and prediction == 0:
        FN += 1
    elif attacked == 0 and prediction == 1:
        FP += 1
    try:
        precision = TP/(TP+FP)
    except:
        precision = 0.0
    try:
        recall = TP/(TP+FN)
    except:
        recall = 0.0
    accuracy = (TP+TN)/(TP+TN+FP+FN)
    return accuracy, precision, recall


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default='138')
    args = parser.parse_args()
    load_the_data("./dataFile/data_for_inference/data_for_inference.csv", "./model/", 5, args.model, '192.168.1.207')
