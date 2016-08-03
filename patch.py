#!/usr/bin/python3

import os
import sys
# import shutil
import re


DIR = os.path.dirname(os.path.realpath(__file__))


def get_css_path():
    os.chdir(DIR)
    for root, dirs, files in os.walk('.'):
        if root.endswith('gnome-shell') and 'gnome-shell.css' in files:
            css_path = os.path.join(root, 'gnome-shell.css')
            return css_path

    return None


class Block:
    of_value = False
    inject_before = []
    lead = None
    body = None
    inject_after = []

    def __init__(self, hold, of_value):
        self.of_value = of_value
        if len(hold) > 1:
            self.lead = hold[0]
            self.body = hold[1:]
        else:
            self.lead = hold[0]
            self.body = []

    def clear_given(self):
        self.lead = ''
        self.body = []

    def output(self, f):
        # finalized = ['/* Arc-Clearly-Dark Customization Begin */\n'] + \
                    # self.inject_before + [self.lead] + \
                    # self.body + self.inject_after + \
                    # ['/* Arc-Clearly-Dark Customization End */\n']
        finalized = self.inject_before + [self.lead] + \
                    self.body + self.inject_after
        f.writelines(finalized)

    def __str__(self):
        return '-------Block-------' + \
               '\nlead: ' + self.lead + \
               '\nbody (len): ' + str(len(self.body)) + '\n' + \
               ''.join(self.body)


def tokenizer(css_file):
    hold = []
    in_comment = False
    in_block = None
    for line in css_file:
        hold.append(line)

        if line.strip().startswith('/*'):
            in_comment = True
        elif line.strip().endswith('{'):
            hold = [''.join(hold)]
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
    def system_icon(m, b):
        # looking for -- padding: 0 4px;
        r = re.compile(r'(padding:\s+\d+\w*)\s*\d+\w*;')
        for i, l in enumerate(b.body):
            b.body[i] = r.sub(r'\1 8px;', l)

    def search_entry_deletion(m, b):
        b.clear_given()

    def dash_color(m, b):
        print('DASH COLOR')
        r1 = re.compile(r'(background-color:)\s*;')
        r2 = re.compile(r'(border-color:)\s*;')
        for i, l in enumerate(b.body):
            x = r1.sub(r'\1 transparent;', l)
            b.body[i] = r2.sub(r'\1 transparent;', x)

    def dash_appwell_addition(m, b):
        pass

    def show_apps_norm(m, b):
        pass

    def show_apps_hover(m, b):
        pass

    def show_apps_active(m, b):
        pass

    def workspace_thumbs(m, b):
        pass

    def workspace_thumbs_rtl(m, b):
        pass

    def workspace_indic(m, b):
        pass

    lead_map = {re.compile(k): v for k, v in {
        r'\s*#panel \.panel-button \.system-status-icon\s*{':
            system_icon,
        r'\s*\.search-entry:hover.*\.search-entry:focus.*{':
            search_entry_deletion,
        r'#dash {':
            dash_color
    }.items()}

    for block in tok:
        # print(block.lead)
        for pat, func in lead_map.items():
            match = pat.match(block.lead)
            if match:
                func(match, block)
                block.output(out_f)
                continue  # proceed to next block


def main():
    css_path = get_css_path()

    if css_path is None:
        print('Did not find gnome-shell.css. Please be sure you placed '
              'this script in the Arc-Dark theme directory')
        sys.exit(2)

    css_file = open(css_path)
    mod_css_path = css_path + '.mod_clearly.new.css'
    mod_css_file = open(mod_css_path, 'w')

    tok = tokenizer(css_file)

    for block in tok:
        if block.lead is None or len(block.lead.strip()) == 0:
            print(block)
        block.output(mod_css_file)

    # transform_output(tok, mod_css_file)
    # transform_output(tok, sys.stdout)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exitting.')
