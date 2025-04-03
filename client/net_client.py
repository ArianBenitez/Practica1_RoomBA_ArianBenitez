# client/net_client.py
import socket
import json

class NetClient:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
        except Exception as e:
            print("Error connecting to server:", e)
            self.sock = None

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def send_cmd(self, cmd_dict):
        if not self.sock:
            print("Socket is not connected")
            return None
        try:
            data_str = json.dumps(cmd_dict)
            self.sock.sendall(data_str.encode('utf-8'))
            resp = self.sock.recv(4096)
            if not resp:
                return None
            try:
                return json.loads(resp.decode('utf-8'))
            except:
                return resp.decode('utf-8')
        except Exception as e:
            print("Error in send_cmd:", e)
            return None
