import threading
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
        self.method(self.HOST, self.PORT)
        print('Closing thread ' + self.name)


def serve_udp(host, port):
    sample_data = str([i for i in range(1, 500000)]).encode()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))

    data = bytes()
    size, address = sock.recvfrom(9)
    print('Thread UDP acquired connection from' + str(address))
    buffer_size = int(size[5:])
    start = time.time()
    while True:
        buffer, address = sock.recvfrom(buffer_size)
        if not buffer:
            break
        data += buffer
    end = time.time()
    print('Thread UDP: received {} kb within {} seconds at rate {} kb/s\n'
          .format(round(len(data) / 1024), round(end - start, 2), int((len(data) / 1024) / (end - start))))


def serve_tcp(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))

    while True:
        sock.listen(1)
        connection, address = sock.accept()
        print('Thread TCP acquired connection from' + str(address))

        raw_buffer_size = connection.recv(9)
        decoded_buffer_size = raw_buffer_size.decode()
        data = bytes()
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
                print('Thread TCP: received {} kb within {} seconds at rate {} kb/s\n'
                      .format(round(len(data)/1024), round(end-start, 2), int((len(data)/1024)/(end-start))))
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


while True:
    try:
        port = int(input('Port number: '))
        break
    except ValueError:
        print('Oops, port number is digits only')

tcp_server_thread = ServerThread(port, 'tcp', serve_tcp)
udp__server_thread = ServerThread(port, 'udp', serve_udp)


udp__server_thread.start()
tcp_server_thread.start()
tcp_server_thread.join()
udp__server_thread.join()
