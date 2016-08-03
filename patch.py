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
        if len(self.body) > 0:
            if not self.body[-1].rstrip().endswith('}'):
                self.body[-1] = self.body[-1].rstrip('\n') + ' }\n'

        # finalized = ['/* Arc-Clearly-Dark Customization Begin */\n'] + \
        #             self.inject_before + [self.lead] + \
        #             self.body + self.inject_after + \
        #             ['/* Arc-Clearly-Dark Customization End */\n']

        f.writelines(
            self.inject_before + [self.lead] + self.body + self.inject_after
        )

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


RULE_RE = re.compile(r'(?P<pre>\s*)(?P<name>[\w-]+):\s*'
                     '(?P<value>.*)\s*;(?P<post>.*}?\s*)')


class RuleParseError(Exception):
    def __init__(self, rule):
        self.message = rule


class Rule:
    def __init__(self, rule_line):
        m = RULE_RE.match(rule_line)
        if m:
            self.pre = m.group('pre')
            self.name = m.group('name')
            self.value = m.group('value')
            self.post = m.group('post')
        else:
            raise RuleParseError(rule_line)

    def formatted(self):
        return self.pre + self.name + ': ' + self.value + ';' + self.post


def transform_output(tok, out_f):
    def deletion(m, b):
        print(b)
        b.clear_given()
        print('ABOVE BLOCK DELETED')

    def system_icon(m, b):
        rules = [Rule(x) for x in b.body]
        for r in rules:
            if r.name == 'padding':
                val = r.value.split()
                val[1] = '8px'
                r.value = ' '.join(val)

        b.body = [r.formatted() for r in rules]

    def dash_color(m, b):
        rules = [Rule(x) for x in b.body]
        for r in rules:
            if r.name == 'background-color' or r.name == 'border-color':
                r.value = 'transparent'

        b.body = [r.formatted() for r in rules]

    def show_apps_norm(m, b):
        rules = [Rule(x) for x in b.body]
        for r in rules:
            if r.name == 'background-color':
                r.value = 'transparent'

        b.body = [r.formatted() for r in rules]

    def show_apps_hover(m, b):
        exc = ('color',)
        rules = list(filter(lambda r: r.name not in exc,
                            [Rule(x) for x in b.body]))
        for r in rules:
            if r.name == 'background-color':
                r.value = 'rgba(186, 195, 207, 0.4)'

        b.body = [r.formatted() for r in rules]

    def show_apps_active(m, b):
        exc = ('color', 'box-shadow', 'transition-duration')
        rules = list(filter(lambda r: r.name not in exc,
                            [Rule(x) for x in b.body]))
        for r in rules:
            if r.name == 'background-color':
                r.value = '#5294E2'

        b.body = [r.formatted() for r in rules]

        x = b.lead.split('\n')
        b.lead = '\n'.join(filter(lambda y: '.show-apps-icon' not in y, x))

    def workspace_thumbs(m, b):
        pass

    def workspace_thumbs_rtl(m, b):
        pass

    def workspace_indic(m, b):
        pass

    lead_map = {re.compile('\s*' + k): v for k, v in {
        r'#panel \.panel-button \.system-status-icon\s*{':
            system_icon,
        r'\.search-entry:hover.*\.search-entry:focus.*{':
            deletion,
        r'#dash\s*{':
            dash_color,
        r'#dash .app-well-app:hover[\S\s]*{':
            deletion,
        r'#dash .app-well-app:active[\S\s]*{':
            deletion,
        r'\.show-apps.*{':
            show_apps_norm,
        r'\.show-apps:hover.*{':
            show_apps_hover,
        r'\.show-apps:active[\S\s]*{':
            show_apps_active
    }.items()}

    for block in tok:
        # print(block.lead)
        for pat, func in lead_map.items():
            match = pat.match(block.lead)
            if match:
                func(match, block)
                block.output(out_f)
                break  # proceed to next block

        if match:
            if func is not deletion:
                del lead_map[pat]


def main():
    css_path = get_css_path()

    if css_path is None:
        print('Did not find gnome-shell.css. Please be sure you placed '
              'this script in the Arc-Dark theme directory')
        sys.exit(2)

    css_file = open(css_path)
    # mod_css_path = css_path + '.mod_clearly.new.css'
    # mod_css_file = open(mod_css_path, 'w')

    tok = tokenizer(css_file)

    # for block in tok:
        # print(block)
        # # block.output(mod_css_file)

    # transform_output(tok, mod_css_file)
    transform_output(tok, sys.stdout)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exitting.')
