import socket, threading

threads = []
ports = [(25565,25565,'172.16.36.136')]

def tunnel(receiver, sender):
    receiver.settimeout(None)
    while (True):
        msg = receiver.recv(4096)
        if len(msg) == 0:
            # if one or the other can no longer recieve
            # close the siblings receiver read
            # close our receivers write since the other already closed our read
            # may cause some exceptions but the thread is done anyway
            sender.shutdown(socket.SHUT_RD)
            receiver.shutdown(socket.SHUT_WR)
            break
        else:
            sender.sendall(msg)

class server(object):
    finished = False

    def run(self, inner_port, outer_port, destination):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.bind(('', inner_port))
        server_sock.listen(5)
        server_sock.settimeout(5)
        while not self.finished:
            try:
                incoming_connection = server_sock.accept()
                outgoing_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                outgoing_connection.connect((destination, outer_port))
                t1 = threading.Thread(target=tunnel, args=(incoming_connection[0], outgoing_connection))
                t2 = threading.Thread(target=tunnel, args=(outgoing_connection, incoming_connection[0]))
                t1.start()
                t2.start()
            except socket.timeout:
                pass

def run_server(*args):
    server().run(*args)

for port in ports:
    thread = threading.Thread(target=run_server, args=port)
    thread.start()
    threads.append(thread)

while True:
    try:
        command = raw_input('>>> ')
        if command == 'end':
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print "Asking threads to exit..."
        server.finished = True
        for thread in threads:
            thread.join()
        break

print "Done"
