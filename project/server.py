import threading
import socket
import json
import logging

logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TCP_IP = 'localhost'
TCP_PORT = 8080
GATEWAY_PORT = 5003  # Port for gateway connections
BUFFER_SIZE = 1024

# Data storage for temperature and humidity
data_storage = {
    'temperature': [],
    'humidity': []
}
data_lock = threading.Lock()  # Lock for thread-safe access to data_storage

# Handle incoming data from gateway
def handle_gateway_connection(conn, addr):
    with conn:
        try:
            print(f"Gateway connection accepted from {addr}")
            logging.info(f"Gateway connection accepted from {addr}")
            handshake_message = conn.recv(BUFFER_SIZE)
            if handshake_message.decode() == "HANDSHAKE":
                conn.sendall("HANDSHAKE_OK".encode())  
                
            while True:
                data = conn.recv(BUFFER_SIZE)           
                if not data:
                    break
                message = json.loads(data.decode()) # Convert JSON string to dictionary
                if message['value'] == 'ALIVE':
                    print(f"ALIVE message received from {addr}")
                    logging.info(f"ALIVE message received from {addr}")
                else:
                    with data_lock:
                        data_storage[message['type']].append(message['value'])
                        print(f"Data received from gateway: Type={message['type']}, Value={message['value']}")
                        logging.info(f"Data received from gateway: Type={message['type']}, Value={message['value']}")
        except Exception as e:
            print(f"Error handling gateway connection: {e}")
            logging.error(f"Error handling gateway connection: {e}")


# Construct HTTP response for the given path
def construct_http_response(path):
    with data_lock:
        if path == '/temperature':
            title = "Temperature Data"
            data = '<br>'.join(str(temp) for temp in data_storage['temperature'])
        elif path == '/humidity':
            title = "Humidity Data"
            data = '<br>'.join(str(hum) for hum in data_storage['humidity'])
        elif path == '/gethumidity':
            title = "Last Humidity Value"
            real_humidity_values = [v for v in data_storage['humidity'] if isinstance(v, (int, float))]
            last_real_value = real_humidity_values[-1] if real_humidity_values else "No real humidity data available"
            data = str(last_real_value)
        else:
            title = "Invalid Path"
            data = "Invalid path"

        html_content = f"""
        <html>
        <head><title>{title}</title></head>
        <body>
            <h1>{title}</h1>
            <p>{data}</p>
        </body>
        </html>
        """
        return f"HTTP/1.1 200 OK\nContent-Type: text/html\n\n{html_content}".encode()

# Handle HTTP client connections
def handle_client_connection(client_socket, addr):
    try:
        data = client_socket.recv(BUFFER_SIZE)  # Receive data from client
        if not data:
            return

        request_line = data.decode().split('\n')[0]
        path = request_line.split()[1]
        response = construct_http_response(path)
        client_socket.sendall(response)
    except Exception as e:
        print(f"Error handling client connection from {addr}: {e}")
        logging.error(f"Error handling client connection from {addr}: {e}")
    finally:            
        client_socket.close()   # Close the client socket
        print(f"Connection closed with {addr}")
        logging.info(f"Connection closed with {addr}")

# Start the HTTP server
def start_http_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     
    server_socket.bind((TCP_IP, TCP_PORT))
    server_socket.listen(5)         
    print(f"HTTP server listening on {TCP_IP}:{TCP_PORT}...")       
    logging.info(f"HTTP server listening on {TCP_IP}:{TCP_PORT}...")

    # Start the thread for accepting gateway connections
    gateway_conn_thread = threading.Thread(target=accept_gateway_connections)
    gateway_conn_thread.start()

    # Accept and handle client connections
    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, addr))
        client_thread.start()

# Accept connections from the gateway
def accept_gateway_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as gateway_socket:
        gateway_socket.bind((TCP_IP, GATEWAY_PORT))
        gateway_socket.listen()
        while True:
            conn, addr = gateway_socket.accept()
            gateway_thread = threading.Thread(target=handle_gateway_connection, args=(conn, addr))
            gateway_thread.start()

if __name__ == "__main__":
    start_http_server()
