import threading
from .receivers import read_can, read_usb
from .monitor_runner import run_monitor

#main program that orchestrates the threads

t1 = threading.Thread(target=read_can, daemon=True)
t2 = threading.Thread(target=read_usb, daemon=True)

t2.start()
t1.start()

# run monitoring in main thread
run_monitor()