# alphabet_ascii = ' '.join([str(ord(x)) for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"])
# whitespace_ascii = ' '.join([str(ord(x)) for x in "\n\r\t\v\f"])
# numbers_ascii = ' '.join([str(ord(x)) for x in "0123456789"])
# state7_symbol_ascii = ' '.join([str(ord(x)) for x in ";:,[]{}+-*<"])

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
whitespace = "\n\r\t\v\f"
numbers = "0123456789"
state7_symbols = ";:,[]{}+-<"
ligal_characters = alphabet + whitespace + numbers + state7_symbols + "*/="

# see if can have characters like []{} after number. not having error now
# if anything except * comes after / takes / as error. maybe /# comes then what ?

class Compiler:
    symbol_table = {"if": "KEYWORD",
                    "else": "KEYWORD",
                    "void": "KEYWORD",
                    "int": "KEYWORD",
                    "repeat": "KEYWORD",
                    "break": "KEYWORD",
                    "until": "KEYWORD",
                    "return": "KEYWORD"}

    def __init__(self, filepath):
        self.file = open(filepath, "r")
        self.symbol_file = open("symbol_table.txt", "w+")
        self.error_file = open("lexical_errors.txt", "w+")
        self.tokens_file = open("tokens.txt", "w+")
        self.current_line = 1
        self.comment_start_line = -1
        self.last_char = ""

    def next_token(self):
        token = ""
        state = 0
        if not self.file.closed:
            while True:
                # self.last_char = self.file.read(1)
                # if self.last_char == "\n":
                #     self.current_line += 1
                # self.last_char_ascii_string = str(ord(self.last_char))
                if state == 0:
                    self.last_char = self.file.read(1)
                    token = self.last_char
                    if self.last_char == "":
                        return None
                    if self.last_char in whitespace:
                        if self.last_char == "\n":
                            self.new_line()
                        state = 1
                    elif self.last_char.isdigit():
                        state = 2
                    elif self.last_char == "/":
                        state = 3
                    elif self.last_char == "=":
                        state = 4
                    elif self.last_char in state7_symbols:
                        state = 7
                    elif self.last_char.isalpha():
                        state = 11
                    elif self.last_char == "*":
                        state = 16
                    else:
                        # fill for panic
                        pass
                elif state == 1:
                    return "whitespace", token
                elif state == 2:
                    self.last_char = self.file.read(1)
                    if self.last_char.isdigit():
                        token += self.last_char
                    elif self.last_char.isalpha():
                        # fill for panic
                        self.write_error("({}, Invalid number".format(token))
                        return self.next_token()
                    elif self.last_char in ligal_characters:
                        state = 8
                    else:
                        # fill for panic
                        self.write_error("({}, Invalid number".format(token))
                        return self.next_token()
                elif state == 3:
                    self.last_char = self.file.read(1)
                    if self.last_char == "*":
                        token += self.last_char
                        state = 9
                        self.comment_start_line = self.current_line
                    elif self.last_char == "/":
                        token += self.last_char
                        state = 10
                    else:
                        # fill for error
                        if self.last_char != "":
                            self.file.seek(self.file.tell() - 1)
                        self.write_error("({}, Invalid input".format(token))
                        return self.next_token()
                elif state == 4:
                    self.last_char = self.file.read(1)
                    if self.last_char == "=":
                        token += self.last_char
                        state = 6
                    elif self.last_char in ligal_characters:
                        state = 5
                    else:
                        # fill for panic
                        self.errors.append((self.current_line, ("/", "Invalid input")))
                        return self.next_token()
                elif state == 5:
                    if self.last_char != "":
                        self.file.seek(self.file.tell() - 1)
                    self.write_token(("SYMBOL", "="))
                    return "SYMBOL", "="
                elif state == 6:
                    return "SYMBOL", "=="
                elif state == 7:
                    return "SYMBOL", token
                elif state == 8:
                    if self.last_char != "":
                        self.file.seek(self.file.tell() - 1)
                    if self.last_char == "\n":
                        self.new_line()
                    return ("NUM", token)
                elif state == 9:
                    self.last_char = self.file.read(1)
                    token += self.last_char
                    if self.last_char == "\n":
                        self.current_line += 1
                    elif self.last_char == "*":
                        state = 12
                    elif self.last_char == "":
                        # fill with error
                        self.errors.append((self.comment_start_line, (token, "Unclosed comment")))
                        return None
                elif state == 10:
                    self.last_char = self.file.read(1)
                    if self.last_char == "\n":
                        self.current_line += 1
                        state = 14
                    elif self.last_char == "":
                        state = 14
                    else:
                        token += self.last_char
                elif state == 11:
                    self.last_char = self.file.read(1)
                    if self.last_char.isalnum():
                        token += self.last_char
                    elif self.last_char in ligal_characters:
                        if self.last_char == "\n":
                            self.current_line += 1
                        state = 13
                    else:
                        # fill with panic
                        self.errors.append((self.current_line, (token, "Invalid input")))
                        return self.next_token()
                elif state == 12:
                    self.last_char = self.file.read(1)
                    token += self.last_char
                    if self.last_char == "\n":
                        self.current_line += 1
                        state = 9
                    elif self.last_char == "/":
                        state = 15
                    elif self.last_char == "":
                        # fill with error
                        pass
                    elif self.last_char != "*":
                        state = 9
                elif state == 13:
                    if token in self.symbol_table:
                        token_type = self.symbol_table[token]
                        return token_type, token
                    self.symbol_table[token] = "ID"
                    return "ID", token
                elif state == 14:
                    if self.last_char == "":
                        return "COMMENT", token
                    # last_char is \n
                    self.file.seek(self.file.tell()-1)
                    return "COMMENT", token
                elif state == 15:
                    return "COMMENT", token
                elif state == 16:
                    self.last_char = self.file.read(1)
                    if self.last_char == "/":
                        # fill with error
                        pass
                    elif self.last_char in ligal_characters:
                        state = 17
                    else:
                        # fill with panic
                        pass
                elif state == 17:
                    if self.last_char != "":
                        self.file.seek(self.file.tell() - 1)
                    return "SYMBOL", "*"
        else:
            return None

    # def write_token(self, token):

    def new_line(self):
        self.current_line += 1
        if self.tokens_file.tell() != 0:
            self.tokens_file.seek(self.tokens_file.tell() - 1)
            last_char = self.tokens_file.read(1)
            if last_char != "\n":
                self.tokens_file.write("\n")
        if self.symbol_file.tell() != 0:
            self.symbol_file.seek(self.symbol_file.tell() - 1)
            last_char = self.symbol_file.read(1)
            if last_char != "\n":
                self.symbol_file.write("\n")
        if self.error_file.tell() != 0:
            self.error_file.seek(self.error_file.tell() - 1)
            last_char = self.error_file.read(1)
            if last_char != "\n":
                self.error_file.write("\n")

    def write_error(self, error):
        last_char = "\n"
        if self.symbol_file.tell() != 0:
            self.symbol_file.seek(self.symbol_file.tell() - 1)
            last_char = self.symbol_file.read(1)
        if last_char == "\n":
            self.symbol_file.write("{}.\t".format(self.current_line) + error + " ")
        else:
            self.symbol_file.write(error + " ")


# f = open("../HW1/Practical/PA1_testcases1.2/T01/input.txt", "r")

# for i in range(300):
#     a = f.read(1)
#     if a == "":
#         break
#     print(a)
#     # print(ord(a))
# f.seek(f.tell() - 1)
# a = f.read(1)
# print(a)


symbol_file = open("../symbol.txt", 'w+')

symbol_file.seek(symbol_file.tell() - 1)
print(symbol_file.read(1))
# symbol_file.write("hello")
# symbol_file.write("come sa yamas")
# symbol_file.write("\n\tzahre mar")
#
# if symbol_file.closed:
#     print("yes")
