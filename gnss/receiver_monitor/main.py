import threading
from .receiver_ETH import read_eth
from .receiver_USB import read_usb

#main program for the project

t1 = threading.Thread(target=read_eth)
t2 = threading.Thread(target=read_usb)

t1.start()
t2.start()

t1.join()
t2.join()