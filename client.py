import socket
import json


# %%
class Client(object):
    """
     A LocaliteJSON socket client used to communicate with a LocaliteJSON socket server.
    example
    -------
    host = '127.0.0.1'
    port = 6666
    client = Client(True)
    client.connect(host, port).send(data)
    response = client.recv()
    client.close()
    example
    -------
    response = Client().connect(host, port).send(data).recv_close()
    """

    socket = None

    def __init__(self, host, port=6666, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout

    def connect(self):
        "connect wth the remote server"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(self.timeout)

    def close(self):
        "closes the connection"
        self.socket.shutdown(1)
        self.socket.close()
        del self.socket

    def write(self, data):
        packet = data.encode("ascii")
        # print("Writing:", packet)
        self.socket.sendall(packet)
        return self

    def read_byte(self, counter, buffer):
        """read next byte from the TCP/IP bytestream and decode as ASCII"""
        if counter is None:
            counter = 0
        char = self.socket.recv(1).decode("ASCII")
        buffer.append(char)
        counter += {"{": 1, "}": -1}.get(char, 0)
        return counter, buffer

    def read(self):
        "parse the message until it is a valid json"
        counter = None
        buffer = []
        while counter != 0:
            counter, buffer = self.read_byte(counter, buffer)
        response = "".join(buffer)
        return self.decode(response)

    def listen(self):
        self.connect()
        msg = self.read()
        self.close()
        return msg

    def decode(self, msg: str, index=0):
        try:
            decoded = json.loads(msg)
        except json.JSONDecodeError as e:
            print("JSONDecodeError: " + msg)
            raise e

        key = list(decoded.keys())[index]
        val = decoded[key]
        return key, val

    def send(self, msg: str):
        self.connect()
        self.write(msg)
        self.close()

    def request(self, msg='{"ping":"pong"}'):
        self.connect()
        self.write(msg)
        print("Sent:", msg)
        key, val = self.read()
        print("Received:", key, val)
        self.close()
        return val


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=1234)
    parser.add_argument("--msg", dest="message", default='{"ping":"pong"}')
    parser.add_argument("--kill", action="store_true")
    args = parser.parse_args()
    client = Client(host=args.host, port=args.port)
    if args.kill:
        client.request(msg='{"cmd":"poison-pill"}')
    else:
        client.request(msg=args.message)
