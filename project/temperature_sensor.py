import socket
import time
import random

TCP_IP = 'localhost'
TCP_PORT = 5001

def send_temperature_data():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((TCP_IP, TCP_PORT))
        while True:
            temperature = round(random.uniform(20, 30),2)
            timestamp = time.time()
            message = f'TEMP,{temperature}, Time :{timestamp}'
            s.sendall(message.encode())
            time.sleep(1)

if __name__ == '__main__':
    send_temperature_data()