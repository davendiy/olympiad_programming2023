#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Модуль призначено для генерації коду за списком рядків програми, які 
спочатку розбиваються на токени за допомогою `tokenizer.py`.

Генератор коду повертає список команд.
Кожна команда - це кортеж: (<код_команди>, <операнд>)

У подальшому обчислення будуть виконуватись з використанням стеку.
Стек - це список, у який ми можемо додавати до кінця (list.append) 
та брати з кінця числа (list.pop).

Для виконання арифметичної операції буде братись
два останніх числа зі стеку,
обчислювати результат операції та додавати результат до стеку.
Тому генератор повинен згенерувати команди
завантаження змінних та констант до стеку
а також виконання арифметичних операцій та присвоєння.

Допустимі команди:
("LOADC", <число>) - завантажити число у стек
("LOADV", <змінна>) - завантажити значення змінної у стек
                      (використовується `storage.py`)

("ADD", None) - обчислити суму двох верхніх елементів стеку
("SUB", None) - обчислити різницю двох верхніх елементів стеку
("MUL", None) - обчислити добуток двох верхніх елементів стеку
("DIV", None) - обчислити частку від ділення двох верхніх елементів стеку

("SET", <змінна>) - встановити (присвоїти) значення змінної
                    у пам'яті (`storage.py`) рівним
                    значенню останнього елементу стеку

Генерація коду виконується за допомогою рекурсивного розбору виразу.
Вираз (expression) представляється як один доданок (term) або сума/різниця
багатьох доданків.

Доданок (term) представляється як один множник (factor) або добуток
(частка від ділення) багатьох множників.

Множник (factor) представляється як константа або змінна,
або вираз (expression) у дужках.

Під час розбору кожна функція забирає токени зі списку токенів tokens,
а також додає команди до списку команд code
"""

from typing import List

from storage import is_in, clear, add
from tokenizer import get_tokens, Token
from syntax_analyzer import check_assignment_syntax


COMMANDS = [
    "LOADC",
    "LOADV",
    "ADD",
    "SUB",
    "MUL",
    "DIV",
    "SET"
]


def generate_code(program_lines: List[str], clear_storage=True):
    """Функція генерує код за списком рядків програми program_lines

    Повертає програмний код у вигляді списку кортежів
    (<код_команди>, <операнд>)
    
    Також, якщо під час генерації коду або аналізу виникає помилка,
    то повертає текст помилки. Якщо помилки немає, то повертає порожній рядок.
    
    Побічний ефект: очищує пам'ять.
   
    :param program_lines: список рядків програми
    :param clear_storage: флаг, чи очищати пам'ять
    :return: список команд - кортежів (<код_команди>, <операнд>)
    :return: текст помилки
    """
    if clear_storage:
        clear()
    code = []
    err = ''
    for line in program_lines:
        tmp_code, err = _generate_line_code(line)

        if err and err != "Порожній вираз":
            break
        elif err == "Порожній вираз":
            continue
        code += tmp_code

    return code, err


def _generate_line_code(program_line: str):
    """Функція генерує код за рядком програми program_line.

    Рядок програми має бути присвоєнням виду x = e,
    (де x - змінна, e - вираз), або порожнім рядком.
    
    Використовує модулі tokenizer та syntax_analyzer для розбору
    та аналізу правильності синтаксису рядка програми.
    
    Використовує функцію _expression для генерації коду виразу, після чого
    генерує команду SET для змінної з лівої частини присвоєння, та додає
    змінну до пам'яті (storage), якщо потрібно.
    
    Якщо program_line - порожній рядок, то функція його ігнорує.
    
    Повертає програмний код для рядка програми у вигляді списку кортежів
    (<код_команди>, <операнд>)
    
    Також, якщо під час генерації коду або аналізу виникає помилка,
    то повертає текст помилки. Якщо помилки немає, то повертає порожній рядок.
    
    :param program_line: рядок програми
    :return: 
        список команд - кортежів (<код_команди>, <операнд>)
        текст помилки
    """

    tokens = get_tokens(program_line)
    succ, err = check_assignment_syntax(tokens)
    if not succ:
        return [], err

    expression_tokens = tokens[2:]
    code = []
    _expression(code, expression_tokens)

    if not is_in(tokens[0].value):
        add(tokens[0].value)

    code.append(('SET', tokens[0].value))
    return code, err


def _expression(code: list, tokens: List[Token]):
    """Функція генерує код за списком токенів виразу.

    Використовує функцію _term для генерації коду доданку, після чого,
    поки список токенів не спорожніє і поточний токен - це операція
    '+' або '-', знову використовує _term для наступного доданку та
    генерує команду ADD або SUB.
    
    Побічний ефект: змінює список code (додає відповідні команди) 
    та список tokens (видаляє розглянуті токени)
    
    :param code: список команд - кортежів (<код_команди>, <операнд>)
    :param tokens: список токенів
    :return: None
    """
    _term(code, tokens)
    while tokens and tokens[0].value in '+-':
        tok = tokens.pop(0)
        _term(code, tokens)
        if tok.value == "+":
            code.append(("ADD", None))
        else:
            code.append(("SUB", None))


def _term(code: list, tokens: List[Token]):
    """Функція генерує код за списком токенів, що починається токенами доданку.

    Використовує функцію _factor для генерації коду множника, після чого,
    поки список токенів не спорожніє і поточний токен - це операція
    '*' або '/', знову використовує _factor для наступного множника та
    генерує команду MUL або DIV.
    
    Побічний ефект: змінює список code (додає нові команди) 
    та список tokens (видаляє розглянуті токени)
    
    :param code: список команд - кортежів (<код_команди>, <операнд>)
    :param tokens: список токенів
    :return: None
    """
    _factor(code, tokens)
    while tokens and tokens[0].value in "*/":
        tok = tokens.pop(0)
        _factor(code, tokens)
        if tok.value == '*':
            code.append(('MUL', None))
        else:
            code.append(('DIV', None))


def _factor(code: list, tokens: List[Token]):
    """Функція генерує код за списком токенів, що починається токенами множника.

    Якщо перший токен - "left_paren", то множник - це вираз у дужках і треба
    викликати функцію _expression, після чого пропустити праву дужку.

    Якщо перший токен - константа або змінна, то треба згенерувати команду
    LOADC (додатково - перетворити константу з рядка у дійсне число) або
    LOADV (додатково - додати змінну до пам'яті, якщо необхідно).
    
    Побічний ефект: змінює список code (додає нові команди) 
    та список tokens (видаляє розглянуті токени)
    
    :param code: список команд - кортежів (<код_команди>, <операнд>)
    :param tokens: список токенів
    :return: None
    """
    first = tokens.pop(0)

    if first.type == 'left_paren': 
        balance = 1
        exp = []
        while tokens:
            tok = tokens.pop(0) 
            if tok.type == 'left_paren': 
                balance += 1 
            elif tok.type == 'right_paren': 
                balance -= 1 
            
            if balance == 0: 
                break
            exp.append(tok)

        _expression(code, exp)
    
    elif first.type == 'variable': 
        if not is_in(first.value): 
            add(first.value)
        code.append(('LOADV', first.value))
    elif first.type == 'constant': 
        code.append(('LOADC', float(first.value)))


if __name__ == "__main__":
    code0, error = generate_code(["a = b + c", 
                                  "y = (2 - 1"])
    assert error == "Неправильно розставлені дужки"

    code1, error = generate_code(["x = 1",
                                  "z = (((a)))",
                                  "a = b + c * (d - e)",
                                  "y = (2 - 1) * (x345 + 3 * d) / 234.5 - z"])
    needed = [('LOADC', 1.0),
                  ('SET', 'x'),
                  ('LOADV', 'a'),
                  ('SET', 'z'),
                  ('LOADV', 'b'),
                  ('LOADV', 'c'),
                  ('LOADV', 'd'),
                  ('LOADV', 'e'),
                  ('SUB', None),
                  ('MUL', None),
                  ('ADD', None),
                  ('SET', 'a'),
                  ('LOADC', 2.0),
                  ('LOADC', 1.0),
                  ('SUB', None),
                  ('LOADV', 'x345'),
                  ('LOADC', 3.0),
                  ('LOADV', 'd'),
                  ('MUL', None),
                  ('ADD', None),
                  ('MUL', None),
                  ('LOADC', 234.5),
                  ('DIV', None),
                  ('LOADV', 'z'),
                  ('SUB', None),
                  ('SET', 'y')]

    success = not error and code1 == needed 
    if len(code1) != len(needed): 
        print(f"wrong amount of commands: expected {len(needed)}, got {len(code1)}")
    elif not success: 
        for exp, got in zip(needed, code1): 
            if exp != got: 
                print(f'wrong code command: expected {exp}, got {got}')

    assert is_in('a')
    assert is_in('x')

    print("Success =", success)

    code2, error = generate_code(['x = ((_abc + 3.12) * (12 - (3 * 2)))'])

    needed = [
        ('LOADV', '_abc'),
        ('LOADC', 3.12),
        ('ADD', None),
        ('LOADC', 12.0),
        ('LOADC', 3.0),
        ('LOADC', 2.0),
        ('MUL', None),
        ('SUB', None),
        ('MUL', None),
        ('SET', 'x'),
    ]

    success = not error and code2 == needed 
    if len(code2) != len(needed): 
        print(f"wrong amount of commands: expected {len(needed)}, got {len(code2)}")
    elif not success: 
        for exp, got in zip(needed, code2): 
            if exp != got: 
                print(f'wrong code command: expected {exp}, got {got}')

    needed = [
        ('LOADC', 1.0),
        ('LOADC', 2.0),
        ('ADD', None),
        ('LOADC', 3.0),
        ('ADD', None),
        ('LOADC', 4.0),
        ('ADD', None),
        ('LOADC', 3.0),
        ('ADD', None),
        ('SET', 'x'),
    ]

    code3, error = generate_code(['x = 1 + 2 + 3 + 4 + ((((3))))'])
    success = not error and code3 == needed 
    if len(code3) != len(needed): 
        print(f"wrong amount of commands: expected {len(needed)}, got {len(code3)}")
    elif not success: 
        for exp, got in zip(needed, code3): 
            if exp != got: 
                print(f'wrong code command: expected {exp}, got {got}')
