from system import *
from config import *
from gui import * 

# gui init
gui = GUI()
gui.after(500, gui.systemLoop)
if __name__ == "__main__":
    gui.mainloop()
    
    