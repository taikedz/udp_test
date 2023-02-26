import socket
import random
import time
import sys

import json

from datetime import datetime
import threading


class Delayer(threading.Thread):
    def __init__(self, delay, lock, operation, *args, **kwargs):
        threading.Thread.__init__(self)

        self._delay = delay
        self._lock = lock

        self._op = operation
        self._args = args
        self._kwarg = kwargs


    def run(self):
        time.sleep(self._delay)

        with self._lock:
            self._op(*self._args, **self._kwargs)


def server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Listening on port {port}")
    server_socket.bind(('0.0.0.0', port))

    server_lock = threading.Lock()


    while True:
        message, address = server_socket.recvfrom(1024)
        message = Message.decode(message)

        delay = 0.1 * random.randint(1,14)
        response = Message.encode({"id": message["id"], "echo": message["message"]})

        print(f"Response in {delay:.2f}s | {address} --> {message}")
        Delayer(delay, server_lock, server_socket.sendto, response, address).start()


class MessageStash(threading.Thread):
    tick = 1/10e1

    def __init__(self, timeout=1):
        threading.Thread.__init__(self, daemon=True)

        self._message_lock = threading.RLock()
        self._stash = {}
        self._timeout = timeout

    def run(self):
        while True:
            self.clear_timed_out_messages()
            time.sleep(self.tick)


    def clear_timed_out_messages(self):
        tN = datetime.now()
        cleanout = []
        with self._message_lock:
            for message_id, data in self._stash.items():
                t0, message = data
                if (tN-t0).total_seconds() >= self._timeout:
                    print(f"Stash timed out: {message_id}")
                    cleanout.append(message_id)

            for M in cleanout:
                self.rem(M)


    def add(self, message_id, message):
        with self._message_lock:
            if message_id in self._stash:
                raise KeyError("Cannot set '{message}' --> message already present: {message_id} : {self._stash[message_id][1]}")
            self._stash[message_id] = (datetime.now(), message)


    def rem(self, message_id):
        with self._message_lock:
            if message_id in self._stash:
                del self._stash[message_id]
                return True
            return False


class Message:
    @staticmethod
    def encode(data_dict):
        return bytes(json.dumps(data_dict), 'utf-8')

    @staticmethod
    def decode(data_bytes):
        return json.loads(str(data_bytes, 'utf-8'))


class Stoppable:
    def __init__(self):
        self._stoppable_running = True

    def stop(self):
        self._stoppable_running = False

    def is_running(self):
        return self._stoppable_running



class UdpClientEmitter(threading.Thread, Stoppable):
    tick = 1/5.0
    messages = ["hi", "hello", "ciao", "aloha", "salutations", "greetings", "yo"]


    def __init__(self, connection, lock, message_stash, addr):
        threading.Thread.__init__(self, daemon=True)
        Stoppable.__init__(self)

        self._conn = connection
        self._lock = lock
        self._addr = addr
        self._shared_stash = message_stash


    def run(self):
        i = 0

        while True:
            i += 1
            msg_id = f"msg_{i}"
            message = Message.encode({"id": msg_id, "message": f"{i}: {random.choice(self.messages)}"})

            with self._lock:
                self._conn.sendto(message, self._addr)
                self._shared_stash.add(msg_id, message)

            if not self.is_running():
                break
            time.sleep(self.tick)


class UdpClientListener(threading.Thread, Stoppable):
    tick = 1/5.0

    def __init__(self, connection, lock, message_stash):
        threading.Thread.__init__(self, daemon=True)
        Stoppable.__init__(self)
        self._lock = lock
        self._conn = connection
        self._shared_stash = message_stash


    def run(self):
        while True:
            try:
                with self._lock:
                    data, server = self._conn.recvfrom(1024)

                data = Message.decode(data)
                m_id = data["id"]

                if self._shared_stash.rem(m_id):
                    print(f"{server} returned: {data['echo']}")
                else:
                    print(f"Received timed out message {m_id}, dropping")

            except TimeoutError: pass

            if not self.is_running():
                break
            time.sleep(self.tick)



class UdpClient:

    def __init__(self, host, port):
        self.addr = (host,port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.settimeout(1)
        self._conn_lock = threading.Lock()


    def run(self):
        shared_stash = MessageStash(timeout=1)
        listener = UdpClientListener(self.client_socket, self._conn_lock, shared_stash)
        emitter = UdpClientEmitter(self.client_socket, self._conn_lock, shared_stash, self.addr)

        shared_stash.start()
        listener.start()
        emitter.start()

        while True:
            try:
                time.sleep(1/10e2)
            except KeyboardInterrupt:
                if emitter.is_running():
                    emitter.stop()
                    print("\nStopped emitter. Waiting for remaining messsages.")
                else:
                    print("\nQuit\n")
                    break


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
            UdpClient(host, port).run()

        else:
            print("Unknown mode")

    except KeyboardInterrupt:
        print("\nQuit.")

main()

