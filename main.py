import socket
import time

host = '10.42.0.137'
port = 5000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

client.send(f'Send from WiFi to serial {time.time()}\n'.encode())

while True:
    data = client.recv(1024)
    print(data.hex())