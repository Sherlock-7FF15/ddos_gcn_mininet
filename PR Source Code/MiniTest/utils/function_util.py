#!/usr/bin/env python3
import socket
import pickle


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


def send_udp_data(data, target_ip, port):
    c_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    c_socket.sendto(pickle.dumps(data), (target_ip, port))