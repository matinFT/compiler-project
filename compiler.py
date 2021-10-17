# alphabet_ascii = ' '.join([str(ord(x)) for x in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"])
# whitespace_ascii = ' '.join([str(ord(x)) for x in "\n\r\t\v\f"])
# numbers_ascii = ' '.join([str(ord(x)) for x in "0123456789"])
# state7_symbol_ascii = ' '.join([str(ord(x)) for x in ";:,[]{}+-*<"])

alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
whitespace = "\n\r\t\v\f "
numbers = "0123456789"
state7_symbols = ";:,[]{}+-<()"
legal_characters = alphabet + whitespace + numbers + state7_symbols + "*/="


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
        #
        self.file = open(filepath, "r")
        self.symbol_file = open("symbol_table.txt", "w+")
        self.error_file = open("lexical_errors.txt", "w+")
        self.tokens_file = open("tokens.txt", "w+")
        self.current_line = 1
        self.comment_start_line = -1
        self.last_char = ""
        self.last_pos = 0
        self.write_symbols()

    def next_token(self):
        token = ""
        state = 0
        if not self.file.closed:
            while True:
                if state == 0:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    # print(self.last_char)
                    # print("state 0: ", self.last_char)
                    token = self.last_char
                    if self.last_char == "":
                        # self.new_line()
                        self.file.close()
                        self.symbol_file.close()
                        self.tokens_file.close()
                        if self.error_file.tell() == 0:
                            self.error_file.write("There is no lexical error.")
                        self.error_file.close()
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
                        self.write_error("({}, Invalid input)".format(token))
                        return self.next_token()
                elif state == 1:
                    return "whitespace", token
                elif state == 2:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    if self.last_char.isdigit():
                        token += self.last_char
                    elif self.last_char.isalpha() or self.last_char not in legal_characters:
                        # fill for panic
                        self.write_error("({}, Invalid number)".format(token + self.last_char))
                        return self.next_token()
                    # not alpha or digit but in legal characters
                    else:
                        state = 8
                elif state == 3:
                    self.last_pos = self.file.tell()
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
                            self.file.seek(self.last_pos)
                        self.write_error("({}, Invalid input)".format(token))
                        return self.next_token()
                elif state == 4:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    if self.last_char == "=":
                        token += self.last_char
                        state = 6
                    elif self.last_char in legal_characters:
                        state = 5
                    else:
                        # fill for panic
                        self.write_error("({}, Invalid input)".format(token + self.last_char))
                        return self.next_token()
                elif state == 5:
                    if self.last_char != "":
                        self.file.seek(self.last_pos)
                    self.write_token("(SYMBOL, =)")
                    return "SYMBOL", "="
                elif state == 6:
                    self.write_token("(SYMBOL, ==)")
                    return "SYMBOL", "=="
                elif state == 7:
                    self.write_token("(SYMBOL, {})".format(token))
                    return "SYMBOL", token
                elif state == 8:
                    if self.last_char != "":
                        self.file.seek(self.last_pos)
                    self.write_token("(NUM, {})".format(token))
                    return "NUM", token
                elif state == 9:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    token += self.last_char
                    if self.last_char == "\n":
                        self.current_line += 1
                    elif self.last_char == "*":
                        state = 12
                    elif self.last_char == "":
                        # fill with error
                        if len(token) > 7:
                            error_string = token[:7] + "..."
                        else:
                            error_string = token
                        self.write_error("({}, Unclosed comment)".format(error_string), True)
                        # self.new_line()
                        return None
                elif state == 10:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    if self.last_char == "\n":
                        state = 14
                    elif self.last_char == "":
                        state = 14
                    else:
                        token += self.last_char
                elif state == 11:
                    # print("state 11 ", self.file.tell())
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    # print(self.last_char)
                    if self.last_char.isalnum():
                        token += self.last_char
                    elif self.last_char in legal_characters:
                        state = 13
                    else:
                        # fill with panic
                        self.write_error("({}, Invalid input)".format(token + self.last_char))
                        return self.next_token()
                elif state == 12:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    token += self.last_char
                    if self.last_char == "\n":
                        self.current_line += 1
                        state = 9
                    elif self.last_char == "/":
                        state = 15
                    elif self.last_char == "":
                        self.write_error("({}, Unclosed comment)".format(token), True)
                        # self.new_line()
                        return None
                    elif self.last_char != "*":
                        state = 9
                elif state == 13:
                    # print("state 13: ", self.last_char)
                    # print("state ", self.file.tell())
                    if self.last_char != "":
                        self.file.seek(self.last_pos)
                    # print("state ", self.file.tell())
                    token_type = self.get_token(token)
                    self.write_token("({}, {})".format(token_type, token))
                    return token_type, token
                elif state == 14:
                    if self.last_char != "":
                        self.file.seek(self.last_pos)
                    # last_char is \n
                    # self.write_token("(COMMENT, {})".format(token))
                    return "COMMENT", token
                elif state == 15:
                    # self.write_token("(COMMENT, {})".format(token))
                    return "COMMENT", token
                elif state == 16:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    if self.last_char == "/":
                        # fill with error
                        self.write_error("({}, Unmatched comment)".format(token + self.last_char))
                        return self.next_token()
                    elif self.last_char in legal_characters:
                        state = 17
                    else:
                        # fill with panic
                        self.write_error("({}, Invalid input)".format(token + self.last_char))
                        return self.next_token()
                elif state == 17:
                    if self.last_char != "":
                        self.file.seek(self.last_pos)
                    self.write_token("(SYMBOL, *)")
                    return "SYMBOL", "*"
        else:
            return None

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

    def write_error(self, error, unclosed_comment=False):
        error_line = self.current_line if not unclosed_comment else self.comment_start_line
        last_char = "\n"
        if self.error_file.tell() != 0:
            self.error_file.seek(self.error_file.tell() - 1)
            last_char = self.error_file.read(1)
        if last_char == "\n":
            self.error_file.write("{}.\t".format(error_line) + error + " ")
        else:
            self.error_file.write(error + " ")

    def write_token(self, token):
        last_char = "\n"
        if self.tokens_file.tell() != 0:
            self.tokens_file.seek(self.tokens_file.tell() - 1)
            last_char = self.tokens_file.read(1)
        if last_char == "\n":
            self.tokens_file.write("{}.\t".format(self.current_line) + token + " ")
        else:
            self.tokens_file.write(token + " ")

    def get_token(self, token):
        if token in self.symbol_table:
            return self.symbol_table[token]
        else:
            self.symbol_table[token] = "ID"
            self.symbol_file.write("{}.\t{}\n".format(len(self.symbol_table), token))
            return "ID"

    def write_symbols(self):
        symbol_num = 1
        for symbol in self.symbol_table:
            self.symbol_file.write("{}.\t{}\n".format(symbol_num, symbol))
            symbol_num += 1


# a = Compiler("../HW1/Practical/tests/tests/PA1_input_output_samples/T02/input.txt")
a = Compiler("input.txt")
while True:
    t = a.next_token()
    if t is None:
        break
#     print(t)

