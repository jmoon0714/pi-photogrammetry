from datetime import timedelta

BUFFER_SIZE = 1024
NETWORK_ID = '192.168.0'
HANDSHAKE = str.encode("Hello Pi Server")
HANDWAVE = 'Goodbye.'.encode()

HOST_IDS = [
            '201','202','203','204','205','206','207','208','209','210',
            '211','212','213','214','215','216','217','218','219','220',
            '221','222','223','224','225','226','227','228','229','230',
            '231','232','233','234','235','236','237','238','239','240',
            '241','242','243','244','245','246','247','248','249','250',
            ]
BLOCK_LIST = [
            '202','204', '208', '212', '216', '220', '224', '228', '232', '236', '240', '244', '248', '249', '250',
            ]

PORT = 20001
BARRIER_THRESHOLD = len(HOST_IDS) - len(BLOCK_LIST)
BUFFER_SIZE = 1024
DELAY = timedelta(seconds=10)
TIMEOUT = timedelta(seconds=100)

if __name__ == "__main__":
    print ("[PARAM]:\tbarrier threshold:", BARRIER_THRESHOLD)