import subprocess
from subprocess import Popen, PIPE, STDOUT
import sys
import io
import time


cmd = ["D:\\Zen\\darknet\\build\\darknet\\x64\\darknet.exe", "detector", "demo", "data/coco.data", "yolo.cfg", "yolo.weights", "http://10.103.212.12:8000/camera/mjpeg", "-i", "0"]
# subprocess.call(cmd)


# p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False)

filename = 'test.log'
with io.open(filename, 'wb') as writer, io.open(filename, 'rb', 1) as reader:
    process = subprocess.Popen(cmd, stdout=writer)
    while process.poll() is None:
        sys.stdout.write(reader.readline())
        time.sleep(0.5)
    # Read the remaining
    sys.stdout.write(reader.readline())

# while True:
# 	output = p.stdout.read()
# 	print output
# with Popen(command, stdin=PIPE, stdout=PIPE, universal_newline=True) as process:
#     with process.stdin as pipe:
#         pipe.write(json.dumps(data))
#     for line in process.stdout:
#         print(line, end='')
#         process(line)


