import threading
from multiprocessing import Process
from datetime import datetime
from datetime import timedelta


BUFFER_SIZE = 1024
DELAY = timedelta(seconds=3)

class PiSocketThread(threading.Thread):
    def __init__(self, client, address, port, barrier):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.port = port
        self.barrier = barrier
    def run(self):
        self.barrier.wait()
        print(f"Telling pi to take a picture {str(DELAY)} after {datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')[:-3]}")
        scheduledTime = (datetime.now()+DELAY).strftime('%y-%m-%d %H:%M:%S.%f')[:-3]
        print("scheduledTime", scheduledTime)
        scheduledTime = str.encode(scheduledTime)
        self.client.sendto(scheduledTime, (self.address, self.port))
        with open(f'capture{self.address[-3:]}.jpg', 'wb') as file:
            image_chunk = self.client.recv(BUFFER_SIZE)
            while(image_chunk):
                file.write(image_chunk)
                image_chunk = self.client.recv(BUFFER_SIZE)

def PiSocketMultiThread(client, address, port, barrier):
    barrier.wait()
    print(f"Telling pi to take a picture {str(DELAY)} after {datetime.now().strftime('%y-%m-%d %H:%M:%S.%f')[:-3]}")
    scheduledTime = (datetime.now()+DELAY).strftime('%y-%m-%d %H:%M:%S.%f')[:-3]
    print("scheduledTime", scheduledTime)
    scheduledTime = str.encode(scheduledTime)
    client.sendto(scheduledTime, (address, port))
