import threading
import struct
import socket
import time


class ServerThread(threading.Thread):
    HOST = socket.gethostname()

    def __init__(self, port, name, method):
        threading.Thread.__init__(self)
        self.PORT = port
        self.name = name
        self.method = method

    def run(self):
        self.method(self.HOST, self.PORT, self.name)
        print('Closing thread ' + self.name)


def show_statistics(name, received, time_elapsed, rate, buffer_size):
    print('Thread {}: received {} kb within {} seconds at rate {} kb/s using buffer size of {}\n'
          .format(name, received, time_elapsed, rate, buffer_size))


def serve_udp(host, port, name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    while True:
        data = bytes()

        raw_buffer_size, address = sock.recvfrom(9)
        print('Thread UDP acquired connection from' + str(address))
        if raw_buffer_size.decode()[:5] == 'SIZE:':
            try:
                buffer_size = int(raw_buffer_size[5:])
                sock.settimeout(5)
                start = time.time()
                while True:
                    buffer, address = sock.recvfrom(buffer_size)
                    if not buffer:
                        break
                    data += buffer
                end = time.time()
                show_statistics(name, round(len(data) / 1024), round(end - start, 2), int((len(data) / 1024) / (end - start)), buffer_size)

            except ValueError:
                print('Size is not int, received {}\n'.format(raw_buffer_size))

            except socket.timeout:
                end = time.time()
                print('Time elapsed')
                show_statistics(name, round(len(data) / 1024), round(end - start, 2), int((len(data) / 1024) / (end - start)), buffer_size)

            sock.settimeout(None)


def serve_tcp(host, port, name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))

    while True:
        data = bytes()

        sock.listen()
        connection, address = sock.accept()
        print('Thread TCP acquired connection from' + str(address))

        raw_buffer_size = connection.recv(9)
        decoded_buffer_size = raw_buffer_size.decode()
        if decoded_buffer_size[:5] == 'SIZE:':
            try:
                buffer_size = int(decoded_buffer_size[5:])

                start = time.time()
                while True:
                    package = connection.recv(buffer_size)
                    if not package:
                        break
                    data += package

                end = time.time()
                show_statistics(name, round(len(data) / 1024), round(end - start, 2), int((len(data)/1024) / (end - start)), buffer_size)

                connection.close()

            except ValueError:
                print('Size is not int, received {}\n'.format(raw_buffer_size))
                connection.close()

            except Exception as e:
                print('Unknown exception occurred\n', e)

        elif decoded_buffer_size[:4] == 'FINE':
            connection.close()
            break
        else:
            connection.close()
            print('SIZE parameter missing\n')


def serve_multicast(host, port, name):
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 9999

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, address = sock.recv(10)
        if data.startswith('DISCOVER'):
            print('discover received')


def start_server():
    while True:
        try:
            port = int(input('Port number: '))
            break
        except ValueError:
            print('Oops, port number is digits only')

    tcp_server_thread = ServerThread(port, 'tcp', serve_tcp)
    udp__server_thread = ServerThread(port, 'udp', serve_udp)
    multicast_server_thread = ServerThread(port, 'cast', serve_multicast)

    udp__server_thread.start()
    tcp_server_thread.start()
    # multicast_server_thread.start()
    tcp_server_thread.join()
    udp__server_thread.join()
    # multicast_server_thread.join()


start_server()
