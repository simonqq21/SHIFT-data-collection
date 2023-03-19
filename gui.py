
'''
grow lights manual on, off, auto button
image capture button
pump1 water button (5s) 
pump2 water button (5s)
pump3 water button (5s)
sensor capture button
'''

import tkinter.messagebox
from tkinter import *
from tkinter import font

class GUI():
    def __init__(self):
        win = Tk()
        win.title('Plant Growth Monitoring System Remote Control')
        win.geometry('720x480')  
        
        win.rowconfigure(0, weight=1) 
        win.rowconfigure(1, weight=1) # sensors
        win.rowconfigure(2, weight=1) # lights
        win.rowconfigure(3, weight=1) # pumps

        lbl1 = Label(win, \
            text="Welcome to the GUI of the Plant Growth Monitoring System.", \
            font=("fangsong ti", 16), \
            anchor=W, \
                justify=LEFT)
        lbl1.grid(column=0, row=0, sticky='nsew', columnspan=3)
        cameraButton = Button(win, text="Capture Image", command=captureImage)
        cameraButton.grid(row=1, column=0, columnspan=1, sticky='nsew')
        sensorButton = Button(win, text="Capture Sensors", command=captureSensors)
        sensorButton.grid(row=1, column=1, sticky='nsew')
        growLightButton = Button(win, text="Status: OFF", command=toggleGrowLights) 
        growLightButton.grid(row=2, column=0, sticky='nsew')
        whiteLightButton = Button(win, text="Click me", command=toggleCameraLights)
        whiteLightButton.grid(row=2, column=1, sticky='nsew')
        pump1Button = Button(win, text="Activate Pump 1 for {} seconds".format(5), command=activatePump) 
        pump1Button.grid(row=3, column=0, sticky='nsew')
        pump2Button = Button(win, text="Activate Pump 2 for {} seconds".format(5), command=activatePump) 
        pump2Button.grid(row=3, column=1, sticky='nsew')
        pump3Button = Button(win, text="Activate Pump 3 for {} seconds".format(5), command=activatePump) 
        pump3Button.grid(row=3, column=2, sticky='nsew')
        win.mainloop()

    
pump_duration = 5 

def toggleGrowLights():
    pass 

def toggleCameraLights():
    pass 

def captureImage():
    pass 

def captureSensors():
    pass 

def activatePump():
    pass 



if __name__ == "__main__":
    pass 

# def change_text():
#     if button["text"] == "Click me":
#         button["text"] = "Clicked!"
#     else:
#         button["text"] = "Click me"

# button = Button(win, text="Click me", command=change_text)
# button.pack()


