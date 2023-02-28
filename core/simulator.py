import socket
from threading import Thread

class UdpCore(Thread):
    def __init__(self,UDP_IP:str,UDP_PORT:int,handle_func:object):
        self.ip = UDP_IP
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
                print(f"{self.ip}:{self.port} client: ",e)

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

class ChannelSub(UdpCore):
    def __init__(self,UDP_IP:str,UDP_PORT:int,channel_list:list):
        self.channel_list = channel_list # [("127.0.0.1",4000),("127.0.0.1","4001")] - main and backup channels for data distribution
        super().__init__(UDP_IP,UDP_PORT,self.handle)
    
    def handle(self,data, addr):
        print(f"\n{self.ip}:{self.port} ChannelSub received: ",data,addr)

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
        3:("127.0.0.1",4003),
        4:("127.0.0.1",4004)
    }
    CHANNEL_LIST = [
        ("127.0.0.1",4000)
    ]

    def test_handler(a1,a2):
        print(a1,a2)

    if len(args)!=3:
        print("-s sub_ip sub_port\n-c channel_ip channel_port")
        sys.exit(1)

    if args[1]=="-s": # ChannelSub - [scriptname,ip,port]
        print(f"sub mode {args[2]}:{args[3]}")
        sub = ChannelSub(args[2],int(args[3]),CHANNEL_LIST)
        sub.start()
        while True:
            sub.send_data(input("Input: "))

    elif args[1]=="-c": #Channel - [scriptname,ip,port]
        print("channel mode {args[2]}:{args[3]}")
        channel = Channel(args[2],int(args[3]),SUB_DICT)
        channel.start()

    else: print("-s sub_ip sub_port\n-c channel_ip channel_port")