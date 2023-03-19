'''
MQTT data packet format
{
    'datetime': (datetime object parsed into string),
    'expt_num': (integer),
    'sitename': (string),
    'type': (string eg. "temperature", "humidity", "light_intensity", "soil_moisture",  
            solution_pH", "solution_EC", "camera"),
    'index': (integer),
    'value': (float),
}
'''
from system import *
from config import *
from gui import * 

# system init 
system = System()
# gui init
gui = GUI()
print("aaaaaa")
system.start() 
gui.after(50, system.loop)
if __name__ == "__main__":
    gui.mainloop()
    
    