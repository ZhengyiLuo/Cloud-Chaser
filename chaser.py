import socket
import fileinput
import time
import sys
import errno

### PARSING ###

valid_objects = ["bottle"]

# append_from_split = ""

def parse_line(line):

		# print("this is the line\"" +line + "\"")
		# global append_from_split

		split_line = line.split('\n')
		# line = append_from_split + split_line[0]
		# append_from_split = split_line[1]

		tokens = line.split(' ')

		for i in range(len(tokens)):

				token_len = len(tokens[i])

				if token_len != 0:
					if tokens[i][token_len - 1] == ",":
						tokens[i] = tokens[i][0 : token_len - 1]

		left = 0
		right = 0
		top = 0
		bottom = 0
		obj_id = 0
		obj = ""
		prob = 0.0

		for i in range(len(tokens)):
			if "=" in tokens[i]:
				token_name = tokens[i].split("=")[0]
				token_val  = tokens[i].split("=")[1]

				#print(repr(token_val))

				if (len(token_name) > 0 and len(token_val) > 0):

					if ("left" == token_name): left = int(token_val)
					elif("right" == token_name): right = int(token_val)
					elif ("top" == token_name): top = int(token_val)
					elif ("bottom" == token_name): bottom = int(token_val)
					elif ("obj_id" == token_name): obj_id = int(token_val)
					elif ("obj" == token_name): obj = token_val
					else: prob = float(token_val.strip())

		return (left, right, top, bottom, obj_id, obj, prob)

def is_valid_object(line):
		parsed = parse_line(line)
		return parsed[5] in valid_objects


LAG = 2
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 500

filename = 'test.log'

	
TCP_IP_YOLO = '158.130.62.103'
TCP_PORT = 8886
BUFFER_SIZE = 10000  # Normally 1024, but we want fast response

s_yolo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_yolo.bind((TCP_IP_YOLO, TCP_PORT))
s_yolo.listen(1)

TCP_IP_ALEXA = '158.130.62.103'
TCP_PORT_ALEXA = 8882
BUFFER_SIZE = 10000  # Normally 1024, but we want fast response

s_alexa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_alexa.bind((TCP_IP_ALEXA, TCP_PORT_ALEXA))
s_alexa.listen(1)

TCP_IP_PI = '10.103.212.12'
# TCP_IP_PI = '128.91.162.76'
TCP_PORT_PI = 8888
MESSAGE = "Hello, World!\n"
s_pi = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s_pi.connect((TCP_IP_PI, TCP_PORT_PI))

alexa_conn, alexa_addr = s_alexa.accept()
conn, addr = s_yolo.accept()
print('Socket connection address:', addr)
print('Alexa connection address:', alexa_addr)

## PARSING CODE ##
have_target = False
found_target = False

# print('Enter Target:')
# target = sys.stdin.readline()
# target = target[0:target.find("\n")]

tol = 30

alexa_conn.setblocking(False)
conn.setblocking(False)

target = "stoptrack"

while 1:

	## See if we have a new target from Alexa ##
	try:
		possible_target = alexa_conn.recv(BUFFER_SIZE).strip()
		print("Target switched to: " + possible_target)
		if (possible_target != ""):
			target = possible_target
			have_target = True
		else:
			target = "stoptrack"
			have_target = False
	except socket.error as e:
		if e.errno == errno.ECONNRESET:
			print("Tyring to reconnect")
			s_alexa.bind((TCP_IP_ALEXA, TCP_PORT_ALEXA))
			s_alexa.listen(1)
		else :
			print("rip")

	## do we have a target? ##
	if target != "stoptrack":
		have_target = True
	else:
		have_target = False

	## Clear buffer before going into the main parsing ##
	if have_target:
		while True:
			try:
				data = conn.recv(BUFFER_SIZE)
				if (data == ""): 
					break
			except socket.error:
				break

	
	found_target = False
	LAG = 2

	time.sleep(LAG) ## TODO: Possibly remove (check if we don't need)

	## Run through 20 lines of YOLO looking for the object ##
	try:
		line = conn.recv(BUFFER_SIZE)
		lines = line.split("\n")
		for i in lines:
			parsed = parse_line(i)

			if parsed[5] == target:
				found_target = True
				LAG = 1
				left = parsed[0]
				right = parsed[1]
				break
	except socket.error:
		pass

	## If we've found our target, set the signal to be the movement ##
	if found_target:
		print("found target")
		x_mid = (left + right) / 2

		if x_mid > SCREEN_WIDTH / 2 + tol:
			MESSAGE = "Right,1.3\n"
		elif x_mid < SCREEN_WIDTH / 2 - tol:
			MESSAGE = "Left,1.3\n"
		else:
			MESSAGE = "Forward,1.3\n"

	## Otherwise the pi should spin looking for it ##
	## TODO: check if target is null, and if so stop ##
	elif target == "stoptrack":
		MESSAGE = "Stop,0.3\n"
	else:
		MESSAGE = "Spin,0.3\n"

	## send the signal ##
	print(MESSAGE)
	s_pi.send(MESSAGE.encode())






