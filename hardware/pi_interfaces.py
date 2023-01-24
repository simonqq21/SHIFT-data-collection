try:
    import board 
    import busio 
except:
    print("error adding interfaces, not running on RPi")

# create i2c interface
try:
    i2c = board.I2C()
except Exception as e:
    print("i2c not initialized, not running on RPi") 
    print(e)

# create onewire interfaces
try:
    onewires = [board.D4, board.D17] 
except Exception as e:
    print("board not initialized, not running on RPi") 
    print(e)