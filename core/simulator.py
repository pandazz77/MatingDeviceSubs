import socket
from threading import Thread

def test_handler(a1,a2):
    print(a1,a2)

class UdpCore(Thread):
    def __init__(self,UDP_IP:str,UDP_PORT:int,handle_func:object):
        self.address = UDP_IP
        self.port = UDP_PORT
        self.handle_func = handle_func
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # DGRAM - udp
        self.sock.bind((UDP_IP,UDP_PORT))
        super().__init__()

    def run(self):
        self.listen(self.handle_func)

    def listen(self,handle_func: object):
        while True:
            try:
                data, addr = self.sock.recvfrom(1024)
                handle_func(data,addr)
            except ConnectionResetError as e:
                print(f"{self.address}:{self.port} client: ",e)

class Channel(UdpCore):
    def __init__(self,UDP_IP:str,UDP_PORT:int,sub_dict:dict):
        self.sub_dict = sub_dict # {1:("127.0.0.1",5555),2:("127.0.0.2",5555)}
        super().__init__(UDP_IP,UDP_PORT,self.handle)

    def handle(self,data,addr):
        ADDR_RT = int(data.decode("ascii")[3:8],2)
        self.sock.sendto(data, self.sub_dict[ADDR_RT])

class ChannelSub(UdpCore):
    def __init__(self,UDP_IP:str,UDP_PORT:int,channel_list:list):
        self.channel_list = channel_list # [("127.0.0.1",4000),("127.0.0.1","4001")] - main and backup channels for data distribution
        super().__init__(UDP_IP,UDP_PORT,self.handle)
    
    def handle(self,data, addr):
        print(f"{self.address}:{self.port} ChannelSub received: ",data,addr)

    def send_data(self,data:str):
        for channel in self.channel_list:
            self.sock.sendto(data.encode("ascii"),channel)


# tests
if __name__ == "__main__":
    import sys
    args = sys.argv
    SUB_DICT = {
        1:("127.0.0.1",4001),
        2:("127.0.0.1",4002),
        3:("127.0.0.1",4003)
    }
    
    channel = Channel("127.0.0.1",4000,SUB_DICT)
    device1 = ChannelSub("127.0.0.1",4001)
    device2 = ChannelSub("127.0.0.1",4002)

    channel.start()
    device1.start()
    device2.start()
    for i in range(10):
        device1.sock.sendto("00100010".encode("ascii"),("127.0.0.1",4000))
    
