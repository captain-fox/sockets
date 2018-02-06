import threading
import socket
import random
import time


def serve_udp(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    print(sock)
    BUFFER_SIZE = 20


def serve_tcp(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    print(sock)
    BUFFER_SIZE = 20


def test_method(thread_name, port, host):

    for i in range(0, 10):
        print('Thread ' + thread_name + str(i) + ' at port ' + str(port))
        time.sleep(random.randrange(1, 10, 1)/100)


class ServerThread(threading.Thread):
    HOST = socket.gethostname()

    def __init__(self, port, name, method):
        threading.Thread.__init__(self)
        self.PORT = port
        self.name = name
        self.method = method

    def run(self):
        print('Starting thread ' + self.name)
        self.method(self.HOST, self.PORT)
        print('Quitting thread ' + self.name)


tcp_thread = ServerThread(8008, 'tcp', serve_tcp)
udp_thread = ServerThread(8008, 'udp', serve_udp)

tcp_thread.start()
udp_thread.start()
tcp_thread.join()
udp_thread.join()