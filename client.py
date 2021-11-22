import socket
import os
from _thread import *
import threading
import multiprocessing
from multiprocessing import Process, Lock
from datetime import timedelta
from PiSocketThread import PiSocketThread
from PiSocketThread import PiSocketMultiThread
from util import *

if __name__ == '__main__':
    multiprocessing.set_start_method('spawn')
    barrier = threading.Barrier(BARRIER_THRESHOLD, action = None, timeout = None)

    n_threads = 0
    sockets = []
    for host_id in HOST_IDS:
        host = '.'.join([NETWORK_ID, host_id])
        print(host)
        try:
            # Create a TCP stream socket
            client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            client_socket.connect((host, PORT))
        except socket.error as e:
            print(str(e))
        print(f'Connected to {host}')
        client_socket.sendto(HANDSHAKE, (host, PORT))
        expected_host_id = client_socket.recvfrom(BUFFER_SIZE)[0].decode('utf-8')[-3:]
        if (expected_host_id not in HOST_IDS):
            print(f'Unknown server {expected_host_id}. Closing socket')
            client_socket.close()
        print('Handshake successful')
        PiSocketThread(client_socket, host, PORT, barrier).start() 
        # p = Process(target=PiSocketMultiThread, args=(client_socket, host, PORT, barrier,))
        # p.start()
        # p.join()
        n_threads+=1
        print('Thread Count: ' + str(n_threads))
