class Testing():
    def __init__(self, a=5, b):
        self.a = a 
        self.b = b

    def print(self):
        print(f"value = {self.a}, {self.b}")

a = Testing()
b = Testing(6)
a.print()
b.print()