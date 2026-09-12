#!/usr/bin/env python3

from sys import argv, stderr
from os.path import isfile

from pypdf import PdfReader, PdfWriter

from .attachments import attachments_preview, attachments_restore
from .js import js_sanitize


def sanitize_to(src: str, dst: str, files: bool=False):
    reader = PdfReader(src)
    writer = PdfWriter()

    writer = js_sanitize(reader, writer)

    if not files:
        writer = attachments_restore(reader, writer)

    with open(dst, 'wb') as f:
        writer.write(f)


def main():
    try:
        inp, out = argv[1], argv[2]
    except IndexError:
        print(f'Usage: {argv[0]} <input.pdf> <output.pdf>', file=stderr)
        exit(1)

    if not isfile(inp):
        print(f'Error: no such file or directory: {inp}', file=stderr)
        exit(1)

    purge_files = False
    try:
        print('This file has the following attachments:')
        if attachments_preview(inp):
            ans = input('Do you want to purge them? [Y/n] ').lower()
            purge_files = (ans[0] != 'n')
    except Exception as e:
        print(f'Unexpected error while scanning the file for attachments: {e}', file=stderr)
        exit(1)

    print('Sanitizing PDF ...')
    try:
        sanitize_to(inp, out, files=purge_files)
    except Exception as e:
        print(f'Unexpected error while sanitizing the file: {e}', file=stderr)
        exit(1)

    print('Success!')
    exit(0)


if __name__ == '__main__':
    main()
