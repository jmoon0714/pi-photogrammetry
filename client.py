import argparse
from datetime import datetime
from multiprocessing import Process, Lock, Barrier
import os
import socket
from tqdm import tqdm

from util import BARRIER_THRESHOLD, HANDSHAKE, BUFFER_SIZE, HOST_IDS, BLOCK_LIST, NETWORK_ID, PORT, HANDWAVE, DELAY, TIMEOUT

class CaptureSession:
    def __init__(self, dst):
        self.dst_dir = dst
        self.barrier = Barrier(BARRIER_THRESHOLD, action = None, timeout = None)
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

    def __capture_img_from_pi(self, client, address, port, count):
        self.barrier.wait()
        # print(f"Telling pi to take a picture {str(DELAY)} after {datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')[:-3]}")
        scheduledTime = (datetime.now()+DELAY).strftime('%y-%m-%d %H:%M:%S.%f')[:-3]
        # print("scheduledTime", scheduledTime)
        scheduledTime = str.encode(scheduledTime)
        client.sendto(scheduledTime, (address, port))
        tic = datetime.now()
        with open(os.path.join(self.dst_dir, f'capture{address[-3:]}_{count}.png'), 'wb') as file:
            image_chunk = client.recv(BUFFER_SIZE)
            count = 0
            while(datetime.now() - tic < TIMEOUT and image_chunk[-4:] != 'DONE'.encode()):
                count+=1
                file.write(image_chunk)
                image_chunk = client.recv(BUFFER_SIZE)
            file.write(image_chunk[:-4])


    def capture_img_from_pis(self):
        round=0
        is_ready = input("Press enter to capture ('q' to quit). \n\t>")
        while(is_ready != 'q'):
            round+=1
            print(f'Round {round}.')
            threads = []
            for client_socket, host, port in self.sockets:
                pst = Process(target=self.__capture_img_from_pi, args=(client_socket, host, port, round))
                threads.append(pst) 
            for thread in threads:
                thread.start()
            for thread in tqdm(list(threads)):
                thread.join()
            is_ready = input("Press enter to capture ('q' to quit).\n\t>")

    def close(self):
        for s, address, port in self.sockets:
            s.sendto(HANDWAVE, (address, port))
            s.close()
        
def main(cwd):
    session = CaptureSession(cwd)
    if(session.connect()):
        session.capture_img_from_pis()
        print('closing')
        session.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Destination for image captures')
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
    main(cwd)
    
