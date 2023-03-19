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
from system import * 

class GUI(Tk):
    def __init__(self):
        '''
        for growLightButton and cameraLightButton, 0 is for OFF, 1 is for ON, and 2 is for AUTO.
        for the rest of the buttons 0 is for inactive and 1 is for activated.
        '''
        super().__init__();

        # system init 
        self.system = System() 
        self.system.start() 

        self.cameraButtonState = 0
        self.sensorButtonState = 0 
        self.growLightButtonState = 0 
        self.cameraLightButtonState = 0
        self.pump1ButtonState = 0
        self.pump2ButtonState = 0
        self.pump3ButtonState = 0
        self.title('Plant Growth Monitoring System Remote Control')
        self.geometry('720x480')  
        
        self.rowconfigure(0, weight=1) 
        self.rowconfigure(1, weight=1) # sensors
        self.rowconfigure(2, weight=1) # lights
        self.rowconfigure(3, weight=1) # pumps

        lbl1 = Label(self, \
            text="Welcome to the GUI of the Plant Growth Monitoring System.", \
            font=("fangsong ti", 16), \
            anchor=W, \
                justify=LEFT)
        lbl1.grid(column=0, row=0, sticky='nsew', columnspan=3)
        cameraButton = Button(self, text="Capture Image", command=self.captureImage)
        cameraButton.grid(row=1, column=0, columnspan=1, sticky='nsew')
        sensorButton = Button(self, text="Capture Sensors", command=self.captureSensors)
        sensorButton.grid(row=1, column=1, sticky='nsew')
        growLightButton = Button(self, text="Status: OFF", command=self.toggleGrowLights) 
        growLightButton.grid(row=2, column=0, sticky='nsew')
        whiteLightButton = Button(self, text="Click me", command=self.toggleCameraLights)
        whiteLightButton.grid(row=2, column=1, sticky='nsew')
        pump1Button = Button(self, text="Activate Pump 1 for {} seconds".format(5), command=self.activatePump) 
        pump1Button.grid(row=3, column=0, sticky='nsew')
        pump2Button = Button(self, text="Activate Pump 2 for {} seconds".format(5), command=self.activatePump) 
        pump2Button.grid(row=3, column=1, sticky='nsew')
        pump3Button = Button(self, text="Activate Pump 3 for {} seconds".format(5), command=self.activatePump) 
        pump3Button.grid(row=3, column=2, sticky='nsew')

        self.after(300, self.systemLoop)

    def toggleGrowLights(self, func):
        pass
        # self.growLightButtonState += 1
        # if self.growLightButtonState == 3:
        #     self.growLightButtonState = 0

        # if (self.growLightButtonState == 0):
            
        # elif (self.growLightButtonState == 1):

        # elif (self.growLightButtonState == 2):

    def toggleCameraLights():
        pass 

    def captureImage():
        pass 

    def captureSensors():
        pass 

    def activatePump():
        pass 

    def systemLoop(self):
        self.system.loop()
        self.update_idletasks() 
        self.update()
        self.after(50, self.systemLoop) 

pump_duration = 5 







if __name__ == "__main__":
    pass 

# def change_text():
#     if button["text"] == "Click me":
#         button["text"] = "Clicked!"
#     else:
#         button["text"] = "Click me"

# button = Button(self, text="Click me", command=change_text)
# button.pack()


