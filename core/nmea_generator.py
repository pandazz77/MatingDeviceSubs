import random
import time

class Generator:
    def __init__(self,name:str,null_message:list):
        self.message = null_message#["5300.97914","N","00259.98174","E","125926","A"]
        self.name = name # GPGLL as example
        self.message.insert(0,self.name)
        self.gen_funcs = [()]

    def get_checksum(self):
        checksum = 0
        for char in ",".join(self.message):
            checksum = checksum ^ ord(char)
        return hex(checksum).upper()[2:] # [2:] to remove "0x"

    def exec_func(self,task:tuple):
        if not callable(task[0]): raise Exception("Invalid generator function")
        if task[1]!=None: task[0](task[1])
        else: task[0]()

    def generate(self):
        for func in self.gen_funcs:
            self.exec_func(func)
        return self.get_message()

    def get_message(self):
        return "$"+",".join(self.message)+"*"+self.get_checksum()

    # Default GenMethods
    def gen_latitude(self,index):
        new_lat = (float(self.message[index]) + random.uniform(-2,2))
        if new_lat>9000 or new_lat<0: return self.gen_latitude(index)
        self.message[index] = "%07.2f" % new_lat

    def gen_latitude_dir(self,index):
        pass

    def gen_longitude(self,index):
        new_long = (float(self.message[index]) + random.uniform(-2,2))
        if new_long>180000 or new_long<0: return self.gen_longitude(index)
        self.message[index] = "%08.2f" % new_long

    def gen_longitude_dir(self,index):
        pass

    def gen_current_time(self,index):
        self.message[index]=time.strftime("%H%M%S.000",time.gmtime())
    
    def gen_date(self,index):
        self.message[index]=time.strftime("%d%m%y",time.gmtime())

    def gen_speed(self,index):
        new_speed = (float(self.message[index]) + random.uniform(-1,1))
        if new_speed>20 or new_speed<0: return self.gen_speed(index)
        self.message[index] = "%04.2f" % new_speed

    def gen_heading(self,index):
        new_heading = (float(self.message[index]) + random.uniform(-1,1))
        if new_heading>359 or new_heading<0: return self.gen_heading()
        self.message[index] = "%04.2f" % new_heading
    

class GLL(Generator): #[name,latitude,N/S,longitude,E/W,time,A/V,A/D/E/M/N]
    def __init__(self,name:str,null_message=None):
        self.name = name+"GLL"
        if not null_message: null_message = ["0000.00","N","00000.00","E","00000.000","A","A"]
        super().__init__(self.name,null_message)
        self.gen_funcs = [(self.gen_latitude,1),(self.gen_longitude,3),(self.gen_current_time,5)]

class ZDA(Generator): #[name,UTCtime,day,month,year,UTC dif hours, UTC dif minutes]
    def __init__(self,name:str,null_message=None):
        self.name = name+"ZDA"
        if not null_message: null_message = ["000000.000","00","00","0000","00","00"]
        super().__init__(self.name,null_message)
        self.gen_funcs = [(self.gen_current_time,1),(self.gen_day,None),(self.gen_month,None),(self.gen_year,None)]

    def gen_day(self):
        self.message[2] = time.strftime("%d",time.gmtime())

    def gen_month(self):
        self.message[3] = time.strftime("%m",time.gmtime())

    def gen_year(self):
        self.message[4] = time.strftime("%Y",time.gmtime())

class VTG(Generator): #[name,Nheading,T/F,,M,speed,speed unit,speed2,speed unit2,A/D/E/M/N]
    def __init__(self,name:str,null_message=None):
        self.name = name+"VTG"
        if not null_message: null_message = ["076.2","T","","M","0.00","N","0.00","K","A"]
        super().__init__(self.name,null_message)
        self.gen_funcs = [(self.gen_heading,1),(self.gen_speed,5)]

    def gen_speed(self,index):
        super().gen_speed(index)
        knot_speed = float(self.message[index])
        kmh_speed = knot_speed*1.852
        self.message[5] = "%04.2f" % knot_speed
        self.message[7] = "%04.2f" % kmh_speed


    
class RMC(Generator): #[name,UTCtime,A/V,latitude,N/S,longitude,E/W,speed,heading,date,MagneticV,E/W]
    def __init__(self,name:str,null_message=None):
        self.name = name+"RMC"
        if not null_message: null_message = ["210230","A","3855.4487","N","09446.0071","W","0.0","076.2","130495","003.8","E"]
        super().__init__(self.name,null_message)
        self.gen_funcs = [(self.gen_current_time,1),(self.gen_latitude,3),(self.gen_longitude,5),(self.gen_position_status,None),(self.gen_speed,7),(self.gen_heading,8),(self.gen_date,9)]

    def gen_position_status(self):
        chance = 0.05
        if random.random()<chance: self.message[2]="V"
        else: self.message[2]="A"

    def get_magnetic(self):
        pass

    def get_magnetic_dir(self):
        pass


# test
if __name__ == "__main__":
    g = GLL("GP")
    g1 = RMC("GP")
    g2 = ZDA("GN")
    g3 = VTG("GP")
    print(g3.generate())