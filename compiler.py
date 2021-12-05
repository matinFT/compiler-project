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
    first_sets = {"Program": ["$", "int", "void"],
                  "Declaration_list": ["int", "void"],
                  "Declaration": ["int", "void"],
                  "Declaration_initial": ["int", "void"],
                  "Declaration_prime": ["(", ";", "["],
                  "Var_declaration_prime": [";", "["],
                  "Fun_declaration_prime": ["("],
                  "Type_specifier": ["int", "void"],
                  "Params": ["int", "void"],
                  "Param_list": [","],
                  "Param": ["int", "void"],
                  "Param_prime": ["["],
                  "Compound_stmt": ["{"],
                  "Statement_list": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM"],
                  "Statement": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM"],
                  "Expression_stmt": ["break", ";", "ID", "(", "NUM"],
                  "Selection_stmt": ["if"],
                  "Else_stmt": ["endif", "else"],
                  "Iteration_stmt": ["repeat"],
                  "Return_stmt": ["return"],
                  "Return_stmt_prime": [";", "ID", "(", "NUM"],
                  "Expression": ["ID", "(", "NUM"],
                  "B": ["=", "(", "[", "*", "+", "-", "<", "==",   ],
                  "H": ["=", "*", "+", "-", "<", "=="],
                  "Simple_expression_zegond": ["(", "NUM"],
                  "Simple_expression_prime": ["(", "*", "+", "-", "<", "=="],
                  "C": ["<", "=="],
                  "Relop": ["<", "=="],
                  "Additive_expression": ["(", "ID", "NUM"],
                  "Additive_expression_prime": ["(", "*", "+", "-"],
                  "Additive_expression_zegond": ["(", "NUM"],
                  "D": ["+", "-"],
                  "Addop": ["+", "-"],
                  "Term": ["(", "ID", "NUM"],
                  "Term_prime": ["(", "*"],
                  "Term_zegond": ["(", "NUM"],
                  "G": ["*"],
                  "Factor": ["(", "ID", "NUM"],
                  "Var_call_prime": ["(", "["],
                  "Var_prime": ["["],
                  "Factor_prime": ["("],
                  "Factor_zegond": ["(", "NUM"],
                  "Args": ["ID", "(", "NUM"],
                  "Arg_list": ["ID", "(", "NUM"],
                  "Arg_list_prime": [","],
                  }

    follow_sets = {"Program": [],
                   "Declaration_list": ["$", "{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}"],
                   "Declaration": ["int", "void", "$", "{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}"],
                   "Declaration_initial": ["(", ";", "[", ",", ")"],
                   "Declaration_prime": ["int", "void", "$", "{", "break", ";", "if", "repeat", "return", "ID", "(",
                                         "NUM", "}"],
                   "Var_declaration_prime": ["int", "void", "$", "{", "break", ";", "if", "repeat", "return", "ID", "(",
                                             "NUM", "}"],
                   "Fun_declaration_prime": ["int", "void", "$", "{", "break", ";", "if", "repeat", "return", "ID", "(",
                                             "NUM", "}"],
                   "Type_specifier": ["ID"],
                   "Params": [")"],
                   "Param_list": [")"],
                   "Param": [",", ")"],
                   "Param_prime": [",", ")"],
                   "Compound_stmt": ["int", "void", "$", "{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM",
                                     "}", "endif", "else", "until"],
                   "Statement_list": ["}"],
                   "Statement": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif", "else",
                                 "until"],
                   "Expression_stmt": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif",
                                       "else", "until"],
                   "Selection_stmt": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif",
                                      "else", "until"],
                   "Else_stmt": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif", "else",
                                 "until"],
                   "Iteration_stmt": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif",
                                      "else", "until"],
                   "Return_stmt": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif", "else",
                                   "until"],
                   "Return_stmt_prime": ["{", "break", ";", "if", "repeat", "return", "ID", "(", "NUM", "}", "endif",
                                         "else", "until"],
                   "Expression": [";", ")", "|", "]", ","],
                   "B": [";", ")", "|", "]", ","],
                   "H": [";", ")", "|", "]", ","],
                   "Simple_expression_zegond": [";", ")", "|", "]", ","],
                   "Simple_expression_prime": [";", ")", "|", "]", ","],
                   "C": [";", ")", "|", "]", ","],
                   "Relop": ["(", "ID", "NUM"],
                   "Additive_expression": [";", ")", "|", "]", ","],
                   "Additive_expression_prime": ["<", "==", ";", ")", "|", "]", ","],
                   "Additive_expression_zegond": ["<", "==", ";", ")", "|", "]", ","],
                   "D": ["<", "==", ";", ")", "|", "]", ","],
                   "Addop": ["(", "ID", "NUM"],
                   "Term": ["+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Term_prime": ["+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Term_zegond": ["+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "G": ["+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Factor": ["*", "+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Var_call_prime": ["*", "+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Var_prime": ["*", "+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Factor_prime": ["*", "+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Factor_zegond": ["*", "+", "-", ";", ")", "<", "==", "|", "]", ","],
                   "Args": [")"],
                   "Arg_list": [")"],
                   "Arg_list_prime": [")"],
                   }

    def __init__(self, filepath):
        self.input_filename = filepath
        self.scanner = Scanner(filepath)
        self.parse_file = open("parse_tree.txt", 'w')
        self.error_file = open("syntax_errors.txt", 'w')
        self.look_ahead = self.scanner.next_token()

    def start(self):
        root_node = Node("Program ", False)
        self.parse(1, root_node)

    def write_parse_tree(self, root_node):
        pass

    def parse(self, state, node):
        if state == 1:
            if self.look_ahead not in self.first_sets["Declaration_list"]:
                if self.panic_mode(1, node):
                    node.add_child(Node("Declaration_list", False))
                    self.parse(2, node)
                else:
                    self.parse(1, node)
            else:
                child_node = Node("Declaration_list", False)
                node.add_child(child_node)
                self.parse(4, child_node)

            # self.panic_mode()
            pass

    #
    #     codes for state 1 to 80
    #

    #
    #     codes for state 81 to 158
    #

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
while True:
    t = a.next_token()
    if t == "$":
        break
