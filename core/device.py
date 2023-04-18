from nmea_generator import GLL, RMC
from udp import UdpClient
from time import sleep

class Device(UdpClient):
    def __init__(self,name:str,gen_list:list,UDP_IP:str,UDP_PORT:int,endpoint:tuple,time_interval:float=0.2):
        super().__init__(UDP_IP,UDP_PORT,endpoint=endpoint)
        self.name = name
        self.gen_list = gen_list
        self.time_interval = time_interval # time interval between sending data in seconds
        self.loop()

    def handle(self, data, addr):
        received_data = data.decode()
        print(f"{self.UDP_IP}:{self.UDP_PORT} < {addr[0], addr[1]}: {received_data}")

    def loop(self):
        while True:
            for generator in self.gen_list:
                self.send_data(generator.generate())
                sleep(self.time_interval)


if __name__ == "__main__":
    d = Device("DEVICE_1",[GLL("GP"),RMC("GP")],"127.0.0.1",4001,("127.0.0.1",4000))
    d.start()
    d.join()