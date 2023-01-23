try:
    import board 
    import busio 
except:
    print("error adding interfaces, not running on RPi")

# create i2c interface
try:
    i2c = board.I2C()
except:
    print("i2c not initialized, not running on RPi") 

# create onewire interfaces
try:
    onewires = [board.D4, board.D17] 
except:
    print("board not initialized, not running on RPi") 