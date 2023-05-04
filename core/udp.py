import socket
from threading import Thread
from time import sleep

class UdpCore(Thread):
    def __init__(self,UDP_IP:str,UDP_PORT:int,handle_func:object):
        self.UDP_IP = UDP_IP
        self.UDP_PORT = UDP_PORT
        self.handle_func = handle_func
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # DGRAM - udp
        self.sock.bind((UDP_IP,UDP_PORT))
        super().__init__()

    def run(self):
        self.listen(self.handle_func)

    def listen(self,handle_func: object):
        while True:
            try:
                data, addr = self.sock.recvfrom(2048)
                handle_func(data,addr)
            except ConnectionResetError as e:
                print(f"{self.UDP_IP}:{self.UDP_PORT} client: ",e)

"""
class Channel(UdpCore):
    def __init__(self,UDP_IP:str,UDP_PORT:int,sub_dict:dict):
        self.sub_dict = sub_dict # {1:("127.0.0.1",5555),2:("127.0.0.2",5555)}
        super().__init__(UDP_IP,UDP_PORT,self.handle)

    def handle(self,data,addr):
        ADDR_RT = int(data.decode("ascii")[3:8],2)
        if ADDR_RT == 31: # sending data to all subs
            for client in self.sub_dict.values():
                self.sock.sendto(data, client)
        else:
            self.sock.sendto(data, self.sub_dict[ADDR_RT])
"""

class UdpClient(UdpCore):
    def __init__(self,UDP_IP:str,UDP_PORT:int,endpoint:tuple=None):
        # Socket endpoint (second client)
        # endpoints is a tuple: (str(IP),int(PORT))
        # Example: endpoint = ("192.168.0.1",2000)
        self.endpoint = endpoint
        super().__init__(UDP_IP,UDP_PORT,self.handle)
    
    def handle(self,data, addr):
        print(f"{self.UDP_IP}:{self.UDP_PORT} < {addr[0]}:{addr[1]}: {data}")

    def send_data(self,data:str,endpoint=None):
        if not endpoint: endpoint = self.endpoint # if endpoint isnt set use endpoint from args
        print(f"{self.UDP_IP}:{self.UDP_PORT} > {endpoint[0]}:{endpoint[1]}: {data}")
        self.sock.sendto(data.encode("ascii"),endpoint)


# tests
if __name__ == "__main__":
    import sys
    args = sys.argv
    listener = UdpClient("127.0.0.1",5010)
    listener.daemon = True
    listener.start()
    while True: sleep(1)
    #listener.join()
    