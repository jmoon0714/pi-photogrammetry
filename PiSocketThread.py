import threading
from multiprocessing import Process
from datetime import datetime
from datetime import timedelta
import os

BUFFER_SIZE = 1024
DELAY = timedelta(seconds=3)
TIMEOUT = timedelta(seconds=100)
class PiSocketThread(threading.Thread):
    def __init__(self, client, address, port, barrier, count, dst_dir):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.port = port
        self.count = count
        self.barrier = barrier
        self.dst_dir = dst_dir

    def run(self):
        self.barrier.wait()
        # print(f"Telling pi to take a picture {str(DELAY)} after {datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')[:-3]}")
        scheduledTime = (datetime.now()+DELAY).strftime('%y-%m-%d %H:%M:%S.%f')[:-3]
        # print("scheduledTime", scheduledTime)
        scheduledTime = str.encode(scheduledTime)
        self.client.sendto(scheduledTime, (self.address, self.port))
        # print('Instruction sent')
        tic = datetime.now()
        with open(os.path.join(self.dst_dir, f'capture{self.address[-3:]}_{self.count}.png'), 'wb') as file:
            image_chunk = self.client.recv(BUFFER_SIZE)
            count = 0
            while(datetime.now() -tic < TIMEOUT and image_chunk[-4:] != 'DONE'.encode()):
                count+=1
                file.write(image_chunk)
                image_chunk = self.client.recv(BUFFER_SIZE)
            file.write(image_chunk[:-4])
        # self.barrier.wait()
        # print('thread is done.')

def PiSocketMultiThread(client, address, port, barrier):
    barrier.wait()
    print(f"Telling pi to take a picture {str(DELAY)} after {datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')[:-3]}")
    scheduledTime = (datetime.now()+DELAY).strftime('%y-%m-%d %H:%M:%S.%f')[:-3]
    print("scheduledTime", scheduledTime)
    scheduledTime = str.encode(scheduledTime)
    client.sendto(scheduledTime, (address, port))
