# 10: line feed, 32: space


class Compiler:
    symbol_table = {"if":"KEYWORD",
                    "else": "KEYWORD",
                    "void": "KEYWORD",
                    "int": "KEYWORD",
                    "repeat": "KEYWORD",
                    "break": "KEYWORD",
                    "until": "KEYWORD",
                    "return": "KEYWORD"}

    def __init__(self, filepath):
        self.file = open(filepath, "r")
        pass

    def next_token(self):

        pass


# f = open("../HW1/Practical/PA1_testcases1.2/T01/input.txt", "r")
# for i in range(21):
#     a = f.read(1)
#     print(a)
#     print(ord(a))

