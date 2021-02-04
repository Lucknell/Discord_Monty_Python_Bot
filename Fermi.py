import random

class Fermi:
    def __init__(self):
        self.first = random.randint(0,9)
        self.second = random.randint(0,9)
        while self.second == self.first:
            self.second = random.randint(0,9)
        self.third = random.randint(0,9)
        while self.third == self.second or self.third == self.first:
            self.third = random.randint(0,9)


    def check_win(self, string):
        result = ""
        bagel = True

        if string[0] == str(self.first):
            result +="Fermi "
            bagel = False
        elif string[0] == str(self.second) or string[0] == str(self.third):
            result += "Pico "
            bagel = False
        
        if string[1] == str(self.second):
            result +="Fermi "
            bagel = False
        elif string[1] == str(self.first) or string[1] == str(self.third):
            result += "Pico "
            bagel = False
        
        if string[2] == str(self.third):
            result +="Fermi"
            bagel = False
        elif string[2] == str(self.second) or string[2] == str(self.first):
            result += "Pico"
            bagel = False
        
        return "Bagel" if bagel else result


    def get_cheats(self):
        return "{}{}{}".format(self.first, self.second, self.third)