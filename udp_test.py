import socket
import random
import time
import sys


def server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Listening on port {port}")
    server_socket.bind(('0.0.0.0', port))


    while True:
        message, address = server_socket.recvfrom(1024)
        message = str(message, 'utf-8')
        delay = 0.1 * random.randint(1,14)
        print(f"Response in {delay:.2f}s | {message} from {address}")
        time.sleep(delay)
        response = bytes(f"I got your '{message}'", 'utf-8')
        server_socket.sendto(response, address)


def client(host, port):
    TICK = 1/5.0
    emitting = True

    messages = ["Hi", "hello", "ciao", "aloha", "salutations", "greetings", "yo"]

    print(f"Using {host}:{port}")
    addr = (host, port)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1)

    i = 0
    while True:
        try:
            if emitting:
                i += 1
                message = bytes(f"{i}: {random.choice(messages)}", 'utf-8')
                client_socket.sendto(message, addr)

            try:
                data, server = client_socket.recvfrom(1024)
                print(f"{data} returned from {server}")
            except TimeoutError:
                if emitting:
                    print(f"(Dropped {message})")

            if emitting:
                time.sleep(TICK)
        except KeyboardInterrupt:
            if emitting:
                print("\nStopped emitting new messages. Here are the remainder responses:\n")
                emitting = False
            else:
                raise

def main():
    try:
        if not sys.argv[1:]:
            print("Specify 'client' or 'server'")

        elif sys.argv[1] == "server":
            port = int(sys.argv[2]) if sys.argv[2:] else 12000
            server(port)

        elif sys.argv[1] == "client":
            host = sys.argv[2] if sys.argv[2:] else "127.0.0.1"
            port = int(sys.argv[3]) if sys.argv[3:] else 12000
            client(host, port)

        else:
            print("Unknown mode")

    except KeyboardInterrupt:
        print("\nQuit.")

main()

