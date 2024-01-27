import socket
import threading
import time
import json
import logging

logging.basicConfig(filename='gateway.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TCP_IP = 'localhost'
TCP_PORT = 5001
UDP_IP = 'localhost'
UDP_PORT = 5002
OUTPUT_TCP_PORT = 5003

humidity_sensor_off_event = threading.Event()

def handle_temperature_connection(conn, addr):
    last_temp_time = time.time()
    is_handshake_printed = False  # Handshake mesajı kontrolü

    while True:
        try:
            data = conn.recv(1024)

            if not data:
                print('TEMP SENSOR OFF')
                break

            print(f'Received temperature data from {addr}: {data.decode()}')
            logging.info(f'Received temperature data from {addr}: {data.decode()}')

            # Create a dictionary for temperature data
            temp_data = {
                'type': 'temperature',
                'value': float(data.decode().split(',')[1]) if len(data.decode().split(',')) > 1 else 0
            }

            # Convert the dictionary to a JSON string
            temp_json = json.dumps(temp_data)

            # Send the JSON string to TCP port 5003
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as output_socket:
                output_socket.connect((TCP_IP, OUTPUT_TCP_PORT))
                output_socket.sendall("HANDSHAKE".encode())  # Sending handshake message
                response = output_socket.recv(1024)  # Waiting for server's response
                if response.decode() == "HANDSHAKE_OK" and not is_handshake_printed:
                    print("Handshake successful with server.")
                    logging.info("Handshake successful with server.")
                    is_handshake_printed = True
                output_socket.sendall(temp_json.encode())

            last_temp_time = time.time()

        except Exception as e:
            if time.time() - last_temp_time > 3:
                print('TEMP SENSOR OFF')
                print('Trying to reconnect in 5 seconds...')
                logging.info('TEMP SENSOR OFF')
                logging.info('Trying to reconnect in 5 seconds...')
                time.sleep(1)
                break


def handle_humidity_connection(sock):
    didprint = False
    is_handshake_printed = False  

    with sock:
        try:
            sock.setblocking(0)
        except:
            print("Humidity sensor off")
            logging.info("Humidity sensor off")
            pass

        # Set the socket to non-blocking mode
        last_alive_time = time.time()

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                if not data:
                    print('HUMIDITY SENSOR OFF')
                    logging.info('HUMIDITY SENSOR OFF')
                    pass

                print(f'Received humidity data from {addr}: {data.decode()}')
                logging.info(f'Received humidity data from {addr}: {data.decode()}')
                didprint = False
                humidity_sensor_off_event.clear()

                # Create a dictionary for humidity data
                humidity_data = {
                    'type': 'humidity',
                    'value': float(data.decode().split(',')[1]) if len(data.decode().split(',')) > 1 else 'ALIVE'
                }

                # Convert the dictionary to a JSON string
                humidity_json = json.dumps(humidity_data)

                # Send the JSON string to TCP port 5003
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as output_socket:
                    output_socket.connect((TCP_IP, OUTPUT_TCP_PORT))
                    output_socket.sendall("HANDSHAKE".encode())  # Sending handshake message
                    response = output_socket.recv(1024)  # Waiting for server's response
                    if response.decode() == "HANDSHAKE_OK" and not is_handshake_printed:
                        print("Handshake successful with server.")
                        logging.info("Handshake successful with server.")
                        is_handshake_printed = True
                    output_socket.sendall(humidity_json.encode())

                # Check for 'ALIVE' message from humidity sensor
                if data == b'ALIVE':
                    last_alive_time = time.time()
                if not humidity_sensor_off_event.is_set():
                    pass

            except socket.error as e:
                # Check for timeout (no data received)
                if 'timed out' in str(e):
                    pass

            # Check for 'HUMIDITY SENSOR OFF' if no 'ALIVE' received for more than 7 seconds
            if time.time() - last_alive_time > 7:
                if didprint == False:
                    print('HUMIDITY SENSOR OFF')
                    print('Trying to reconnect in 5 seconds...')
                    logging.info('HUMIDITY SENSOR OFF')
                    logging.info('Trying to reconnect in 5 seconds...')
                    didprint = True
                humidity_sensor_off_event.set()
                time.sleep(1)


if __name__ == '__main__':
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as temp_server, \
                socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as hum_server:

                temp_server.bind((TCP_IP, TCP_PORT))
                temp_server.listen()

                hum_server.bind((UDP_IP, UDP_PORT))

                print('Gateway is listening for connections...')
                logging.info('Gateway is listening for connections...')

                hum_thread = threading.Thread(target=handle_humidity_connection, args=(hum_server,))

                if hum_thread.is_alive() == False:
                    hum_thread.start()

                temp_thread = threading.Thread(target=handle_temperature_connection, args=temp_server.accept())
                if temp_thread.is_alive() == False:
                    temp_thread.start()
                time.sleep(1)  # Sleep briefly to allow threads to start

                while temp_thread.is_alive() or not humidity_sensor_off_event.is_set():
                    try:
                        if not temp_thread.is_alive():
                            temp_thread = threading.Thread(target=handle_temperature_connection, args=temp_server.accept())
                            temp_thread.start()

                    except:
                        pass

        except Exception as e:
            print(f"Error: {e}")
            logging.info(f"Error: {e}")
