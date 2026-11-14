from dataclasses import dataclass
from typing import Any

@dataclass
class Token:
    type: str
    value: Any
    line: int

RESERVED_WORDS = {
    "if",
    "goto",
    "and",
    "or",
    "not"
}

OPERATORS = {
    "+",
    "-",
    "*",
    "/",
    "%",
    "<",
    "<=",
    ">",
    ">=",
    "==",
    "!="
}
    
def is_letter(char):
    return char.isalpha() or char == "_"


def is_digit(char):
    return char.isdigit()
    
def read_identifier(code, position, line):

    start = position

    while position < len(code) and (
        is_letter(code[position]) or is_digit(code[position])
    ):
        position += 1

    word = code[start:position]

    if word in RESERVED_WORDS:
        token_type = word.upper()
    else:
        token_type = "IDENTIFIER"

    token = Token(token_type, word, line)

    return token, position

def read_number(code, position, line):

    start = position

    while position < len(code) and is_digit(code[position]):
        position += 1

    number = int(code[start:position])

    token = Token("NUMBER", number, line)

    return token, position

def read_string(code, position, line):

    position += 1  # Skip opening quotation mark

    start = position

    while position < len(code) and code[position] != '"':

        if code[position] == "\n" or code[position] == "\r":
            raise ValueError(f"Unclosed string at line {line}")

        position += 1

    if position >= len(code):
        raise ValueError(f"Unclosed string at line {line}")

    text = code[start:position]

    position += 1  # Skip closing quotation mark

    token = Token("STRING", text, line)

    return token, position

def read_operator(code, position, line):

    operator = code[position:position + 2]

    # Check two-character operators first
    if operator in OPERATORS:

        token = Token("OPERATOR", operator, line)

        return token, position + 2

    # Check one-character operators
    operator = code[position]

    if operator == "=":
        token = Token("ASSIGNMENT", operator, line)

    elif operator in OPERATORS:
        token = Token("OPERATOR", operator, line)

    else:
        raise ValueError(
            f"Unknown operator at line {line}: {operator}"
        )

    return token, position + 1

def tokenize(code):

    tokens = []

    position = 0
    line = 1

    while position < len(code):

        char = code[position]

        # 1. Ignore spaces and tabs
        if char in " \t":
            position += 1

        # 2. Handle newlines
        elif char == "\n":

            tokens.append(Token("NEWLINE", None, line))
            position += 1
            line += 1

        # 3. Ignore comments
        elif char == "#":

            while position < len(code) and code[position] not in "\n":
                position += 1

        # 4. Read identifiers
        elif is_letter(char):

            token, position = read_identifier(
                code, position, line
            )

            tokens.append(token)

        # 5. Read numbers
        elif is_digit(char):

            token, position = read_number(
                code, position, line
            )

            tokens.append(token)

        # 6. Read strings
        elif char == '"':

            token, position = read_string(
                code, position, line
            )

            tokens.append(token)

        # 7. Read operators
        elif char in "+-*/%<>=!":

            token, position = read_operator(
                code, position, line
            )

            tokens.append(token)

        # 8. Read special symbols
        elif char in "(),:":

            tokens.append(Token("SYMBOL", char, line))
            position += 1

        # 9. Handle unexpected characters
        else:

            raise ValueError(
                f"Unexpected character at line {line}: {char}"
            )

    tokens.append(Token("EOF", None, line))

    return tokens

print(tokenize("Start:\n\t if health < goto flee"))