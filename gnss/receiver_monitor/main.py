import threading
from .receivers import read_eth, read_usb
from .monitoring import run_monitor

#main program that orchestrates the threads

t1 = threading.Thread(target=read_eth, daemon=True)
t2 = threading.Thread(target=read_usb, daemon=True)

t1.start()
t2.start()

# run monitoring in main thread
run_monitor()