import socket
import math
import time
import numpy as np
from struct import pack

def genData( t: float, amp: float = 1, phaseshift: float = 0, steps: float = 256, frequency: float = 1):
    omega = 2 * math.pi * frequency
    return amp * math.sin(omega * t / steps + phaseshift * math.pi*2) + amp

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 55555))

try:
    x = 8 # num columns
    y = 5 # num rows
    t = 0
    while True:
        data = []
        for yi in range(y):
            for xi in range(x):
                data.append(pack("=f", genData(t, amp=256, phaseshift=(xi + yi) / x)))
        client.send(b"".join(data))
        t += 1
        if t >= 256:
            t = 0
        time.sleep(0.02)

except KeyboardInterrupt:
    pass

client.close()