import socket
import fileinput
    
TCP_IP = '128.91.162.76'
TCP_PORT = 8000
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

while True:
	for line in fileinput.input():
		s.send(line.encode())
		print(line)
		
#		data = s.recv(BUFFER_SIZE)
#s.close()

print("received data:", data)