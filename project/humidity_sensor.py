import socket
import time
import random

UDP_IP = 'localhost'
UDP_PORT = 5002

def send_humidity_data():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            humidity = round(random.uniform(40, 90),2)
            timestamp = time.time()
            if humidity > 80:
                message = f'HUMID,{humidity}, Time :{timestamp}'
                s.sendto(message.encode(), (UDP_IP, UDP_PORT))
            time.sleep(1)
            if int(timestamp) % 3 == 0:
                s.sendto('ALIVE'.encode(), (UDP_IP, UDP_PORT))
                time.sleep(2)

if __name__ == '__main__':
    send_humidity_data()