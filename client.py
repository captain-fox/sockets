import threading
import socket
import time


class ClientThread(threading.Thread):
    HOST = socket.gethostname()
    sample_data = [i for i in range(1, 500000)]

    def __init__(self, port, name, method, buffer_size, nagle=None):
        threading.Thread.__init__(self)
        self.PORT = port
        self.name = name
        self.method = method
        self.BUFFER_SIZE = buffer_size

    def run(self):
        self.method(str(self.sample_data).encode(), self.HOST, self.PORT, self.BUFFER_SIZE)
        print('Closing thread ' + self.name)


def send_udp(data, host=socket.gethostname(), port=8008, buffer_size=40):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto('SIZE:{}\n'.format(buffer_size).encode(), (host, port))

    package = data[:buffer_size]
    array_pointer = buffer_size

    while package:
        if sock.sendto(package, (host, port)):
            package = data[array_pointer:array_pointer+buffer_size]
            array_pointer += buffer_size
    sock.sendto(b'', (host, port))
    sock.close()
    print('Data sent: {} kb'.format(round(len(data) / 1024)))


def send_tcp(data, host=socket.gethostname(), port=8008, buffer_size=40):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)


    s.connect((host, port))
    s.send('SIZE:{}\n'.format(buffer_size).encode())
    s.sendall(data)
    s.close()
    print('Data sent: {} kb'.format(round(len(data)/1024)))


while True:
    try:
        port = int(input('Port number: '))
        nagle = input('Turn on Nagle: y/n')
        if nagle == 'y':
            pass
        elif nagle == 'n':
            pass
        else:
            raise Exception
        break
    except ValueError:
        print('Oops, port number is digits only')
    except Exception:
        pass

tcp_client_thread = ClientThread(port, 'tcp', send_tcp, 1024)
udp_client_thread = ClientThread(port, 'udp', send_udp, 1024)

udp_client_thread.start()
tcp_client_thread.start()

tcp_client_thread.join()
udp_client_thread.join()
