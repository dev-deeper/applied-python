#!/usr/bin/python -i
# -*- coding: utf-8 -*-

import argparse
import sys
import re

# Конвертации поддерживаемых специальных символов в формат RegExp
re_match = {
    '*': '.*',
    '?': '.'
}


def print_line(idx, char, line, params):
    """Отправка строки на печать с номером строки или без"""
    out_str = ''
    if params.line_number:
        out_str = str(idx + 1) + char
    output(out_str + line)


def output(line):
    """Вывод строки на экран"""
    print(line)


def match_line(line, params):
    """Проверка строки на соответствие паттерну"""
    r_value = bool(re.search(params.pattern, line, re.IGNORECASE if params.ignore_case else 0))

    if params.invert:
        r_value = not r_value

    return r_value


def grep(lines, params):
    # Конвертирование паттерна в формат RegExp
    for char in re_match:
        if char in params.pattern:
            params.pattern = params.pattern.replace(char, re_match[char])

    count = 0  # count - подсчёт числа совпадений (флаг -c)
    prev_lines = []  # Буфер строк, предшествующих совпавшей в before context
    prev_firstline_idx = -1  # Индекс строки, находящейся в начале буфера в before context
    last_printed = -1  # последняя напечатанная строка для context'ов
    to_print = 0  # число строк для вывода в after context

    if params.context:
        params.before_context = params.before_context if params.before_context else params.context
        params.after_context = params.after_context if params.after_context else params.context

    for line_idx, line in enumerate(lines):
        line = line.rstrip()

        match = match_line(line, params)

        if match:
            # Вычисление числа строк, удовлетворяющих паттерну
            if params.count:
                count += 1
                continue

            if params.before_context:
                if last_printed != -1 and prev_lines and prev_firstline_idx - last_printed > 1:
                    output("--")

                # Вывод предшествующих строк
                if line_idx - last_printed > 1:
                    for prev_line in prev_lines:
                        print_line(prev_firstline_idx, '-', prev_line, params)
                        prev_firstline_idx += 1
                    prev_lines.clear()
                print_line(line_idx, ':', line, params)
                last_printed = line_idx

            if params.after_context:
                if last_printed != -1 and line_idx - last_printed > 1:
                    output("--")
                if not params.before_context:
                    print_line(line_idx, ':', line, params)
                    last_printed = line_idx
                to_print = params.after_context

            if not (params.before_context or params.after_context):
                print_line(line_idx, ':', line, params)
        else:
            if params.before_context:
                prev_lines.append(line)
                if len(prev_lines) == 1:
                    prev_firstline_idx = line_idx

                if len(prev_lines) > params.before_context:
                    prev_firstline_idx += 1
                    prev_lines.pop(0)

            if params.after_context and to_print > 0:
                    # Печатаем текущую строку в after_context
                    # И удаляем её из буфера before_context
                    if params.before_context:
                        prev_lines.pop()
                    print_line(line_idx, '-', line, params)
                    last_printed = line_idx
                    to_print -= 1

    # end of for

    if params.count:
        output(str(count))


def parse_args(args):
    parser = argparse.ArgumentParser(description='This is a simple grep on python')
    parser.add_argument(
        '-v', action="store_true", dest="invert", default=False, help='Selected lines are those not matching pattern.')
    parser.add_argument(
        '-i', action="store_true", dest="ignore_case", default=False, help='Perform case insensitive matching.')
    parser.add_argument(
        '-c',
        action="store_true",
        dest="count",
        default=False,
        help='Only a count of selected lines is written to standard output.')
    parser.add_argument(
        '-n',
        action="store_true",
        dest="line_number",
        default=False,
        help='Each output line is preceded by its relative line number in the file, starting at line 1.')
    parser.add_argument(
        '-C',
        action="store",
        dest="context",
        type=int,
        default=0,
        help='Print num lines of leading and trailing context surrounding each match.')
    parser.add_argument(
        '-B',
        action="store",
        dest="before_context",
        type=int,
        default=0,
        help='Print num lines of trailing context after each match')
    parser.add_argument(
        '-A',
        action="store",
        dest="after_context",
        type=int,
        default=0,
        help='Print num lines of leading context before each match.')
    parser.add_argument('pattern', action="store", help='Search pattern. Can contain magic symbols: ?*')
    return parser.parse_args(args)


def main():
    params = parse_args(sys.argv[1:])
    grep(sys.stdin.readlines(), params)


if __name__ == '__main__':
    main()
