from core.nmea_generator import RMC, GLL, ZDA, VTG
from core.device import Device
from time import sleep
import sys

def parse_generators(generators:str) -> list:
    #GPGLL,GPRMC - example input
    result = []
    if ',' in generators:
        generators_list = generators.split(",")
    else:
        generators_list = [generators]
    for gen in generators_list:
        gen_name = gen[0:2]
        gen_type = gen[2:]
        if gen_type == "RMC":
            generator = RMC(gen_name)
        elif gen_type == "GLL":
            generator = GLL(gen_name)
        elif gen_type == "ZDA":
            generator = ZDA(gen_name)
        elif gen_type == "VTG":
            generator = VTG(gen_name)
        else:
            raise Exception(f"Invalid generator type: {gen_type}")
        result.append(generator)
    return result

def parse_args(args:list):
    for i in range(len(args)):
        if args[i] == "-g":
            DEVICE_NAME = args[i+1]
            GENERATORS = parse_generators(args[i+2])
            CLIENT_IP, CLIENT_PORT = args[i+3].split(":")
            ENDPOINT_IP, ENDPOINT_PORT = args[i+4].split(":")
            d =  Device(DEVICE_NAME,GENERATORS,CLIENT_IP,int(CLIENT_PORT),(ENDPOINT_IP,int(ENDPOINT_PORT)))
            d.daemon = True
            d.start()
    while True: sleep(1)


if __name__ == "__main__":
    # -g DEVICE_NAME GPGLL,GPRMC CLIENT_IP:CLIENT_PORT ENDPOINT_IP:ENDPOINT_PORT - example args
    args = sys.argv
    parse_args(args)