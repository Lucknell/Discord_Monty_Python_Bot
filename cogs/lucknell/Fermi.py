import random
import utils

class Fermi:
    def __init__(self, size=3):
        self.answer = [random.randint(0,9)]
        self.size = size
        size -=1
        while size > 0:
            option = random.randint(0,9)
            if not option in self.answer:
                self.answer.append(option)
                size -=1

    def check_win(self, string):
        result = ""
        bagel = True

        if len(string) < len(self.answer) or not utils.is_int(string):
            return "Bagel"
        for i in range(self.size):
            if string[i] == str(self.answer[i]):
                result +="Fermi "
                bagel = False
            elif int(string[i]) in self.answer:
                result += "Pico "
                bagel = False

        return "Bagel" if bagel else result


    def get_cheats(self):
        answer = ""
        for ans in self.answer:
            answer+= str(ans)
        return answer