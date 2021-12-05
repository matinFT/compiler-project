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
    symbols = {'Program': {'first_set': ['$', 'int', 'void'], 'follow_set': [], 'is_terminal': False},
               'Declaration-list': {'first_set': ['int', 'void'],
                                    'follow_set': ['$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM',
                                                   '}'],
                                    'is_terminal': False}, 'Declaration': {'first_set': ['int', 'void'],
                                                                           'follow_set': ['int', 'void', '$', '{',
                                                                                          'break',
                                                                                          ';',
                                                                                          'if', 'repeat', 'return',
                                                                                          'ID', '(',
                                                                                          'NUM', '}'],
                                                                           'is_terminal': False},
               'Declaration-initial': {'first_set': ['int', 'void'], 'follow_set': ['(', ';', '[', ',', ')'],
                                       'is_terminal': False}, 'Declaration-prime': {'first_set': ['(', ';', '['],
                                                                                    'follow_set': ['int', 'void', '$',
                                                                                                   '{',
                                                                                                   'break', ';', 'if',
                                                                                                   'repeat',
                                                                                                   'return', 'ID', '(',
                                                                                                   'NUM',
                                                                                                   '}'],
                                                                                    'is_terminal': False},
               'Var-declaration-prime': {'first_set': [';', '['],
                                         'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return',
                                                        'ID',
                                                        '(', 'NUM', '}'], 'is_terminal': False},
               'Fun-declaration-prime': {'first_set': ['('],
                                         'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return',
                                                        'ID',
                                                        '(', 'NUM', '}'], 'is_terminal': False},
               'Type-specifier': {'first_set': ['int', 'void'], 'follow_set': ['ID'], 'is_terminal': False},
               'Params': {'first_set': ['int', 'void'], 'follow_set': [')'], 'is_terminal': False},
               'Param-list': {'first_set': [','], 'follow_set': [')'], 'is_terminal': False},
               'Param': {'first_set': ['int', 'void'], 'follow_set': [',', ')'], 'is_terminal': False},
               'Param-prime': {'first_set': ['['], 'follow_set': [',', ')'], 'is_terminal': False},
               'Compound-stmt': {'first_set': ['{'],
                                 'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID',
                                                '(',
                                                'NUM',
                                                '}', 'endif', 'else', 'until'], 'is_terminal': False},
               'Statement-list': {'first_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
                                  'follow_set': ['}'], 'is_terminal': False},
               'Statement': {'first_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
                             'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif',
                                            'else',
                                            'until'], 'is_terminal': False},
               'Expression-stmt': {'first_set': ['break', ';', 'ID', '(', 'NUM'],
                                   'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                                  'endif',
                                                  'else', 'until'], 'is_terminal': False},
               'Selection-stmt': {'first_set': ['if'],
                                  'follow_set': ['{',
                                                 'break',
                                                 ';',
                                                 'if',
                                                 'repeat',
                                                 'return',
                                                 'ID',
                                                 '(',
                                                 'NUM',
                                                 '}',
                                                 'endif',
                                                 'else',
                                                 'until'],
                                  'is_terminal': False},
               'Else-stmt': {'first_set': ['endif', 'else'],
                             'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif',
                                            'else',
                                            'until'], 'is_terminal': False}, 'Iteration-stmt': {'first_set': ['repeat'],
                                                                                                'follow_set': ['{',
                                                                                                               'break',
                                                                                                               ';',
                                                                                                               'if',
                                                                                                               'repeat',
                                                                                                               'return',
                                                                                                               'ID',
                                                                                                               '(',
                                                                                                               'NUM',
                                                                                                               '}',
                                                                                                               'endif',
                                                                                                               'else',
                                                                                                               'until'],
                                                                                                'is_terminal': False},
               'Return-stmt': {'first_set': ['return'],
                               'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                              'endif',
                                              'else',
                                              'until'], 'is_terminal': False},
               'Return-stmt-prime': {'first_set': [';', 'ID', '(', 'NUM'],
                                     'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                                    'endif',
                                                    'else', 'until'], 'is_terminal': False},
               'Expression': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [';', ')', '|', ']', ','],
                              'is_terminal': False},
               'B': {'first_set': ['=', '(', '[', '*', '+', '-', '<', '=='], 'follow_set': [';', ')', '|', ']', ','],
                     'is_terminal': False},
               'H': {'first_set': ['=', '*', '+', '-', '<', '=='], 'follow_set': [';', ')', '|', ']', ','],
                     'is_terminal': False},
               'Simple-expression-zegond': {'first_set': ['(', 'NUM'], 'follow_set': [';', ')', '|', ']', ','],
                                            'is_terminal': False},
               'Simple-expression-prime': {'first_set': ['(', '*', '+', '-', '<', '=='],
                                           'follow_set': [';', ')', '|', ']', ','],
                                           'is_terminal': False},
               'C': {'first_set': ['<', '=='], 'follow_set': [';', ')', '|', ']', ','], 'is_terminal': False},
               'Relop': {'first_set': ['<', '=='], 'follow_set': ['(', 'ID', 'NUM'], 'is_terminal': False},
               'Additive-expression': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': [';', ')', '|', ']', ','],
                                       'is_terminal': False},
               'Additive-expression-prime': {'first_set': ['(', '*', '+', '-'],
                                             'follow_set': ['<', '==', ';',
                                                            ')',
                                                            '|', ']', ','],
                                             'is_terminal': False},
               'Additive-expression-zegond': {'first_set': ['(', 'NUM'],
                                              'follow_set': ['<', '==', ';', ')', '|', ']', ','],
                                              'is_terminal': False},
               'D': {'first_set': ['+', '-'], 'follow_set': ['<', '==', ';', ')', '|', ']', ','], 'is_terminal': False},
               'Addop': {'first_set': ['+', '-'], 'follow_set': ['(', 'ID', 'NUM'], 'is_terminal': False},
               'Term': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                        'is_terminal': False},
               'Term-prime': {'first_set': ['(', '*'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                              'is_terminal': False},
               'Term-zegond': {'first_set': ['(', 'NUM'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                               'is_terminal': False},
               'G': {'first_set': ['*'], 'follow_set': ['+', '-', ';', ')', '<', '==', '|', ']', ','],
                     'is_terminal': False},
               'Factor': {'first_set': ['(', 'ID', 'NUM'],
                          'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                          'is_terminal': False},
               'Var-call-prime': {'first_set': ['(', '['],
                                  'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                                  'is_terminal': False},
               'Var-prime': {'first_set': ['['], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                             'is_terminal': False},
               'Factor-prime': {'first_set': ['('], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                                'is_terminal': False},
               'Factor-zegond': {'first_set': ['(', 'NUM'],
                                 'follow_set': ['*', '+', '-', ';', ')', '<', '==', '|', ']', ','],
                                 'is_terminal': False},
               'Args': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [')'], 'is_terminal': False},
               'Arg-list': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [')'], 'is_terminal': False},
               'Arg-list-prime': {'first_set': [','], 'follow_set': [')'], 'is_terminal': False},

               # terminals from here
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

    predicts = {
        # state_num : ( [(edge_symbol1, target_state1), (edge_symbol2, target_state2)], is_final_state )
        # epsilon is shown with ""
        1: ([("Declaration-list", 2)], False),
        2: ([("$", 3)], False),
        3: ([], True),
        4: ([("Declaration", 5), ("", 6)], False),
        5: ([("Declaration-list", 6)], False),
        6: ([], True),
        7: ([("Declaration-initial", 8)], False),
        8: ([("Declaration-prime", 9)], False),
        9: ([], True),
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
        pass

    def parse(self, state, node):
        pass

    def panic_mode(self, state, node):  # returns true if we should go to next state. else False
        pass


class Node:
    def __init__(self, value, is_terminal):
        self.value = value
        self.is_terminal = is_terminal
        self.children = []

    def add_child(self, node):
        self.children.append(node)


a = Scanner("../HW1/Practical/tests/tests/PA1_input_output_samples/T05/input.txt")
# a = Compiler("input.txt")
# while True:
#     t = a.next_token()
#     if t == "$":
#         break
