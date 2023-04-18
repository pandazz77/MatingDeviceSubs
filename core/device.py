from nmea_generator import GLL, RMC, ZDA, VTG
from threading import Thread
from udp import UdpClient
from time import sleep

class Device(UdpClient,Thread):
    def __init__(self,name:str,gen_list:list,UDP_IP:str,UDP_PORT:int,endpoint:tuple,time_interval:float=0.2):
        super().__init__(UDP_IP,UDP_PORT,endpoint=endpoint)
        self.name = name
        self.gen_list = gen_list
        self.time_interval = time_interval # time interval between sending data in seconds
        Thread().__init__()

    def handle(self, data, addr):
        received_data = data.decode()
        print(f"{self.UDP_IP}:{self.UDP_PORT} < {addr[0], addr[1]}: {received_data}")

    def run(self):
        while True:
            for generator in self.gen_list:
                self.send_data(generator.generate())
                sleep(self.time_interval)


if __name__ == "__main__":
    d1 = Device(name="DEVICE_1",gen_list=[GLL("GP"),RMC("GP")],UDP_IP="127.0.0.1",UDP_PORT=4001,endpoint=("127.0.0.1",5001))
    d2 = Device(name="DEVICE_2",gen_list=[ZDA("GN")],UDP_IP="127.0.0.1",UDP_PORT=4002,endpoint=("127.0.0.1",5001))
    d3 = Device(name="DEVICE_3",gen_list=[VTG("GP")],UDP_IP="127.0.0.1",UDP_PORT=4003,endpoint=("127.0.0.1",5001))
    d1.start()
    d2.start()
    d3.start()