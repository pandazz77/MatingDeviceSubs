from nmea_generator import GLL, RMC

class Device:
    def __init__(self,name:str,address:int,gen_list:list):
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
        data = format(addr_rt,"05b")+"000000000"
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
    
    def get_packet(self):
        inf_packet = ""
        for generator in self.gen_list:
            inf_packet+=self.encode_inf_packet(generator.generate())
        #n_com = self.get_n_com(inf_packet)
        packet=inf_packet#self.get_com_word(5,n_com)+self.get_res_word(5)+inf_packet+self.get_com_word(5,n_com)
        return packet
    
if __name__ == "__main__":
    d = Device("DEVICE_1",1,[GLL("GP"),RMC("GP")])
    #print(d.gen_binary("hello"))
    #print(d.get_parity(0b1101000))
    #print(len(d.get_inf_word("1000000110000001")))
    #packet = d.encode_inf_packet(d.gen_list[0].generate())
    #print(packet)
    #print(d.decode_inf_packet(packet))
    #print(d.get_com_word(3,5))
    packet = d.get_packet()
    print(packet)
    print(len(packet))
    print(d.decode_inf_packet(packet))