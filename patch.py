#!/usr/bin/python3

# Copyright 2016 icasdri
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import re


DIR = os.path.dirname(os.path.realpath(__file__))


def get_css_path():
    os.chdir(DIR)
    for root, dirs, files in os.walk('.'):
        if root.endswith('gnome-shell') and 'gnome-shell.css' in files:
            css_path = os.path.join(root, 'gnome-shell.css')
            return css_path

    return None


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

    def get_rules(self):
        return [Rule.parse(x) for x in self.body]

    def update_rules(self, rules):
        self.body = [r.formatted() for r in rules]

    def output(self, f):
        if len(self.body) > 0 and self.of_value:
            if not self.body[-1].rstrip().endswith('}'):
                self.body[-1] = self.body[-1].rstrip('\n') + ' }\n'

        f.writelines(
            self.inject_before + [self.lead] + self.body + self.inject_after
        )

    def __str__(self):
        return '-------Block-------' + \
               '\nlead: ' + self.lead + \
               '\nbody (len): ' + str(len(self.body)) + '\n' + \
               ''.join(self.body)


RULE_RE = re.compile(r'(?P<pre>\s*)(?P<name>[\w-]+):\s*'
                     '(?P<value>.*)\s*;(?P<post>.*}?\s*)')


class RuleParseError(Exception):
    def __init__(self, rule):
        self.message = rule


class Rule:
    @classmethod
    def parse(cls, rule_line):
        m = RULE_RE.match(rule_line)
        if m:
            self = cls()
            self.pre = m.group('pre')
            self.name = m.group('name')
            self.value = m.group('value')
            self.post = m.group('post')
            return self
        else:
            raise RuleParseError(rule_line)
        pass

    def formatted(self):
        return self.pre + self.name + ': ' + self.value + ';' + self.post

    def clone(self):
        x = Rule()
        x.pre = self.pre
        x.name = self.name
        x.value = self.value
        x.post = self.post
        return x


def transform_output(tok, out_f):
    def deletion(b):
        b.clear_given()

    def system_icon(b):
        rules = b.get_rules()
        for r in rules:
            if r.name == 'padding':
                val = r.value.split()
                val[1] = '8px'
                r.value = ' '.join(val)

        b.update_rules(rules)

    def dash_color(b):
        rules = b.get_rules()
        for r in rules:
            if r.name == 'background-color' or r.name == 'border-color':
                r.value = 'transparent'

        b.update_rules(rules)

    def show_apps_norm(b):
        rules = b.get_rules()
        for r in rules:
            if r.name == 'background-color':
                r.value = 'transparent'

        b.update_rules(rules)

    def show_apps_hover(b):
        exc = ('color',)
        rules = list(filter(lambda r: r.name not in exc, b.get_rules()))
        for r in rules:
            if r.name == 'background-color':
                r.value = 'rgba(186, 195, 207, 0.4)'

        b.update_rules(rules)

    def show_apps_active(b):
        exc = ('color', 'box-shadow', 'transition-duration')
        rules = list(filter(lambda r: r.name not in exc, b.get_rules()))
        for r in rules:
            if r.name == 'background-color':
                r.value = '#5294E2'

        b.update_rules(rules)

        x = b.lead.split('\n')
        b.lead = '\n'.join(filter(lambda y: '.show-apps-icon' not in y, x))

    def workspace_thumbs(b):
        exc = ('border-image',)
        rules = list(filter(lambda r: r.name not in exc, b.get_rules()))
        x = rules[0]

        r1 = x.clone()
        r1.name = 'background-color'
        r1.value = 'transparent'
        rules.append(r1)

        r2 = x.clone()
        r2.name = 'border-color'
        r2.value = 'transparent'
        rules.append(r2)

        b.update_rules(rules)

    def workspace_indic(b):
        rules = b.get_rules()
        for r in rules:
            if r.name == 'border':
                vals = r.value.split(' ')
                if 'px' in vals[0]:
                    vals[0] = '3px'
                r.value = ' '.join(vals)

        b.update_rules(rules)

    lead_map = {
        # startwith string,   contains string     OR  False for strict match
        #                   (implies startswith)  OR  True for startwith match
        ('#panel .panel-button .system-status-icon', False): system_icon,
        ('.search-entry:hover', '.search-entry:focus'): deletion,
        ('#dash', False): dash_color,
        ('#dash .app-well-app:hover', True): deletion,
        ('#dash .app-well-app:active', True): deletion,
        ('.show-apps', True): show_apps_norm,
        ('.show-apps:hover', True): show_apps_hover,
        ('.show-apps:active', True): show_apps_active,
        ('.workspace-thumbnails', False): workspace_thumbs,
        ('.workspace-thumbnails:rtl', False): workspace_thumbs,
        ('.workspace-thumbnail-indicator', False): workspace_indic,
    }

    def startswith_special(to_test, s):
        return to_test.startswith(s + ' ') or to_test.startswith(s + ',') or \
               to_test == s

    for block in tok:
        for pat, func in lead_map.items():
            lea = block.lead.strip().rstrip('{').rstrip()

            s, c = pat
            match = False

            if c is False:
                match = (lea == s)
            elif c is True:
                match = startswith_special(lea, s)
            else:
                match = startswith_special(lea, s) and (c in lea)

            if match:
                func(block)
                block.inject_before.insert(
                    0, '/* Arc-Clearly-Dark Customization Begin */\n'
                )
                block.inject_after.append(
                    '/* Arc-Clearly-Dark Customization End */\n'
                )
                break  # proceed to next block

        block.output(out_f)


def main():
    css_path = get_css_path()

    if css_path is None:
        print('Did not find gnome-shell.css. Please be sure you placed '
              'this script in the Arc-Dark theme directory')
        sys.exit(2)

    css_file = open(css_path)
    mod_css_path = css_path + '.mod_clearly'
    mod_css_file = open(mod_css_path, 'w')

    tok = tokenizer(css_file)

    transform_output(tok, mod_css_file)

    base_bak_name = css_path + '.before_mod_clearly'
    if os.path.isfile(base_bak_name):
        for alt_name in (base_bak_name + '.' + str(i) for i in range(1, 100)):
            if not os.path.isfile(alt_name):
                os.rename(css_path, alt_name)
                os.rename(css_path + '.mod_clearly', css_path)
        else:
            print('A hundred different backup .before_mod_clearly files found.'
                  'Giving up on patching as creating more is ridiculous.')
    else:
        os.rename(css_path, base_bak_name)
        os.rename(css_path + '.mod_clearly', css_path)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Exitting.')
