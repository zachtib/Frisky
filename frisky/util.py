from typing import Tuple, List


def sanitize(string: str) -> str:
    string = string.replace('“', '"').replace('”', '"')
    return string


def quotesplit(string: str, separators: Tuple[chr] = (' ', '\t'), groupers: Tuple[chr] = ('"',)) -> List[str]:
    """
    Split the input string, string, into a list of substrings while respecting nested grouping of strings
    :param string: The string to split
    :param separators: A tuple of characters that define the boundaries of substrings
    :param groupers: A tuple of characters that define "groupers" which will allow substrings to contain
        separator characters without being broken apart
    :return: a list of substrings
    """
    intersection = [value for value in separators if value in groupers]
    if len(intersection) > 0:
        raise ValueError(f'No characters can be shared between separators and groupers: {intersection}')

    string = sanitize(string)

    result: List[str] = []
    stack: List[chr] = []
    substring: str = ""

    def add_token(token: str):
        if token.startswith('@'):
            token = token.lstrip('@')
        result.append(token)

    for character in string:
        if character in separators:
            if len(stack) == 0:
                if len(substring) > 0:
                    add_token(substring)
                    substring = ''
            else:
                substring += character
        elif character in groupers:
            if len(stack) == 0:
                stack.append(character)
            else:
                if stack[-1] == character:
                    stack.pop()
                    if len(stack) == 0:
                        add_token(substring)
                        substring = ''
                    else:
                        substring += character
                else:
                    stack.append(character)
                    substring += character
        else:
            substring += character

    if len(substring) > 0:
        add_token(substring)

    return result
