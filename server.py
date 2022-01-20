import sched
import socket
from datetime import datetime
from picamera import PiCamera
from time import sleep
import logging
import traceback

BUFFER_SIZE = 1024
CAPTURE_FILEPATH = '/home/pi/Desktop/picture.png'
HANDSHAKE = str.encode("Hello Pi Server")
HANDWAVE = str.encode('Goodbye.')
ip = '192.168.0.2' + socket.gethostname()[-2:]
HOST, PORT = (ip, 20001)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    filemode='w',
    datefmt='%Y-%m-%d %H:%M:%S'
)
def main():
    # Setup TCP Socket
    server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    try:
        server_socket.bind((HOST, PORT))
    except socket.error as e:
        logging.error(e)
        logging.info('Could not bind.')
        return

    # Setup Camera
    camera = PiCamera()
    # camera.framerate = 3
    # camera.resolution = (3280, 2464)
    camera.resolution = (1920, 1080)

    logging.info('Waiting for a Connection...')
    server_socket.listen(5)
    while (True):
        try:
            client, _ = server_socket.accept()
            expectedHandshake = client.recvfrom(BUFFER_SIZE)[0]
            if(expectedHandshake != HANDSHAKE):
                logging.error('Unknown Handshake.')
                break
            client.send(str.encode(HOST))
            round = 1
            logging.info('Connected!')
            while(True):
                expectedTimeOrHandwave = client.recvfrom(BUFFER_SIZE)
                # Exit Condition
                if(expectedTimeOrHandwave[0] == HANDWAVE or expectedTimeOrHandwave[0].decode('utf-8') == ''):
                    server_socket.close()
                    camera.close()
                    return 1
                if(expectedTimeOrHandwave[0] == ''):
                    logging.info("huh?")
                    continue

                logging.info(f'Round {round} started.')
                scheduledTime = datetime.strptime((expectedTimeOrHandwave[0].decode('utf-8')),'%y-%m-%d %H:%M:%S.%f')
                logging.info(f"Scheduled Time: {scheduledTime}")
                camera.start_preview()
                logging.info(f"Sleeping for {(scheduledTime-datetime.now()).total_seconds()} seconds.")
                assert (scheduledTime > datetime.now())
                sleep((scheduledTime-datetime.now()).total_seconds())
                camera.capture(CAPTURE_FILEPATH)
                logging.info(f"Captured image at {datetime.now().strftime('%H:%M:%S.%f')}")
                camera.stop_preview()
                # Send image to client
                with open(CAPTURE_FILEPATH, 'rb') as file:
                    image_data = file.read()
                    image_data += 'DONE'.encode()
                    client.sendall(image_data)
                logging.info(f'Round {round} finished')
                round+=1
        except ValueError as e:
            logging.error(traceback.print_exc())
            logging.info('Waiting for a Connection...')
        except AssertionError as e:
            logging.error("No image taken because the scheduled time has already passed. GO FIND THE BUG!")
            logging.error(traceback.print_exc())
            logging.info('Waiting for a Connection...')
    

if __name__ == '__main__':
    main()