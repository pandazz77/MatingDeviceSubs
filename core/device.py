from nmea_generator import GLL, RMC
from simulator import ChannelSub

class Device(ChannelSub):
    def __init__(self,name:str,address:int,gen_list:list,UDP_IP:str,UDP_PORT:int,channel_list:list):
        super().__init__(UDP_IP,UDP_PORT,channel_list)
        self.name = name
        self.address = address
        self.gen_list = gen_list
        self.SYNC_D = "000" # for inf word
        self.SYNC_C = "001" # for com word

    """
    def get_parity(self,x:int):
        x ^= x >> 16
        x ^= x >> 8
        x ^= x >> 4
        x ^= x >> 2
        x ^= x >> 1
        return (x & 1) == 1
    """
    def get_parity(self,data:str):
        return str(data.count("1") % 2)

    def get_com_word(self,addr_rt:int,n_com:int):
        data = format(addr_rt,"05b")+"1"+format(self.address,"05b")+format(n_com,"05b")
        return self.SYNC_C+data+self.get_parity(data)

    def get_res_word(self,addr_rt:int):
        data = format(addr_rt,"05b")+"00000000000"
        return self.SYNC_C+data+self.get_parity(data)

    def get_inf_word(self,data:str): # data in binary format (string)
        if len(data)!=16: raise Exception("Invalid data length")
        return self.SYNC_D+data+self.get_parity(data)

    def get_n_com(self,inf_packet:str): # -> packet size
        return int(len(inf_packet)/20)

    def encode_inf_packet(self,message:str): # message in nmea format (string)
        inf_packet = ""
        for i in range(0,len(message),2):
            data = format(ord(message[i]),"08b")
            if i+1<len(message): data+=format(ord(message[i+1]),"08b")
            else: data+="00000000"
            inf_packet+=self.get_inf_word(data)
        return inf_packet

    def decode_inf_packet(self,packet:str):
        message = ""
        for i in range(0,len(packet),20):
            sync = packet[i:i+3]
            if sync!=self.SYNC_D: raise Exception("Invalid sync signal")
            parity = packet[i+19]
            data = packet[i+3:i+19]
            if self.get_parity(data)!=parity: raise Exception("Invalid parity")
            message+=chr(int(data[:8],2))+chr(int(data[8:],2))

        return message
    
    def get_inf_packet(self):
        inf_packet = ""
        for generator in self.gen_list:
            inf_packet+=self.encode_inf_packet(generator.generate())
        return inf_packet

    # ChannelSub methods
    def handle(self, data, addr):
        received_data = data.decode()
        print(received_data)
        SYNC = received_data[:3]
        if SYNC==self.SYNC_C: # command word
            ADDR_RT = int(received_data[3:8],2)
            WR = int(received_data[8],2)
            SUB_ADDR = int(received_data[9:14],2)
            N_COM = int(received_data[14:19],2)
            if ADDR_RT!=self.address | ADDR_RT!=31 : raise Exception("Invalid address")
            if WR==1: # controller requests data
                self.send_data(self.get_res_word(SUB_ADDR)+self.get_inf_packet())
            else: # controller sending data
                print(self.decode_inf_packet(received_data[20:]))
                self.send_data(self.get_res_word(SUB_ADDR))

        elif SYNC==self.SYNC_D: # information word
            print(self.decode_inf_packet(received_data))

        else:
            raise Exception("Unknown sync signal")


if __name__ == "__main__":
    d = Device("DEVICE_1",1,[GLL("GP"),RMC("GP")],"127.0.0.1",4001,[("127.0.0.1",4000)])
    d.start()
    d.join()