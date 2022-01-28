from anytree import Node, RenderTree


class MyNode:
    def __init__(self, value, is_terminal):
        self.is_terminal = is_terminal
        self.children = []
        if not isinstance(value, str):
            self.value = ", ".join(value)
            if not is_terminal:
                self.symbol = value
            elif value[0] in ["ID", "NUM"]:
                self.symbol = value[0]
            else:
                self.symbol = value[1]
        else:
            self.value = value
            self.symbol = value

    def add_child(self, node):
        self.children.append(node)


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
        self.file = open(filepath + "input.txt", "r")
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
                        return "EOF", "$"
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
                    # return "WHITESPACE", token
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
                                self.step_back()
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
                        self.step_back()
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
                        self.step_back()
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
                        return "EOF", "$"
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
                        return "EOF", "$"
                    elif self.last_char != "*":
                        state = 9
                elif state == 13:
                    if self.last_char != "":
                        self.step_back()
                    token_type = self.get_token(token)
                    self.write_token("({}, {})".format(token_type, token))
                    return token_type, token
                elif state == 14:
                    if self.last_char != "":
                        self.step_back()
                    # return "COMMENT", token
                    return self.next_token()

                elif state == 15:
                    self.write_token("(COMMENT, {})".format(token))
                    # return "COMMENT", token
                    return self.next_token()
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
                        self.step_back()
                    self.write_token("(SYMBOL, *)")
                    return "SYMBOL", "*"
        else:
            return "EOF", "$"

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

    def step_back(self):
        self.file.seek(self.last_pos)


class CodeGenerator:
    def __init__(self, data_start, temp_start, stack_pointer, return_reg):
        self.PB = [
            '0\t(ASSIGN, #0, {}, )'.format(stack_pointer),
            '1\t(ASSIGN, #0, {}, )'.format(return_reg),
            '2\t(SUB, {}, #1, {})'.format(stack_pointer, stack_pointer),
            '3\t(PRINT, {}, , )'.format(stack_pointer),
            '4\t(SUB, {}, #1, {})'.format(stack_pointer, stack_pointer),
            '5\t(JP, @{}, , )'.format(stack_pointer)
        ]
        self.semantic_stack = []
        self.data_end = data_start
        self.temp_end = temp_start
        self.sp = stack_pointer
        self.RR = return_reg

    def get_data_space(self, data_bytes):
        self.data_end += data_bytes
        return self.data_end - data_bytes

    def get_temp_space(self, temp_bytes):
        self.temp_end += temp_bytes
        return self.temp_end - temp_bytes

    def save(self):
        pass


class Parser:
    # a dictionary with grammar symbols as it's keys. every key is mapped to another dictionary
    # containing first_set, follow_set, is_terminal attribute of that symbol
    symbols = {
        'Program': {'first_set': ['$', 'int', 'void'], 'follow_set': [], 'is_terminal': False, 'start_state': 0,
                    'predict_set': ['$', 'int', 'void']},
        'Declaration-list': {'first_set': ['int', 'void', ''], 'follow_set': ['$', '{', 'break', ';', 'if',
                                                                              'repeat', 'return', 'ID', '(',
                                                                              'NUM', '}'], 'is_terminal': False,
                             'start_state': 3, 'predict_set': ['int', 'void', '', '$', '{', 'break',
                                                               ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM',
                                                               '}']},
        'Declaration': {'first_set': ['int', 'void'],
                        'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID',
                                       '(', 'NUM', '}'], 'is_terminal': False, 'start_state': 6,
                        'predict_set': ['int', 'void']},
        'Declaration-initial': {'first_set': ['int', 'void'], 'follow_set': ['(', ';', '[', ',', ')'],
                                'is_terminal': False, 'start_state': 9, 'predict_set': ['int', 'void']},
        'Declaration-prime': {'first_set': ['(', ';', '['],
                              'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return',
                                             'ID', '(', 'NUM', '}'], 'is_terminal': False, 'start_state': 12,
                              'predict_set': ['(', ';', '[']}, 'Var-declaration-prime': {'first_set': [';', '['],
                                                                                         'follow_set': ['int',
                                                                                                        'void',
                                                                                                        '$', '{',
                                                                                                        'break',
                                                                                                        ';',
                                                                                                        'if',
                                                                                                        'repeat',
                                                                                                        'return',
                                                                                                        'ID',
                                                                                                        '(',
                                                                                                        'NUM',
                                                                                                        '}'],
                                                                                         'is_terminal': False,
                                                                                         'start_state': 14,
                                                                                         'predict_set': [';',
                                                                                                         '[']},
        'Fun-declaration-prime': {'first_set': ['('],
                                  'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return',
                                                 'ID', '(', 'NUM', '}'], 'is_terminal': False, 'start_state': 19,
                                  'predict_set': ['(']},
        'Type-specifier': {'first_set': ['int', 'void'], 'follow_set': ['ID'], 'is_terminal': False,
                           'start_state': 24, 'predict_set': ['int', 'void']},
        'Params': {'first_set': ['int', 'void'], 'follow_set': [')'], 'is_terminal': False, 'start_state': 26,
                   'predict_set': ['int', 'void']},
        'Param-list': {'first_set': [',', ''], 'follow_set': [')'], 'is_terminal': False, 'start_state': 31,
                       'predict_set': [',', '', ')']},
        'Param': {'first_set': ['int', 'void'], 'follow_set': [',', ')'], 'is_terminal': False,
                  'start_state': 35, 'predict_set': ['int', 'void']},
        'Param-prime': {'first_set': ['[', ''], 'follow_set': [',', ')'], 'is_terminal': False,
                        'start_state': 38, 'predict_set': ['[', '', ',', ')']},
        'Compound-stmt': {'first_set': ['{'],
                          'follow_set': ['int', 'void', '$', '{', 'break', ';', 'if', 'repeat', 'return', 'ID',
                                         '(', 'NUM', '}', 'endif', 'else', 'until'], 'is_terminal': False,
                          'start_state': 41, 'predict_set': ['{']},
        'Statement-list': {'first_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', ''],
                           'follow_set': ['}'], 'is_terminal': False, 'start_state': 46,
                           'predict_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '',
                                           '}']},
        'Statement': {'first_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM'],
                      'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}', 'endif',
                                     'else', 'until'], 'is_terminal': False, 'start_state': 49,
                      'predict_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM']},
        'Expression-stmt': {'first_set': ['break', ';', 'ID', '(', 'NUM'],
                            'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                           'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 51,
                            'predict_set': ['break', ';', 'ID', '(', 'NUM']},
        'Selection-stmt': {'first_set': ['if'],
                           'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                          'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 54,
                           'predict_set': ['if']}, 'Else-stmt': {'first_set': ['endif', 'else'],
                                                                 'follow_set': ['{', 'break', ';', 'if',
                                                                                'repeat', 'return', 'ID', '(',
                                                                                'NUM', '}', 'endif', 'else',
                                                                                'until'], 'is_terminal': False,
                                                                 'start_state': 61,
                                                                 'predict_set': ['endif', 'else']},
        'Iteration-stmt': {'first_set': ['repeat'],
                           'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                          'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 65,
                           'predict_set': ['repeat']}, 'Return-stmt': {'first_set': ['return'],
                                                                       'follow_set': ['{', 'break', ';', 'if',
                                                                                      'repeat', 'return', 'ID',
                                                                                      '(', 'NUM', '}', 'endif',
                                                                                      'else', 'until'],
                                                                       'is_terminal': False, 'start_state': 72,
                                                                       'predict_set': ['return']},
        'Return-stmt-prime': {'first_set': [';', 'ID', '(', 'NUM'],
                              'follow_set': ['{', 'break', ';', 'if', 'repeat', 'return', 'ID', '(', 'NUM', '}',
                                             'endif', 'else', 'until'], 'is_terminal': False, 'start_state': 75,
                              'predict_set': [';', 'ID', '(', 'NUM']},
        'Expression': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [';', ')', ']', ','], 'is_terminal': False,
                       'start_state': 78, 'predict_set': ['ID', '(', 'NUM']},
        'B': {'first_set': ['=', '(', '[', '*', '+', '-', '<', '==', ''], 'follow_set': [';', ')', ']', ','],
              'is_terminal': False, 'start_state': 81,
              'predict_set': ['=', '(', '[', '*', '+', '-', '<', '==', '', ';', ')', ']', ',']},
        'H': {'first_set': ['=', '*', '+', '-', '<', '==', ''], 'follow_set': [';', ')', ']', ','],
              'is_terminal': False, 'start_state': 86,
              'predict_set': ['=', '*', '+', '-', '<', '==', '', ';', ')', ']', ',']},
        'Simple-expression-zegond': {'first_set': ['(', 'NUM'], 'follow_set': [';', ')', ']', ','],
                                     'is_terminal': False, 'start_state': 90, 'predict_set': ['(', 'NUM']},
        'Simple-expression-prime': {'first_set': ['(', '*', '+', '-', '<', '==', ''],
                                    'follow_set': [';', ')', ']', ','], 'is_terminal': False, 'start_state': 93,
                                    'predict_set': ['(', '*', '+', '-', '<', '==', '', ';', ')', ']', ',']},
        'C': {'first_set': ['<', '==', ''], 'follow_set': [';', ')', ']', ','], 'is_terminal': False,
              'start_state': 96, 'predict_set': ['<', '==', '', ';', ')', ']', ',']},
        'Relop': {'first_set': ['<', '=='], 'follow_set': ['(', 'ID', 'NUM'], 'is_terminal': False,
                  'start_state': 99, 'predict_set': ['<', '==']},
        'Additive-expression': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': [';', ')', ']', ','],
                                'is_terminal': False, 'start_state': 101, 'predict_set': ['(', 'ID', 'NUM']},
        'Additive-expression-prime': {'first_set': ['(', '*', '+', '-', ''],
                                      'follow_set': ['<', '==', ';', ')', ']', ','], 'is_terminal': False,
                                      'start_state': 104,
                                      'predict_set': ['(', '*', '+', '-', '', '<', '==', ';', ')', ']', ',']},
        'Additive-expression-zegond': {'first_set': ['(', 'NUM'], 'follow_set': ['<', '==', ';', ')', ']', ','],
                                       'is_terminal': False, 'start_state': 107, 'predict_set': ['(', 'NUM']},
        'D': {'first_set': ['+', '-', ''], 'follow_set': ['<', '==', ';', ')', ']', ','], 'is_terminal': False,
              'start_state': 110, 'predict_set': ['+', '-', '', '<', '==', ';', ')', ']', ',']},
        'Addop': {'first_set': ['+', '-'], 'follow_set': ['(', 'ID', 'NUM'], 'is_terminal': False,
                  'start_state': 114, 'predict_set': ['+', '-']},
        'Term': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': ['+', '-', ';', ')', '<', '==', ']', ','],
                 'is_terminal': False, 'start_state': 116, 'predict_set': ['(', 'ID', 'NUM']},
        'Term-prime': {'first_set': ['(', '*', ''], 'follow_set': ['+', '-', ';', ')', '<', '==', ']', ','],
                       'is_terminal': False, 'start_state': 119,
                       'predict_set': ['(', '*', '', '+', '-', ';', ')', '<', '==', ']', ',']},
        'Term-zegond': {'first_set': ['(', 'NUM'], 'follow_set': ['+', '-', ';', ')', '<', '==', ']', ','],
                        'is_terminal': False, 'start_state': 122, 'predict_set': ['(', 'NUM']},
        'G': {'first_set': ['*', ''], 'follow_set': ['+', '-', ';', ')', '<', '==', ']', ','],
              'is_terminal': False, 'start_state': 125,
              'predict_set': ['*', '', '+', '-', ';', ')', '<', '==', ']', ',']},
        'Factor': {'first_set': ['(', 'ID', 'NUM'], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', ']', ','],
                   'is_terminal': False, 'start_state': 129, 'predict_set': ['(', 'ID', 'NUM']},
        'Var-call-prime': {'first_set': ['(', '[', ''],
                           'follow_set': ['*', '+', '-', ';', ')', '<', '==', ']', ','], 'is_terminal': False,
                           'start_state': 134,
                           'predict_set': ['(', '[', '', '*', '+', '-', ';', ')', '<', '==', ']', ',']},
        'Var-prime': {'first_set': ['[', ''], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', ']', ','],
                      'is_terminal': False, 'start_state': 138,
                      'predict_set': ['[', '', '*', '+', '-', ';', ')', '<', '==', ']', ',']},
        'Factor-prime': {'first_set': ['(', ''], 'follow_set': ['*', '+', '-', ';', ')', '<', '==', ']', ','],
                         'is_terminal': False, 'start_state': 142,
                         'predict_set': ['(', '', '*', '+', '-', ';', ')', '<', '==', ']', ',']},
        'Factor-zegond': {'first_set': ['(', 'NUM'],
                          'follow_set': ['*', '+', '-', ';', ')', '<', '==', ']', ','], 'is_terminal': False,
                          'start_state': 146, 'predict_set': ['(', 'NUM']},
        'Args': {'first_set': ['ID', '(', 'NUM', ''], 'follow_set': [')'], 'is_terminal': False,
                 'start_state': 150, 'predict_set': ['ID', '(', 'NUM', '', ')']},
        'Arg-list': {'first_set': ['ID', '(', 'NUM'], 'follow_set': [')'], 'is_terminal': False,
                     'start_state': 152, 'predict_set': ['ID', '(', 'NUM']},
        'Arg-list-prime': {'first_set': [',', ''], 'follow_set': [')'], 'is_terminal': False, 'start_state': 155,
                           'predict_set': [',', '', ')']},
        '$': {'first_set': ['$'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['$']},
        'int': {'first_set': ['int'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['int']},
        'void': {'first_set': ['void'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['void']},
        '(': {'first_set': ['('], 'follow_set': [], 'is_terminal': True, 'predict_set': ['(']},
        ')': {'first_set': [')'], 'follow_set': [], 'is_terminal': True, 'predict_set': [')']},
        '[': {'first_set': ['['], 'follow_set': [], 'is_terminal': True, 'predict_set': ['[']},
        ']': {'first_set': [']'], 'follow_set': [], 'is_terminal': True, 'predict_set': [']']},
        ';': {'first_set': [';'], 'follow_set': [], 'is_terminal': True, 'predict_set': [';']},
        '{': {'first_set': ['{'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['{']},
        '}': {'first_set': ['}'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['}']},
        'break': {'first_set': ['break'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['break']},
        'if': {'first_set': ['if'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['if']},
        'else': {'first_set': ['else'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['else']},
        'repeat': {'first_set': ['repeat'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['repeat']},
        'return': {'first_set': ['return'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['return']},
        'until': {'first_set': ['until'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['until']},
        'ID': {'first_set': ['ID'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['ID']},
        'endif': {'first_set': ['endif'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['endif']},
        'NUM': {'first_set': ['NUM'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['NUM']},
        '=': {'first_set': ['='], 'follow_set': [], 'is_terminal': True, 'predict_set': ['=']},
        '*': {'first_set': ['*'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['*']},
        '+': {'first_set': ['+'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['+']},
        '-': {'first_set': ['-'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['-']},
        '<': {'first_set': ['<'], 'follow_set': [], 'is_terminal': True, 'predict_set': ['<']},
        '==': {'first_set': ['=='], 'follow_set': [], 'is_terminal': True, 'predict_set': ['==']},
        ',': {'first_set': [','], 'follow_set': [], 'is_terminal': True, 'predict_set': [',']}}

    edges = {
        0: ([('Declaration-list', 1)], True, False),
        1: ([('$', 2)], False, False),
        2: ([], False, True),

        3: ([('Declaration', 4), ('', 5)], True, False),
        4: ([('Declaration-list', 5)], False, False),
        5: ([], False, True),

        6: ([('Declaration-initial', 7)], True, False),
        7: ([('Declaration-prime', 8)], False, False),
        8: ([], False, True),

        9: ([('Type-specifier', 10)], True, False),
        10: ([('ID', 11)], False, False),
        11: ([], False, True),

        12: ([('Fun-declaration-prime', 13), ('Var-declaration-prime', 13)], True, False),
        13: ([], False, True),

        14: ([('[', 15), (';', 18)], True, False),
        15: ([('NUM', 16)], False, False),
        16: ([(']', 17)], False, False),
        17: ([(';', 18)], False, False),
        18: ([], False, True),

        19: ([('(', 20)], True, False),
        20: ([('Params', 21)], False, False),
        21: ([(')', 22)], False, False),
        22: ([('Compound-stmt', 23)], False, False),
        23: ([], False, True),

        24: ([('int', 25), ('void', 25)], True, False),
        25: ([], False, True),

        26: ([('int', 27), ('void', 30)], True, False),
        27: ([('ID', 28)], False, False),
        28: ([('Param-prime', 29)], False, False),
        29: ([('Param-list', 30)], False, False),
        30: ([], False, True),

        31: ([(',', 32), ('', 34)], True, False),
        32: ([('Param', 33)], False, False),
        33: ([('Param-list', 34)], False, False),
        34: ([], False, True),

        35: ([('Declaration-initial', 36)], True, False),
        36: ([('Param-prime', 37)], False, False),
        37: ([], False, True),

        38: ([('[', 39), ('', 40)], True, False),
        39: ([(']', 40)], False, False),
        40: ([], False, True),

        41: ([('{', 42)], True, False),
        42: ([('Declaration-list', 43)], False, False),
        43: ([('Statement-list', 44)], False, False),
        44: ([('}', 45)], False, False),
        45: ([], False, True),

        46: ([('Statement', 47), ('', 48)], True, False),
        47: ([('Statement-list', 48)], False, False),
        48: ([], False, True),

        49: ([('Expression-stmt', 50), ('Compound-stmt', 50), ('Selection-stmt', 50),
              ('Iteration-stmt', 50), ('Return-stmt', 50)],
             True, False),
        50: ([], False, True),

        51: ([('Expression', 52), ('break', 52), (';', 53)], True, False),
        52: ([(';', 53)], False, False),
        53: ([], False, True),

        54: ([('if', 55)], True, False),
        55: ([('(', 56)], False, False),
        56: ([('Expression', 57)], False, False),
        57: ([(')', 58)], False, False),
        58: ([('Statement', 59)], False, False),
        59: ([('Else-stmt', 60)], False, False),
        60: ([], False, True),

        61: ([('else', 62), ('endif', 64)], True, False),
        62: ([('Statement', 63)], False, False),
        63: ([('endif', 64)], False, False),
        64: ([], False, True),

        65: ([('repeat', 66)], True, False),
        66: ([('Statement', 67)], False, False),
        67: ([('until', 68)], False, False),
        68: ([('(', 69)], False, False),
        69: ([('Expression', 70)], False, False),
        70: ([(')', 71)], False, False),
        71: ([], False, True),

        72: ([('return', 73)], True, False),
        73: ([('Return-stmt-prime', 74)], False, False),
        74: ([], False, True),

        75: ([('Expression', 76), (';', 77)], True, False),
        76: ([(';', 77)], False, False),
        77: ([], False, True),

        78: ([('ID', 79), ('Simple-expression-zegond', 80)], True, False),
        79: ([('B', 80)], False, False),
        80: ([], False, True),

        81: ([('[', 82), ('Simple-expression-prime', 85), ('=', 159)], True, False),
        82: ([('Expression', 83)], False, False),
        83: ([(']', 84)], False, False),
        84: ([('H', 85)], False, False),
        159: ([('Expression', 85)], False, False),
        85: ([], False, True),

        86: ([('G', 87), ('=', 160)], True, False),
        87: ([('D', 88)], False, False),
        88: ([('C', 89)], False, False),
        160: ([('Expression', 89)], False, False),
        89: ([], False, True),

        90: ([('Additive-expression-zegond', 91)], True, False),
        91: ([('C', 92)], False, False),
        92: ([], False, True),

        93: ([('Additive-expression-prime', 94)], True, False),
        94: ([('C', 95)], False, False),
        95: ([], False, True),

        96: ([('Relop', 97), ['', 98]], True, False),
        97: ([('Additive-expression', 98)], False, False),
        98: ([], False, True),

        99: ([('<', 100), ('==', 100)], True, False),
        100: ([], False, True),

        101: ([('Term', 102)], True, False),
        102: ([('D', 103)], False, False),
        103: ([], False, True),

        104: ([('Term-prime', 105)], True, False),
        105: ([('D', 106)], False, False),
        106: ([], False, True),

        107: ([('Term-zegond', 108)], True, False),
        108: ([('D', 109)], False, False),
        109: ([], False, True),

        110: ([('Addop', 111), ('', 113)], True, False),
        111: ([('Term', 112)], False, False),
        112: ([('D', 113)], False, False),
        113: ([], False, True),

        114: ([('+', 115), ('-', 115)], True, False),
        115: ([], False, True),

        116: ([('Factor', 117)], True, False),
        117: ([('G', 118)], False, False),
        118: ([], False, True),

        119: ([('Factor-prime', 120)], True, False),
        120: ([('G', 121)], False, False),
        121: ([], False, True),

        122: ([('Factor-zegond', 123)], True, False),
        123: ([('G', 124)], False, False),
        124: ([], False, True),

        125: ([('*', 126), ('', 128)], True, False),
        126: ([('Factor', 127)], False, False),
        127: ([('G', 128)], False, False),
        128: ([], False, True),

        129: ([('(', 130), ('NUM', 132), ('ID', 133)], True, False),
        130: ([('Expression', 131)], False, False),
        131: ([(')', 132)], False, False),
        132: ([], False, True),
        133: ([('Var-call-prime', 132)], False, False),

        134: ([('(', 135), ('Var-prime', 137)], True, False),
        135: ([('Args', 136)], False, False),
        136: ([(')', 137)], False, False),
        137: ([], False, True),

        138: ([('[', 139), ('', 141)], True, False),
        139: ([('Expression', 140)], False, False),
        140: ([(']', 141)], False, False),
        141: ([], False, True),

        142: ([('(', 143), ('', 145)], True, False),
        143: ([('Args', 144)], False, False),
        144: ([(')', 145)], False, False),
        145: ([], False, True),

        146: ([('(', 147), ('NUM', 149)], True, False),
        147: ([('Expression', 148)], False, False),
        148: ([(')', 149)], False, False),
        149: ([], False, True),

        150: ([('', 151), ('Arg-list', 151)], True, False),
        151: ([], False, True),

        152: ([('Expression', 153)], True, False),
        153: ([('Arg-list-prime', 154)], False, False),
        154: ([], False, True),

        155: ([(',', 156), ('', 158)], True, False),
        156: ([('Expression', 157)], False, False),
        157: ([('Arg-list-prime', 158)], False, False),
        158: ([], False, True)}

    def __init__(self, filepath):
        self.scanner = Scanner(filepath)
        self.error_file = open("syntax_errors.txt", 'w')
        self.look_ahead = ""
        self.current_token = ""
        self.wait_scanner = False
        self.root_node = None
        self.symbol_table = [
            {"name": "output", "type": "func", "return type": "void", "address": 2, "args": []},

        ]
        self.code_generator = CodeGenerator(400, 808, 800, 804)
        self.scope_stack = [0]
        self.in_func_args = False

    def parse(self):
        self.root_node = MyNode("Program", False)
        current_node = self.root_node
        current_state = 0
        state_stack = []
        node_stack = []

        while True:
            self.look_ahead = self.next_token()
            self.parser_action(current_state)
            if self.edges[current_state][2]:
                if current_state == 2:
                    break
                current_state = state_stack.pop()
                current_node = node_stack.pop()
                self.wait_scanner = True
                continue

            l_a_lexeme = self.look_ahead[0] if self.look_ahead[0] in ["ID", "NUM"] else self.look_ahead[1]
            state_edges = self.edges[current_state][0]
            error_flag = True
            for edge in state_edges:
                if edge[0] == "":
                    if l_a_lexeme in self.symbols[current_node.symbol]["follow_set"]:
                        current_node.add_child(MyNode("epsilon", True))
                        # print("used epsilon")
                        current_state = edge[1]
                        self.wait_scanner = True
                        error_flag = False
                        break
                elif l_a_lexeme in self.symbols[edge[0]]["predict_set"]:
                    error_flag = False
                    if self.symbols[edge[0]]["is_terminal"]:
                        current_node.add_child(MyNode(self.look_ahead, True))
                        current_state = edge[1]
                        break
                    else:
                        current_node.add_child(MyNode(edge[0], False))
                        state_stack.append(edge[1])
                        node_stack.append(current_node)
                        current_state = self.symbols[edge[0]]["start_state"]
                        current_node = current_node.children[-1]
                        self.wait_scanner = True
                        break
            if error_flag:
                # print(current_state, self.look_ahead, state_stack)
                edge = state_edges[0]
                if self.symbols[edge[0]]["is_terminal"]:
                    self.error_file.write("#{} : syntax error, missing {}\n".format(self.scanner.current_line, edge[0]))
                    current_state = edge[1]
                    self.wait_scanner = True
                else:
                    if l_a_lexeme in self.symbols[edge[0]]["follow_set"]:
                        self.error_file.write(
                            "#{} : syntax error, missing {}\n".format(self.scanner.current_line, edge[0]))
                        current_state = edge[1]
                        self.wait_scanner = True
                    else:
                        if self.panic_mode(current_state, current_node):
                            break

        self.write_parse_tree(self.root_node)
        if self.error_file.tell() == 0:
            self.error_file.write("There is no syntax error.")

        self.error_file.close()

    def parser_action(self, state):
        if state == 10 or state == 27:
            self.symbol_table.append({"name": self.look_ahead[1], "type": self.current_token[1]})
            if self.in_func_args:
                self.symbol_table[self.in_func_args]["args"].append(self.look_ahead[1])
        elif state == 15:
            self.symbol_table[-1]["type"] = "int[]"
            self.symbol_table[-1]["length"] = int(self.look_ahead[1])
            self.symbol_table[-1]["init_val"] = self.code_generator.get_data_space(int(self.look_ahead[1])*4)
        elif state == 18 or state == 29 or state == 33:
            self.symbol_table[-1]["address"] = self.code_generator.get_data_space(4)
            self.print_symbol_table()
        elif state == 20:
            self.in_func_args = len(self.symbol_table) - 1
            self.symbol_table[-1]["return type"] = self.symbol_table[-1]["type"]
            self.symbol_table[-1]["type"] = "func"
            self.symbol_table[-1]["address"] = len(self.code_generator.PB)
            self.symbol_table[-1]["args"] = []
            self.scope_stack.append(len(self.symbol_table))
        elif state == 22:
            self.in_func_args = False
        elif state == 23:
            if len(self.symbol_table) > self.scope_stack[-1]:
                self.symbol_table = self.symbol_table[:self.scope_stack[-1]]
                self.scope_stack.pop()
        elif state == 39:
            self.symbol_table[-1]["type"] = "int[]"

    def write_parse_tree(self, root_node):
        parse_file = open("parse_tree.txt", 'w', encoding='utf-8')
        anytree_root = self.make_anytree(root_node)
        root_information = RenderTree(anytree_root).by_attr('name')
        parse_file.write(root_information)
        parse_file.close()
        # root_information = root_information.replace("\n", "\r\n")
        # print(root_information[10:12].encode())
        # parse_file.write(bytes(root_information, 'utf-8'))

    def make_anytree(self, root_node: MyNode, parent=-1):
        if root_node.is_terminal:
            if root_node.value[-1] != "$":
                if root_node.value != "epsilon":
                    value = "(" + root_node.value + ")"
                else:
                    value = "epsilon"
            else:
                value = "$"
        else:
            value = root_node.value
        if parent == -1:
            anytree_node = Node(value)
        else:
            anytree_node = Node(value, parent=parent)
        for x in root_node.children:
            self.make_anytree(x, parent=anytree_node)
        return anytree_node

    # continues removing tokens .returns True if reaches EOF
    def panic_mode(self, state, node):  # returns true if we should go to next state. else False
        edge = self.edges[state][0][0]
        while True:
            l_a_lexeme = self.look_ahead[0] if self.look_ahead[0] in ["ID", "NUM"] else self.look_ahead[1]
            if l_a_lexeme in self.symbols[edge[0]]["first_set"] or l_a_lexeme in self.symbols[edge[0]]["follow_set"]:
                self.wait_scanner = True
                return False
            if l_a_lexeme == "$":
                self.error_file.write("#{} : syntax error, Unexpected EOF\n".format(self.scanner.current_line))
                return True
            self.error_file.write("#{} : syntax error, illegal {}\n".format(self.scanner.current_line, l_a_lexeme))
            self.look_ahead = self.next_token()

    def next_token(self):
        if self.wait_scanner:
            self.wait_scanner = False
            return self.look_ahead
        else:
            self.current_token = self.look_ahead
            return self.scanner.next_token()

    @staticmethod
    def compare_files(filepath, read_type="r"):
        first_file = open(filepath + "/parse_tree.txt", read_type).read()
        second_file = open("parse_tree.txt", read_type).read()
        if first_file == second_file:
            print("equal Parse Tree")
        else:
            print("different Parse Tree")

        first_file = open(filepath + "/syntax_errors.txt", read_type).read()
        second_file = open("syntax_errors.txt", read_type).read()
        if first_file == second_file:
            print("equal syntax errors")
        else:
            print("different syntax errors")

    @staticmethod
    def test_all(path_to_test_cases):
        for i in range(1, 11):
            filepath = path_to_test_cases + "/T{}/".format(str(i).zfill(2))
            print("\ntest-case {}".format(str(i).zfill(2)))
            a = Parser(filepath)
            a.parse()
            Parser.compare_files(filepath, "r")

    def print_symbol_table(self):
        print("\n***********")
        for x in self.symbol_table:
            print(x)


# filepath = ""
filepath = "../HW3/Practical/TestCases/T2/"
a = Parser(filepath)
a.parse()
