import socket
import os
from _thread import *
from datetime import datetime
import threading
import argparse
from tqdm import tqdm
import multiprocessing
from multiprocessing import Process, Lock
from datetime import timedelta
from PiSocketThread import PiSocketThread
from PiSocketThread import PiSocketMultiThread
from util import *

class CaptureSession:
    def __init__(self, dst):
        self.dst_dir = dst
        multiprocessing.set_start_method('spawn')
        self.barrier = threading.Barrier(BARRIER_THRESHOLD, action = None, timeout = None)
        self.sockets = []

    def __handshake(self, client_socket, host, port):
        client_socket.sendto(HANDSHAKE, (host, port))
        expected_host_id = client_socket.recvfrom(BUFFER_SIZE)[0].decode('utf-8')[-3:]
        if (expected_host_id not in HOST_IDS):
            print(f'Unknown server {expected_host_id}.')
            print('Handshake unsuccessful.')
            return False
        print('Handshake successful.')
        return True

    def connect(self):
        for host_id in HOST_IDS:
            if (host_id in BLOCK_LIST):
                continue
            host = '.'.join([NETWORK_ID, host_id])
            # Create a TCP stream socket
            try:
                client_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
                client_socket.connect((host, PORT))
            except socket.error as e:
                print(f'Could not connect to {host} because error: \n\t {str(e)}')
                continue
            print(f'Connected to {host}')
            # Initiate Handshake
            if (not self.__handshake(client_socket, host, PORT)):
                client_socket.close()
            # Successful Connection
            self.sockets.append((client_socket, host, PORT))
        print(f'{len(self.sockets)} sockets connected succesfully.')
        return len(self.sockets)

    def capture(self):
        round=0
        is_ready = input("Press enter to capture ('q' to quit). \n\t>")
        while(is_ready != 'q'):
            round+=1
            print(f'Round {round}.')
            threads = []
            for client_socket, host, port in self.sockets:
                pst = PiSocketThread(client_socket, host, port, self.barrier, round, self.dst_dir)
                pst.start()
                threads.append(pst) 
                # p = Process(target=PiSocketMultiThread, args=(client_socket, host, PORT, barrier,))
                # p.start()
                # p.join()
            for thread in tqdm(list(threads)):
                thread.join()
            is_ready = input("Press enter to capture ('q' to quit).\n\t>")
    def close(self):
        for s, address, port in self.sockets:
            s.sendto(HANDWAVE, (address, port))
            s.close()
        

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Destination for image captures')
    # date = (datetime.now()).strftime('%m.%d.%y %H:%M:%S')
    date = (datetime.now()).strftime('%m.%d.%y')

    parser.add_argument('--dst', dest='dst', default='/home/jmoon/Documents/CAIR/',
                    help='Absolute path to destination dir')
    parser.add_argument('--exp_no', dest='exp_no', default='X', help='Experiment number')
    parser.add_argument('--session_name', dest='session_name', default=f'{date} Experiment {parser.parse_args().exp_no}',
                    help='Session name')
    args = parser.parse_args()
    cwd = os.path.join(args.dst, args.session_name, 'data')
    if (not os.path.exists(cwd)):
        print(f'Created new dir: {cwd}')
        os.makedirs(cwd)
    session = CaptureSession(cwd)
    if(session.connect()):
        session.capture()
        print('closing')
        session.close()
