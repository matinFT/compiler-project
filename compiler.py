from anytree import Node, RenderTree
class Scanner:
    symbol_table = {"if": "KEYWORD",
                    "else": "KEYWORD",
                    "void": "KEYWORD",
                    "int": "KEYWORD",
                    "repeat": "KEYWORD",
                    "break": "KEYWORD",
                    "until": "KEYWORD",
                    "return": "KEYWORD",
                    "endif": "KEYWORD"}
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    whitespace = "\n\r\t\v\f "
    numbers = "0123456789"
    state7_symbols = ";:,[]{}+-<()"
    legal_characters = alphabet + whitespace + numbers + state7_symbols + "*/="

    def __init__(self, filepath):
        # setting files
        self.file = open(filepath, "r")
        self.symbol_file = open("symbol_table.txt", "w+")
        self.error_file = open("lexical_errors.txt", "w+")
        self.tokens_file = open("tokens.txt", "w+")
        self.current_line = 1
        self.comment_start_line = -1
        self.last_char = ""
        self.last_pos = 0
        self.write_symbols()

    # returns next valid token. returns $ if reaches EOF
    def next_token(self):
        token = ""
        state = 0
        if not self.file.closed:
            while True:
                # deciding what to do in every state based on input character
                if state == 0:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    token = self.last_char
                    if self.last_char == "":
                        # self.new_line()
                        self.file.close()
                        self.symbol_file.close()
                        self.tokens_file.close()
                        if self.error_file.tell() == 0:
                            self.error_file.write("There is no lexical error.")
                        self.error_file.close()
                        return "$"
                    if self.last_char in self.whitespace:
                        if self.last_char == "\n":
                            self.new_line()
                        state = 1
                    elif self.last_char.isdigit():
                        state = 2
                    elif self.last_char == "/":
                        state = 3
                    elif self.last_char == "=":
                        state = 4
                    elif self.last_char in self.state7_symbols:
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
                    return self.next_token()
                    # return "whitespace", token
                elif state == 2:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    if self.last_char.isdigit():
                        token += self.last_char
                    elif self.last_char.isalpha() or self.last_char not in self.legal_characters:
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
                        if self.last_char in self.legal_characters:
                            if self.last_char != "":
                                self.file.seek(self.last_pos)
                            self.write_error("({}, Invalid input)".format(token))
                        else:
                            self.write_error("({}, Invalid input)".format(token + self.last_char))
                        # if self.last_char != "":
                        #     self.file.seek(self.last_pos)
                        # self.write_error("({}, Invalid input)".format(token))
                        return self.next_token()
                elif state == 4:
                    self.last_pos = self.file.tell()
                    self.last_char = self.file.read(1)
                    if self.last_char == "=":
                        token += self.last_char
                        state = 6
                    elif self.last_char in self.legal_characters:
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
                        return "$"
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
                    elif self.last_char in self.legal_characters:
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
                        return "$"
                    elif self.last_char != "*":
                        state = 9
                elif state == 13:
                    if self.last_char != "":
                        self.file.seek(self.last_pos)
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
                    elif self.last_char in self.legal_characters:
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
            return "$"

    # manages new line in files and self.current_line for one \n
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

    # writes error to error file. manages line numbers in error file too
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

    # writes token to tokens file. manages line numbers in error file too
    def write_token(self, token):
        last_char = "\n"
        if self.tokens_file.tell() != 0:
            self.tokens_file.seek(self.tokens_file.tell() - 1)
            last_char = self.tokens_file.read(1)
        if last_char == "\n":
            self.tokens_file.write("{}.\t".format(self.current_line) + token + " ")
        else:
            self.tokens_file.write(token + " ")

    # returns token's type. puts token in symbol table at first appearance
    def get_token(self, token):
        if token in self.symbol_table:
            return self.symbol_table[token]
        else:
            self.symbol_table[token] = "ID"
            self.symbol_file.write("{}.\t{}\n".format(len(self.symbol_table), token))
            return "ID"

    # writes the KEYWORDS to symbol file
    def write_symbols(self):
        symbol_num = 1
        for symbol in self.symbol_table:
            self.symbol_file.write("{}.\t{}\n".format(symbol_num, symbol))
            symbol_num += 1


class Parser:
    # a dictionary with grammar symbols as it's keys. every key is mapped to another dictionary
    # containing first_set, follow_set, is_terminal attribute of that symbol
    symbols = {'Program': {'first_set': ['$', 'int', 'void'], 'follow_set': [], 'is_terminal': False, 'start_state': 0},
               'Declaration-list': {'first_set': ['int', 'void'],
                                    'follow_set': ['$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM',
                                                   '}'], 'is_terminal': False, 'start_state': 3},
               'Declaration': {'first_set': ['int', 'void'],
                               'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID',
                                              '(', 'NUM', '}'], 'is_terminal': False, 'start_state': 6},
               'Declaration-initial': {'first_set': ['int', 'void'], 'follow_set': ['(', ';', '[', ',', ')'],
                                       'is_terminal': False, 'start_state': 9},
               'Declaration-prime': {'first_set': ['(', ';', '['],
                                     'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return',
                                                    'ID', '(', 'NUM', '}'], 'is_terminal': False, 'start_state': 12},
               'Var-declaration-prime': {'first_set': [';', '['],
                                         'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return',
                                                        'ID', '(', 'NUM', '}'], 'is_terminal': False,
                                         'start_state': 14}, 'Fun-declaration-prime': {'first_set': ['('],
                                                                                       'follow_set': ['int', 'void',
                                                                                                      '$', '{', 'break',
                                                                                                      ';', 'if',
                                                                                                      'repeat',
                                                                                                      'return', 'ID',
                                                                                                      '(', 'NUM', '}'],
                                                                                       'is_terminal': False,
                                                                                       'start_state': 19},
               'Type-specifier': {'first_set': ['int', 'void'], 'follow_set': ['ID'], 'is_terminal': False,
                                  'start_state': 24},
               'Params': {'first_set': ['int', 'void'], 'follow_set': [')'], 'is_terminal': False, 'start_state': 26},
               'Param-list': {'first_set': [','], 'follow_set': [')'], 'is_terminal': False, 'start_state': 31},
               'Param': {'first_set': ['int', 'void'], 'follow_set': [',', ')'], 'is_terminal': False,
                         'start_state': 35},
               'Param-prime': {'first_set': ['['], 'follow_set': [',', ')'], 'is_terminal': False, 'start_state': 38},
               'Compound-stmt': {'first_set': ['{'],
                                 'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID',
                                                '(', 'NUM', '}', 'endif', 'else', 'until'], 'is_terminal': False,
                                 'start_state': 41},
               'Statement-list': {'first_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
                                  'follow_set': ['}'], 'is_terminal': False, 'start_state': 46},
               'Statement': {'first_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
                             'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif',
                                            'else', 'until'], 'is_terminal': False, 'start_state': 49},
               'Expression-stmt': {'first_set': ['break', ';', 'ID', '(', 'NUM'],
                                   'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                                  'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 51},
               'Selection-stmt': {'first_set': ['if'],
                                  'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                                 'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 54},
               'Else-stmt': {'first_set': ['endif', 'else'],
                             'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif',
                                            'else', 'until'], 'is_terminal': False, 'start_state': 61},
               'Iteration-stmt': {'first_set': ['repeat'],
                                  'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                                 'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 65},
               'Return-stmt': {'first_set': ['return'],
                               'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                              'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 72},
               'Return-stmt-prime': {'first_set': [';', 'ID', '(', 'NUM'],
                                     'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                                    'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 75},
               'Expression': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [';', ')', '|', ']', ','],
                              'is_terminal': False, 'start_state': 78},
               'B': {'first_set': ['=', '(', '[', '*', '+', '-', '<', '=='], 'follow_set': [';', ')', '|', ']', ','],
                     'is_terminal': False, 'start_state': 81},
               'H': {'first_set': ['=', '*', '+', '-', '<', '=='], 'follow_set': [';', ')', '|', ']', ','],
                     'is_terminal': False, 'start_state': 86},
               'Simple-expression-zegond': {'first_set': ['(', 'NUM'], 'follow_set': [';', ')', '|', ']', ','],
                                            'is_terminal': False, 'start_state': 90},
               'Simple-expression-prime': {'first_set': ['(', '*', '+', '-', '<', '=='],
                                           'follow_set': [';', ')', '|', ']', ','], 'is_terminal': False,
                                           'start_state': 93},
               'C': {'first_set': ['<', '=='], 'follow_set': [';', ')', '|', ']', ','], 'is_terminal': False,
                     'start_state': 96},
               'Relop': {'first_set': ['<', '=='], 'follow_set': ['(', 'ID', 'NUM'], 'is_terminal': False,
                         'start_state': 99},
               'Additive-expression': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': [';', ')', '|', ']', ','],
                                       'is_terminal': False, 'start_state': 101},
               'Additive-expression-prime': {'first_set': ['(', '*', '+', '-'],
                                             'follow_set': ['<', '==', ';', ')', '|', ']', ','], 'is_terminal': False,
                                             'start_state': 104},
               'Additive-expression-zegond': {'first_set': ['(', 'NUM'],
                                              'follow_set': ['<', '==', ';', ')', '|', ']', ','], 'is_terminal': False,
                                              'start_state': 107},
               'D': {'first_set': ['+', '-'], 'follow_set': ['<', '==', ';', ')', '|', ']', ','], 'is_terminal': False,
                     'start_state': 110},
               'Addop': {'first_set': ['+', '-'], 'follow_set': ['(', 'ID', 'NUM'], 'is_terminal': False,
                         'start_state': 114},
               'Term': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                        'is_terminal': False, 'start_state': 116},
               'Term-prime': {'first_set': ['(', '*'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                              'is_terminal': False, 'start_state': 119},
               'Term-zegond': {'first_set': ['(', 'NUM'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                               'is_terminal': False, 'start_state': 122},
               'G': {'first_set': ['*'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                     'is_terminal': False, 'start_state': 125}, 'Factor': {'first_set': ['(', 'ID', 'NUM'],
                                                                           'follow_set': ['*', '+', '-', ';', ')', '<',
                                                                                          '==', '|', ']', ','],
                                                                           'is_terminal': False, 'start_state': 129},
               'Var-call-prime': {'first_set': ['(', '['],
                                  'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                                  'is_terminal': False, 'start_state': 134},
               'Var-prime': {'first_set': ['['], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                             'is_terminal': False, 'start_state': 138},
               'Factor-prime': {'first_set': ['('], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                                'is_terminal': False, 'start_state': 142}, 'Factor-zegond': {'first_set': ['(', 'NUM'],
                                                                                             'follow_set': ['*', '+',
                                                                                                            '-', ';',
                                                                                                            ')', '<',
                                                                                                            '==', '|',
                                                                                                            ']', ','],
                                                                                             'is_terminal': False,
                                                                                             'start_state': 146},
               'Args': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [')'], 'is_terminal': False, 'start_state': 150},
               'Arg-list': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [')'], 'is_terminal': False,
                            'start_state': 152},
               'Arg-list-prime': {'first_set': [','], 'follow_set': [')'], 'is_terminal': False, 'start_state': 155},
               # terminals from here on
               '$': {'first_set': '$', 'follow_set': [], 'is_terminal': True},
               'int': {'first_set': 'int', 'follow_set': [], 'is_terminal': True},
               'void': {'first_set': 'void', 'follow_set': [], 'is_terminal': True},
               '(': {'first_set': '(', 'follow_set': [], 'is_terminal': True},
               ')': {'first_set': ')', 'follow_set': [], 'is_terminal': True},
               '[': {'first_set': '[', 'follow_set': [], 'is_terminal': True},
               ']': {'first_set': ']', 'follow_set': [], 'is_terminal': True},
               ';': {'first_set': ';', 'follow_set': [], 'is_terminal': True},
               '{': {'first_set': '{', 'follow_set': [], 'is_terminal': True},
               '}': {'first_set': '}', 'follow_set': [], 'is_terminal': True},
               'break': {'first_set': 'break', 'follow_set': [], 'is_terminal': True},
               'if': {'first_set': 'if', 'follow_set': [], 'is_terminal': True},
               'repeat': {'first_set': 'repeat', 'follow_set': [], 'is_terminal': True},
               'return': {'first_set': 'return', 'follow_set': [], 'is_terminal': True},
               'ID': {'first_set': 'ID', 'follow_set': [], 'is_terminal': True},
               'endif': {'first_set': 'endif', 'follow_set': [], 'is_terminal': True},
               'NUM': {'first_set': 'NUM', 'follow_set': [], 'is_terminal': True},
               '=': {'first_set': '=', 'follow_set': [], 'is_terminal': True},
               '*': {'first_set': '*', 'follow_set': [], 'is_terminal': True},
               '+': {'first_set': '+', 'follow_set': [], 'is_terminal': True},
               '-': {'first_set': '-', 'follow_set': [], 'is_terminal': True},
               '<': {'first_set': '<', 'follow_set': [], 'is_terminal': True},
               '==': {'first_set': '==', 'follow_set': [], 'is_terminal': True},
               ',': {'first_set': ',', 'follow_set': [], 'is_terminal': True}}

    edges = {
        # state_num : ( [(edge_symbol1, target_state1), (edge_symbol2, target_state2)], is_final_state )
        # epsilon is shown with ""
        0: ([("Declaration-list", 2)], False),
        1: ([("$", 3)], False),
        2: ([], True),

        3: ([("Declaration", 5), ("", 6)], False),
        4: ([("Declaration-list", 6)], False),
        5: ([], True),

        6: ([("Declaration-initial", 8)], False),
        7: ([("Declaration-prime", 9)], False),
        8: ([], True),

        9: ([("Type-specifier", 11)], False),
        10: ([("ID", 12)], False),
        11: ([], True),

        12: ([("Fun-declaration-prime", 14), ("Var-declaration-prime", 14)], False),
        13: ([], True),

        14: ([("[", 16), (";", 19)], False),
        15: ([("NUM", 17)], False),
        16: ([("]", 18)], False),
        17: ([(";", 19)], False),
        18: ([], True),

        19: ([("(", 21)], False),
        20: ([("Params", 22)], False),
        21: ([(")", 23)], False),
        22: ([("Compound-stmt", 24)], False),
        23: ([], True),

        24: ([("int", 26), ("void", 26)], False),
        25: ([], True),

        26: ([("int", 28), ("void", 31)], False),
        27: ([("ID", 29)], False),
        28: ([("Param-prime", 30)], False),
        29: ([("Param-list", 31)], False),
        30: ([], True),

        31: ([(",", 33), ("", 35)], False),
        32: ([("Param", 34)], False),
        33: ([("Param_list", 35)], False),
        34: ([], True),

        35: ([("Declaration-initial", 37)], False),
        36: ([("Param-prime", 38)], False),
        37: ([], True),

        38: ([("[", 40), ("", 41)], False),
        39: ([("]", 41)], False),
        40: ([], True),

        41: ([("{", 42)], False),
        42: ([("Declaration-list", 43)], False),
        43: ([("Statement-list", 44)], False),
        44: ([("}", 45)], False),
        45: ([], True),

        46: ([("Statement", 47), ("", 48)], False),
        47: ([("Statement-list", 48)], False),
        48: ([], True),

        49: ([("Expression-stmt", 50), ("Compound-stmt", 50),
              ("Selection-stmt", 50), ("Iteration-stmt", 50)],
             False),
        50: ([], True),

        51: ([("Expression", 52), ("break", 52),
              (";", 53)], False),
        52: ([(";", 53)], False),
        53: ([], True),

        54: ([("if", 55)], False),
        55: ([("(", 56)], False),
        56: ([("Expression", 57)], False),
        57: ([(")", 58)], False),
        58: ([("Statement", 59)], False),
        59: ([("Else-stmt", 60)], False),
        60: ([], True),

        61: ([("else", 62), ("endif", 64)], False),
        62: ([("Statement", 63)], False),
        63: ([("endif", 64)], False),
        64: ([], True),

        65: ([("repeat", 66)], False),
        66: ([("Statement", 67)], False),
        67: ([("until", 68)], False),
        68: ([("(", 69)], False),
        69: ([("Expression", 70)], False),
        70: ([(")", 71)], False),
        71: ([], True),

        72: ([("return", 73)], False),
        73: ([("Return-stmt-prime", 74)], False),
        74: ([], True),

        75: ([("Expression", 76), (";", 77)], False),
        76: ([(";", 77)], False),
        77: ([], True),

        78: ([("ID", 79), ("Simple_expression_zegond ", 80)], False),
        79: ([("B", 80)], False),
        80: ([], True),

        81: ([("[", 82)], ("Expression", 83), ("Simple-expression-prime ", 85), False),
        82: ([("Expression", 83)], False),
        83: ([("]", 84)], False),
        84: ([("H", 85)], False),
        85: ([], True),

        86: ([("G", 87), ("Expression", 89)], False),
        87: ([("D", 88)], False),
        88: ([("C", 89)], False),
        89: ([], True),

        90: ([("Additive-expression-zegond", 91)], False),
        91: ([("C", 92)], False),
        92: ([], True),

        93: ([("Additive-expression-prime", 94)], False),
        94: ([("C", 95)], False),
        95: ([], True),

        96: ([("Relop", 97),["",98]], False),
        97: ([("Additive-expression", 98)], False),
        98: ([], True),

        99: ([("<", 100),("==", 100)], False),
        100: ([], True),

        101: ([("Term", 102)], False),
        102: ([("D", 103)], False),
        103: ([], True),

        104: ([("Term-prime", 105)], False),
        105: ([("D", 106)], False),
        106: ([], True),

        107: ([("Term-zegond", 108)], False),
        108: ([("D", 109)], False),
        109: ([], True),

        110: ([("Addop", 111),("",113)], False),
        111: ([("Term", 112)], False),
        112: ([("D", 113)], False),
        113: ([], True),

        114: ([("+", 115),("-", 115)], False),
        115: ([], True),

        116: ([("Factor", 117)], False),
        117: ([("G", 118)], False),
        118: ([], True),

        119: ([("Factor-prime", 120)], False),
        120: ([("G", 121)], False),
        121: ([], True),

        122: ([("Factor-zegond", 123)], False),
        123: ([("G", 124)], False),
        124: ([], True),

        125: ([("*", 126),("", 128)], False),
        126: ([("Factor", 127)], False),
        127: ([("G", 128)], False),
        128: ([], True),

        129: ([("(", 130),("NUM", 132),("ID", 133)], False),
        130: ([("Expression", 131)], False),
        131: ([(")", 132)], False),
        132: ([], True),
        133: ([("Var-call-prime", 132)], False),

        134: ([("(", 135),("Var-prime", 137)], False),
        135: ([("Args", 136)], False),
        136: ([(")", 137)], False),
        137: ([], True),

        138: ([("[", 139),("", 141)], False),
        139: ([("Expression", 140)], False),
        140: ([("]", 141)], False),
        141: ([], True),

        142: ([("{", 143),("", 145)], False),
        143: ([("Args", 144)], False),
        144: ([("}", 145)], False),
        145: ([], True),

        146: ([("{", 147),("NUM", 149)], False),
        147: ([("Expression", 148)], False),
        148: ([("}", 149)], False),
        149: ([], True),

        150: ([("", 151),("Arg-list", 151)], False),
        151: ([], True),

        152: ([("Expression", 153)], False),
        153: ([("Arg-list-prime", 154)], False),
        154: ([], True),

        155: ([(",", 156),("", 158)], False),
        156: ([("Expression", 157)], False),
        157: ([("Arg-list-prime", 158)], False),
        158: ([], True),
    }
    

    def __init__(self, filepath):
        self.input_filename = filepath
        self.scanner = Scanner(filepath)
        self.parse_file = open("parse_tree.txt", 'w')
        self.error_file = open("syntax_errors.txt", 'w')
        self.look_ahead = self.scanner.next_token()

    def start(self):
        root_node = Node("Program", False)
        self.parse(1, root_node)

    def write_parse_tree(self, root_node):
        for pre, fill, node in RenderTree(root_node):
            print("%s%s" % (pre, node.name))

    def parse(self, state, node):
        pass

    def panic_mode(self, state, node):  # returns true if we should go to next state. else False
        pass


class Node_Parser:
    def __init__(self, value, is_terminal,parent_parser):
        self.value = Node(value,parent=parent_parser)
        self.is_terminal = is_terminal



# a = Scanner("../HW1/Practical/tests/tests/PA1_input_output_samples/T05/input.txt")
# a = Compiler("input.txt")
# while True:
#     t = a.next_token()
#     if t == "$":
#         break
