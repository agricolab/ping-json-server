import socket
import json
import threading


def decode(msg):
    try:
        msg = msg.decode("ascii")
        return json.loads(msg)
    except Exception as e:  # pragma no cover
        # print("JSONDecodeError:", msg)
        return None


def has_poison(payload) -> bool:
    try:
        return payload["cmd"] == "poison-pill"
    except Exception as e:
        return False


def read_msg(client: socket.socket):
    """parse the message until it is a valid Payload and return the first"""
    msg = bytearray(b" ")
    while True:
        try:
            prt = client.recv(1)
            # print(prt)
            if prt == b"":
                print("EOF")
                return None
            msg += prt
            payload = decode(msg)
            if payload is not None:
                return payload

        except Exception as e:  # pragma no cover
            print(e)
            return None


# -----------------------------------------------------------------------------
class PingServer(threading.Thread):
    def __init__(self, port: int = 1234, host=None):
        threading.Thread.__init__(self)
        if host is None:
            hostname = socket.gethostname()
            host = socket.gethostbyname(hostname)
        self.host = host
        self.port = port
        self.is_running = threading.Event()

    def await_running(self):
        while not self.is_running.is_set():  # pragma no cover
            pass

    def run(self):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((self.host, self.port))
        listener.listen(1)  # one  unaccepted client is allowed
        self.is_running.set()
        print(f"Server {self.host}:{self.port} started")
        while self.is_running.is_set():
            try:
                client, address = listener.accept()
                payload = read_msg(client)
                print(f"Received: {payload}")
                if not payload:
                    continue
                for k, v in payload.items():
                    reply = {v: k}
                client.sendall(json.dumps(reply).encode("ascii"))
                print(f"Sent: {payload}")
                if has_poison(payload):
                    self.is_running.clear()
                    break
            except Exception as e:  # pragma no cover
                print(e)
            finally:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
        print("Shutting server down")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument("--host", dest="host", default="127.0.0.1")
    parser.add_argument("--port", dest="port", type=int, default=1234)
    args = parser.parse_args()
    ps = PingServer(host=args.host, port=args.port)
    ps.start()
    ps.await_running()
