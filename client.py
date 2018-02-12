import threading
import socket
import re
import time


class ClientThread(threading.Thread):
    HOST = socket.gethostname()
    sample_data = [i for i in range(1, 250000)]

    def __init__(self, host, port, name, method, buffer_size, nagle=False):
        threading.Thread.__init__(self)
        # self.HOST = host
        self.PORT = port
        self.name = name
        self.method = method
        self.BUFFER_SIZE = buffer_size
        self.nagle = nagle

    def run(self):
        self.method(str(self.sample_data).encode(), self.HOST, self.PORT, self.BUFFER_SIZE, self.nagle)
        print('Closing thread ' + self.name)


def send_udp(data, host=socket.gethostname(), port=8008, buffer_size=40, nagle=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto('SIZE:{}\n'.format(buffer_size).encode(), (host, port))

    package = data[:buffer_size]
    array_pointer = buffer_size

    while package:
        if sock.sendto(package, (host, port)):
            time.sleep(0.01)
            package = data[array_pointer:array_pointer+buffer_size]
            array_pointer += buffer_size
    sock.sendto(b'', (host, port))
    sock.close()
    print('Data sent: {} kb'.format(round(len(data) / 1024)))


def send_tcp(data, host=socket.gethostname(), port=8008, buffer_size=40, nagle=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if nagle:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)

    sock.connect((host, port))
    sock.send('SIZE:{}\n'.format(buffer_size).encode())
    sock.sendall(data)
    sock.close()
    print('Data sent: {} kb'.format(round(len(data)/1024)))


# ---------------- menu
def start_client():
    ip_pattern = re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    while True:
        try:
            port = int(input('Port number: '))
            break
        except ValueError:
            print('Port number should contain digits only')

    while True:
        user_input = input('Turn on Nagle for TCP (y/n): ')
        if user_input == 'y':
            Nagle = True
            break
        elif user_input == 'n':
            Nagle = False
            break
        else:
            print('Invalid input')

    while True:
        try:
            buffer = int(input('Size of buffer (3-4 digits): '))
            break
        except ValueError:
            print('Buffer size should contain digits only')

    while True:
        host = input('IP Address: ')
        ip_test = ip_pattern.match(host)
        if ip_test:
            print(host)
            break
        else:
            print('Invalid IP')

    tcp_client_thread = ClientThread(host, port, 'tcp', send_tcp, buffer, Nagle)
    udp_client_thread = ClientThread(host, port, 'udp', send_udp, buffer)

    udp_client_thread.start()
    tcp_client_thread.start()

    tcp_client_thread.join()
    udp_client_thread.join()


start_client()
