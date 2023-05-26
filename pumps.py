try:
    import socket
    import json
    import os
    import threading
    from datetime import date, datetime, time, timedelta
    from time import sleep
    from hardware.irrigation_pumps import SyncedPumps
    import socket
except Exception as e:
    print(e)
from config import Config