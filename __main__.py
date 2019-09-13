from scanner.scanAndStore_Rssi import run as run_save
from sender.post_data import run as run_send
from sender.retry_data import run as run_retry
from threading import Thread
import signal

if __name__ == '__main__':
    saveThread = Thread(target=run_save)
    sendThread = Thread(target=run_send)
    retryThread = Thread(target=run_retry)

    saveThread.start()
    sendThread.start()
    retryThread.start()
