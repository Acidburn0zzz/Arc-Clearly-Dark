#!/usr/bin/python3

import os
import sys
import shutil
import re


DIR=os.path.dirname(os.path.realpath(__file__))


def get_css_path():
    os.chdir(DIR)
    for root, dirs, files in os.walk('.'):
        if root.endswith('gnome-shell') and files.contains('gnome-shell.css'):
            css_path = os.path.join(root, 'gnome-shell.css')
            return css_path

    return None


class Block:
    of_value = False
    inject_before = None
    lead = None
    body = None
    inject_after = None

    def __init__(self, hold, of_value):
        self.of_value = of_value
        if len(hold) > 1:
            self.lead = hold[0]
            self.body = hold[1:]
        else:
            self.lead = hold[0]
            self.body = []

    def output(self, f):
        finalized = self.inject_before + [self.lead] \
                    + self.body + self.inject_after
        for line in finalized:
            f.writelines(map(lambda l: l + '\n', finalized))


def tokenizer(css_file):
    hold = []
    in_comment = False
    in_block = None
    for line in css_file:
        hold.append(line)

        if line.strip().startswith('/*'):
            in_comment = True
        elif line.strip().endswith('{'):
            in_block = True

        if in_comment:
            if line.strip().endswith('*/'):
                in_comment = False
                yield Block(hold, of_value=False)
                hold = []
            continue

        if in_block:
            if line.strip().endswith('}'):
                in_block = False
                yield Block(hold, of_value=True)
                hold = []
            continue


def transform_output(tok, out_f):
    lead_map = {re.compile(x) for x in {
        
    }}

    for block in tok:
        
        pass


def main():
    css_path = get_css_path()

    if css_file is None:
        print('Did not find gnome-shell.css. Please be sure you placed '
              'this script in the Arc-Dark theme directory')
        sys.exit(2)


    css_file = open(css_path)
    mod_css_path = css_path + '.mod_clearly.new.css'
    mod_css_file = open(mod_css_path, 'w')

    tok = tokenizer(css_file)

    transform_output(tok, mod_css_file)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exitting.')
