# -*- coding: utf-8 -*-
"""
creolize.py - converter from WikiCreole 1.0 format to XHTML.
"""

import re

MARKUP = {
    '=': {'stag': '<h1>', 'etag': '</h1>\n'},
    '==': {'stag': '<h2>', 'etag': '</h2>\n'},
    '===': {'stag': '<h3>', 'etag': '</h3>\n'},
    '====': {'stag': '<h4>', 'etag': '</h4>\n'},
    '=====': {'stag': '<h5>', 'etag': '</h5>\n'},
    '======': {'stag': '<h6>', 'etag': '</h6>\n'},
    'p': {'stag': '<p>', 'etag': '</p>\n'},
    'verbatim': {'stag': '<pre>', 'etag': '</pre>\n'},
    '----': {'tag': '<hr />\n'},
    '*': {
        'stag': '<ul>\n<li>', 'etag': '</li>\n</ul>\n',
        '*': '</li>\n<li>', '#': '</li>\n</ul>\n<ol>\n<li>',
        ';': '</li>\n</ul>\n<dl>\n<dt>',
        ':': '</li>\n</ul>\n<dl>\n<dd>',
    },
    '#': {
        'stag': '<ol>\n<li>', 'etag': '</li>\n</ol>\n',
        '#': '</li>\n<li>', '*': '</li>\n</ol>\n<ul>\n<li>',
        ';': '</li>\n</ol>\n<dl>\n<dt>',
        ':': '</li>\n</ul>\n<dl>\n<dd>',
    },
    ';':  {
        'stag': '<dl>\n<dt>', 'etag': '</dt>\n</dl>\n',
        ';': '</dt>\n<dt>', ':': '</dt>\n<dd>',
        '*': '</dt>\n</dl>\n<ul>\n<li>',
        '#': '</dt>\n</dl>\n<ol>\n<li>',
    },
    ':':  {
        'stag': '<dl>\n<dd>', 'etag': '</dd>\n</dl>\n',
        ';': '</dd>\n<dt>', ':': '</dd>\n<dd>',
        '*': '</dd>\n</dl>\n<ul>\n<li>',
        '#': '</dd>\n</dl>\n<ol>\n<li>',
    },
    '||': {
        'stag': '<table>\n<tr>', 'etag': '</tr>\n</table>\n',
        '||': '</tr>\n<tr>',
    },
    '|':  {'stag': '<td>', 'etag': '</td>'},
    '|=': {'stag': '<th>', 'etag': '</th>'},
    '>': {
        'stag': '<div style="margin-left:2em">\n', 'etag': '</div>\n',
    },
    '**': {'stag': '<strong>', 'etag': '</strong>'},
    '//': {'stag': '<em>', 'etag': '</em>'},
    '##': {'stag': '<tt>', 'etag': '</tt>'},
    '^^': {'stag': '<sup>', 'etag': '</sup>'},
    ',,': {'stag': '<sub>', 'etag': '</sub>'},
    '__': {'stag': '<span class="underline">', 'etag': '</span>'},
    '\\\\':   {'tag': '<br />\n'},
    'nowiki': {'stag': '<code>', 'etag': '</code>'},
    '<<<': {'stag': '', 'etag': ''},
    'toc': {'stag': '<div class="toc">\n', 'etag': '</div>\n'},
}

# &<>"' : specials for XML/HTML
# {} : specials for python Django Template
# \ : special for javascript
XML_SPECIAL_PATTERN = re.compile(r'''
    (?:([<>"'\\\{\}])
    | \& (?:([a-zA-Z_][a-zA-Z0-9_]*|\#(?:[0-9]{1,5}|x[0-9a-fA-F]{2,4}));)?
    )
''', re.M|re.S|re.X)

XML_STOICK_PATTERN = re.compile(r'''([&<>"'\\\{\}])''', re.M|re.S|re.X)

DJANGO_SPECIAL_PATTERN = re.compile(r'''
    (?:([<>\\\{\}])
    | \& (?:([a-zA-Z_][a-zA-Z0-9_]*|\#(?:[0-9]{1,5}|x[0-9a-fA-F]{2,4}));)?
    )
''', re.M|re.S|re.X)

XML_SPECIAL = {
    '&': '&amp;', '<': '&lt;', '>': '&gt;',
    '"': '&quot;', "'": '&#39;', '\\': '&#92;',
    '{': '&#123;', '}': '&#125;',
}

URI_SPECIAL_PATTERN = re.compile(r'''
    (?: (\%([0-9A-Fa-f]{2})?)
    |   (&(?:amp;)?)
    |   ([^a-zA-Z0-9_~\-.=+\$,:\@/;?\#])
    )
''', re.M|re.S|re.X)

NAME_SPECIAL_PATTERN = re.compile(r'''
    ([^a-zA-Z0-9_.\-:/])
''', re.M|re.S|re.X)

BASE36 = '0123456789abcdefghijklmnopqrstuvwxyz'

WTYPE_NULL = 0
WTYPE_TEXT = 1
WTYPE_STAG = 2
WTYPE_ETAG = 3

TOKEN_PATTERN = re.compile(r'''
    (?: (?P<EOF>\Z)
    |   (?P<EOL>\n)
    |   ^
        (?: (?P<VERBATIM>\{\{\{\n.*?\n\}\}\}\n)
        |   [\x20\t]* (?: (?P<HRULE>-{4,})[\x20\t]*\n
            |   (?P<JUSTLIST>
                    (?:\*(?:(?!\*)|\*{2,})|\#(?:(?!\#)|\#{2,}))[\x20\t]*)
            |   (?P<TD>\|=?)[\x20\t]*
            |   (?P<TERM>\;+)[\x20\t]*
            |   (?P<QUOTE>\>+)[\x20\t]*
            |   (?P<HEADING>=+)[\x20\t]*))
    |   (?P<HEADING1>[\x20\t]*=+)[\x20\t]*(?=\n|\Z)
    |   (?P<MAYBELIST>\*\*|\#\#)
    |   (?P<ENDTR>[\x20\t]*\|)[\x20\t]*(?=\n|\Z)
    |   (?P<TD1>\|=?[\x20\t]*)
    |   (?P<DESC>\:+)
    |   (?P<PHRASE>\/\/|\^\^|,,|__)
    |   (?P<BREAK>\\\\)
    |   (?P<NOWIKI>\{\{\{ .*? \}\}\}+)
    |   (?P<BRACKETED>\[\[ [^\n]*? \]\])
    |   (?P<BRACED>\{\{(?!\{) [^\n]*? \}\})
    |   <<(?:<(?P<PLACEHOLDER>.*?)>>>
        |[\x20\t]*(?P<PLUGIN>.*?)[\x20\t]*>>)
    |   (?P<TEXT1>\{\{+ | \[\[+ | <<+)
    |   \b
        (?P<FREESTAND>https?://(?:[A-Za-z0-9\-._~:/?\#&+,;=]|%[0-9A-Fa-f]{2})+
            (?:[A-Za-z0-9\-_~/\#&+=]|%[0-9A-Fa-f]{2})
        |   ftps?://[A-Za-z0-9\-._\/+]+[A-Za-z0-9\-_\/+])
    |   (?P<ESCAPE>\~
            (?: (?=[\x20\t\r\n])
            |   \*+ | \/\/ | \\\\ | \#+ | \^\^ | ,, | __ | ;+ | \:+ | =+
            |   \[\[[^\r\n]*?\]\] | \{\{(?:(?!\{)[^\r\n]*?\}\}|\{+) | <<+
            |   ----+
            |   https?://(?:[A-Za-z0-9\-._~:/?\#&+,;=]|%[0-9A-Fa-f]{2})+
                (?:[A-Za-z0-9\-_~/\#&+=]|%[0-9A-Fa-f]{2})
            |   ftps?://[A-Za-z0-9\-._/+]+[A-Za-z0-9\-_/+]
            |   .))
    |   (?P<BLANK>[\x20\t]+)
    |   (?P<TEXT>.+?)
        (?= [\x20\t]*
            (?: \Z
            |   [\n~\|:] | \*\* | \#\# | \/\/ | \^\^ | \,\, | \_\_ | \\\\
            |   \{\{ |\[\[ | <<
            |   =+[\x20\t]*(?:\n|\Z)
            |   \b (?:https?://|ftp://)))
    )
''', re.M|re.S|re.X)

# WikiCreolize 1.0 and additions is lied on a regular grammar.
TOKEN_STATE = {
    'EOF': [
        [None], [None, 3], [None, 3], [None, 0], [None, 2], [None, 2],
        [None, 4], [None, 4], [None, 4], [None, 3, 1], [None, 3, 1],
        [None, 2], [None, 2],
    ],
    'EOL': [
        [0], [2, 27], [0, 3], [0, 0], [5, 27], [0, 2], [8], [8], [0, 4],
        [10, 27], [0, 3, 1], [12, 27], [0, 2],
    ],
    'VERBATIM': [
        [0, 20], [0], [0, 3, 20], [0], [0], [0, 2, 20], [0], [0], [0, 4, 20],
        [0], [0, 3, 1, 20], [0], [0, 2, 20],
    ],
    'HRULE': [
        [0, 11], [0], [0, 3, 11], [0], [0], [0, 2, 11], [0], [0], [0, 4, 11],
        [0], [0, 3, 1, 11], [0], [0, 2, 11],
    ],
    'HEADING': [
        [3, 21], [1, 26], [3, 3, 21], [0, 0], [4, 26], [3, 2, 21], [6, 26],
        [0], [3, 4, 21], [9, 26], [3, 3, 1, 21], [11, 26], [3, 2, 21],
    ],
    'HEADING1': [
        [3, 21], [1, 26], [3, 3, 21], [0, 0], [4, 26], [3, 2, 21], [6, 26],
        [0], [3, 4, 21], [9, 26], [3, 3, 1, 21], [11, 26], [3, 2, 21],
    ],
    'JUSTLIST': [
        [4, 23], [0], [4, 3, 23], [0], [0], [4, 13], [0], [0], [4, 4, 23],
        [0], [4, 3, 1, 23], [0], [4, 13],
    ],
    'MAYBELIST': [
        [1, 24, 15], [1, 15], [1, 15], [3, 15], [4, 15], [4, 13], [6, 15],
        [0], [1, 4, 24, 15], [9, 15], [10, 15], [11, 15], [4, 13],
    ],
    'TD': [
        [6, 25], [1, 26], [6, 3, 25], [3, 26], [4, 26], [6, 2, 25], [6, 18],
        [0], [6, 19], [9, 26], [6, 3, 1, 25], [11, 26], [6, 2, 25],
    ],
    'TD1': [
        [6, 25], [1, 26], [6, 3, 25], [3, 26], [4, 26], [6, 2, 25], [6, 18],
        [0], [6, 19], [9, 26], [6, 3, 1, 25], [11, 26], [6, 2, 25],
    ],
    'ENDTR': [
        [0], [1, 26], [0], [3, 26], [4, 26], [0], [7], [0], [0], [9, 26], [0],
        [11, 26], [0],
    ],
    'TERM': [
        [11, 23], [0], [11, 3, 23], [0], [0], [11, 13], [0], [0], [11, 4, 23],
        [0], [11, 3, 1, 23], [0], [11, 13],
    ],
    'DESC': [
        [9, 22, 24], [1, 26], [9, 3, 22, 24], [3, 26], [4, 26], [4, 13],
        [6, 26], [0], [9, 4, 22, 24], [9, 26], [9, 3, 12, 24], [4, 8],
        [4, 13],
    ],
    'QUOTE': [
        [9, 22, 24], [0], [9, 3, 22, 24], [0], [0], [9, 2, 22, 24], [0], [0],
        [9, 4, 22, 24], [0], [9, 3, 12, 24], [0], [9, 2, 22, 24],
    ],
    'BLANK': [
        [0], [1, 27], [2], [3, 27], [4, 27], [5], [6, 27], [0], [8], [9, 27],
        [10], [11, 27], [12],
    ],
    'PHRASE': [
         [1, 24, 15], [1, 15], [1, 15], [3, 15], [4, 15], [4, 15],
         [6, 15], [15], [1, 4, 24, 15], [9, 15], [9, 15], [11, 15],
         [11, 15],
    ],
    'BREAK': [
         [1, 24, 5], [1, 5], [1, 5], [3, 5], [4, 5], [4, 5],
         [6, 5], [5], [1, 4, 24, 5], [9, 5], [9, 5], [11, 5],
         [11, 5],
    ],
    'NOWIKI': [
         [1, 24, 14], [1, 14], [1, 14], [3, 14], [4, 14], [4, 14],
         [6, 14], [14], [1, 4, 24, 14], [9, 14], [9, 14], [11, 14],
         [11, 14],
    ],
    'BRACKETED': [
         [1, 24, 7], [1, 7], [1, 7], [3, 7], [4, 7], [4, 7],
         [6, 7], [7], [1, 4, 24, 7], [9, 7], [9, 7], [11, 7],
         [11, 7],
    ],
    'BRACED': [
         [1, 24, 6], [1, 6], [1, 6], [3, 6], [4, 6], [4, 6],
         [6, 6], [6], [1, 4, 24, 6], [9, 6], [9, 6], [11, 6],
         [11, 6],
    ],
    'PLACEHOLDER': [
         [1, 24, 16], [1, 16], [1, 16], [3, 16], [4, 16], [4, 16],
         [6, 16], [16], [1, 4, 24, 16], [9, 16], [9, 16], [11, 16],
         [11, 16],
    ],
    'PLUGIN': [
         [1, 24, 17], [1, 17], [1, 17], [3, 17], [4, 17], [4, 17],
         [6, 17], [17], [1, 4, 24, 17], [9, 17], [9, 17], [11, 17],
         [11, 17],
    ],
    'FREESTAND': [
         [1, 24, 10], [1, 10], [1, 10], [3, 10], [4, 10], [4, 10],
         [6, 10], [10], [1, 4, 24, 10], [9, 10], [9, 10], [11, 10],
         [11, 10],
    ],
    'ESCAPE': [
         [1, 24, 9], [1, 9], [1, 9], [3, 9], [4, 9], [4, 9],
         [6, 9], [9], [1, 4, 24, 9], [9, 9], [9, 9], [11, 9],
         [11, 9],
    ],
    'TEXT': [
         [1, 24, 26], [1, 26], [1, 26], [3, 26], [4, 26], [4, 26],
         [6, 26], [26], [1, 4, 24, 26], [9, 26], [9, 26], [11, 26],
         [11, 26],
    ],
    'TEXT1': [
         [1, 24, 26], [1, 26], [1, 26], [3, 26], [4, 26], [4, 26],
         [6, 26], [26], [1, 4, 24, 26], [9, 26], [9, 26], [11, 26],
         [11, 26],
    ],
}

class Creolize:

    def __init__(self):
        self.type = 'xhtml'
        self.script_name = 'http://example.net/wiki/'
        self.static_location = 'http://example.net/static/'
        self.link_visitor = None
        self.plugin_visitor = None
        self.plugin_running = False
        self.toc = 0
        self.tocinfo = []
        self.dispatch_table = [
            self._end_heading,
            self._end_indent,
            self._end_list,
            self._end_paragraph,
            self._end_table,
            self._insert_br,
            self._insert_braced,
            self._insert_bracketed,
            self._insert_colon,
            self._insert_escaped,
            self._insert_freestand,
            self._insert_hr,
            self._insert_indent,
            self._insert_list,
            self._insert_nowiki,
            self._insert_phrase,
            self._insert_placeholder,
            self._insert_plugin,
            self._insert_td,
            self._insert_tr,
            self._insert_verbatim,
            self._start_heading,
            self._start_indent,
            self._start_list,
            self._start_paragraph,
            self._start_table,
            self.put,
            self.puts,
        ]

    def convert(self, wiki_source):
        self._init_generator()
        for (data, action_list) in self.scaniter(wiki_source):
            for i in action_list:
                self.dispatch_table[i](data)
        if self.toc and len(self.tocinfo) >= self.toc:
            toc = self._list_toc().result
            self.result = toc + self.result
        return self

    def visit_link(self, link, text, builder):
        anchor = {}
        if re.search(r'(?i)script:', link):
            return anchor
        if not re.match(r'(?:(?:f|ht)tps?://|\#)', link):
            link = builder.script_name + link
            if builder.type == 'django':
                anchor['djangotag'] = 'wiki_link'
        anchor['href'] = link
        anchor['text'] = text
        return anchor

    def visit_image(self, link, title, builder):
        image = {}
        if re.search(r'(?i)script:', link):
            return image
        if not re.match(r'https?://', link):
            link = builder.static_location + link
        image['src'] = link
        image['alt'] = title
        return image

    def visit_plugin(self, data, builder):
        plugin = {}
        if builder.type == 'django':
            plugin['djangotag'] = 'wiki_plugin ' + data
        return plugin

    def scaniter(self, wiki_source):
        wiki_source = re.sub(r"(?:\r\n?|\n)", "\n", wiki_source)
        wiki_source = wiki_source.rstrip("\n") + "\n"
        state = 0
        for m in TOKEN_PATTERN.finditer(wiki_source):
            if state is None:
                break
            token_kind = m.lastgroup
            data = m.groupdict()[m.lastgroup]
            succ = TOKEN_STATE[token_kind][state]
            actions = succ[1:]
            if len(actions) > 0:
                yield (data, actions)
            state = succ[0]

    def _init_generator(self):
        self.prev_wtype = WTYPE_NULL
        self.blank = ''
        self.result = ''
        self.list = []
        self._clear_phrase()

    def _start_block(self, mark):
        self.result += self.blank + MARKUP[mark]['stag']
        self.blank = ''
        self.prev_wtype = WTYPE_STAG
        self._clear_phrase()

    def _end_block(self, mark):
        self._flush_phrase()
        self.result += MARKUP[mark]['etag']
        self.blank = ''
        self.prev_wtype = WTYPE_ETAG

    def _put_markup(self, mark, kind):
        if kind != 'stag':
            self.blank = ''
        self.result += self.blank + MARKUP[mark][kind]
        self.blank = ''
        self.prev_wtype = WTYPE_ETAG if kind == 'etag' else WTYPE_STAG

    def put(self, data):
        self.result += self.blank + self.escape_text(data)
        self.blank = ''
        self.prev_wtype = WTYPE_TEXT
        return self

    def put_xml(self, data):
        self.result += self.blank + self.escape_xml(data)
        self.blank = ''
        self.prev_wtype = WTYPE_TEXT
        return self

    def put_raw(self, data):
        self.result += self.blank + data
        self.blank = ''
        self.prev_wtype = WTYPE_TEXT
        return self

    def puts(self, data):
        self.blank = ''
        if data == '':
            self.result += '\n'
            self.prev_wtype = WTYPE_NULL
        elif self.prev_wtype == WTYPE_TEXT:
            c = ord(self.result[-1])
            if c >= 0x21 and c <= 0x7e:
                self.blank = ' '
        elif self.prev_wtype == WTYPE_ETAG:
            self.blank = ' '
        return self

    def escape_xml(self, s):
        def repl(m):
            return XML_SPECIAL[m.group(1)];
        return XML_STOICK_PATTERN.sub(repl, s)

    def escape_text(self, s):
        def repl(m):
            if m.group(1):
                return XML_SPECIAL[m.group(1)]
            elif m.group(2):
                return '&' + m.group(2) + ';'
            return '&amp;'
        return XML_SPECIAL_PATTERN.sub(repl, s)

    def escape_uri(self, uri):
        def repl(m):
            if m.group(2):
                return m.group(1)
            elif m.group(1):
                return '%25'
            elif m.group(3):
                return '&amp;'
            else:
                return ('%%%02X' % ord(m.group(4)))
        return URI_SPECIAL_PATTERN.sub(repl, uri.encode('utf_8'))

    def escape_name(self, name):
        def repl(m):
            return ('%%%02X' % ord(m.group(1)))
        return NAME_SPECIAL_PATTERN.sub(repl, name.encode('utf_8'))

    def escape_django(self, s):
        def repl(m):
            if m.group(1):
                return XML_SPECIAL[m.group(1)]
            elif m.group(2):
                return '&' + m.group(2) + ';'
            return '&amp;'
        return XML_SPECIAL_PATTERN.sub(repl, s)

    def hash_base36(self, text):
        x = hash(text.encode('utf_8'))
        b36 = ''
        for e in [2176782336, 60466176, 1679616, 46656, 1296, 36, 1]:
            b36 = b36 + BASE36[x / e]
            x = x % e
        return b36

    # BLOCK

    def _start_paragraph(self, data):
        self._start_block('p')

    def _end_paragraph(self, data):
        self._end_block('p')

    def _start_heading(self, data):
        self.heading = data[0:6]
        self.heading_pos = len(self.result)
        self._start_block(self.heading)

    def _end_heading(self, data):
        """ '= heading =\n' """
        mark = self.heading
        self._end_block(mark)
        self.heading = None
        if not self.toc:
            return
        i = self.result.find('<h', self.heading_pos) + 3
        if i < 3:
            return
        text = self.result[self.heading_pos:].rstrip('\n')
        text = re.sub(r'<.*?>', '', text)
        if len(text) == 0:
            return
        hid = 'h' + self.hash_base36(text)
        self.result = self.result[:i] + ' id="' + hid + '"' + self.result[i:]
        self.tocinfo.append([len(mark), hid, text])

    def _list_toc(self):
        toc = self.__class__()
        toc._init_generator()
        if not self.toc:
            return toc
        toc._put_markup('toc', 'stag')
        for info in self.tocinfo:
            toc._insert_list('*' * info[0])
            toc._insert_link(info[2], '#' + info[1], info[2])
        toc._end_list('')
        toc._put_markup('toc', 'etag')
        return toc

    def _start_indent(self, data):
        """ ': indented paragraph', '> and also' """
        self.indent = 0
        self._insert_indent(data)

    def _insert_indent(self, data):
        data = data.replace(' ', '')
        level = len(data)
        step = level - self.indent
        tag_kind = 'stag' if step > 0 else 'etag'
        for x in range(abs(step)):
            self._put_markup('>', tag_kind)
        self.indent = level

    def _end_indent(self, data):
        self._insert_indent('')

    def _start_list(self, data):
        self.list = []
        self._clear_phrase()
        self._insert_list(data)

    def _insert_colon(self, data):
        self._insert_list(':' * self.list[-1][0])

    def _insert_list(self, data):
        """
        list: '* ul', '# ol', '; dl dt', ': dl dd'
        """
        self._flush_phrase()
        mark = data.replace(' ', '')
        level = len(mark)
        mark = mark[0]
        while len(self.list) > 1 and level < self.list[-1][0]:
            if self.list[-2][0] < level:
                self.list[-1][0] = level
                break
            e = self.list.pop()
            self._put_markup(e[1], 'etag')
        if len(self.list) == 0:
            self._put_markup(mark, 'stag')
            self.list.append([level, mark])
        elif self.list[-1][0] < level:
            prev = self.list[-1][1]
            if prev == ';' and (mark == '*' or mark == '#'):
                self._put_markup(';', ':')
                self.list[-1][1] = ':'
            self.puts('')
            self._put_markup(mark, 'stag')
            self.list.append([level, mark])
        else:
            prev = self.list[-1][1]
            self._put_markup(prev, mark)
            self.list[-1][0] = level
            self.list[-1][1] = mark
        self._clear_phrase()

    def _end_list(self, data):
        self._flush_phrase()
        while len(self.list) > 0:
            e = self.list.pop()
            self._put_markup(e[1], 'etag')
        self.list = []

    def _start_table(self, data):
        """ '|table|data|\n' """
        self._put_markup('||', 'stag')
        self.table = re.match(r'(\|=?)', data).group(1)
        self._start_block(self.table)

    def _insert_tr(self, data):
        self._end_block(self.table)
        self._put_markup('||', '||')
        self.table = re.match(r'(\|=?)', data).group(1)
        self._start_block(self.table)

    def _insert_td(self, data):
        """ '| td |= th | """
        self._end_block(self.table)
        self.table = re.match(r'(\|=?)', data).group(1)
        self._start_block(self.table)

    def _end_table(self, data):
        self._end_block(self.table)
        self._put_markup('||', 'etag')
        self.table = None

    def _insert_hr(self, data):
        """ horizontal rule """
        self._put_markup('----', 'tag')

    def _insert_verbatim(self, data):
        """  '\n{{{\n block level verbatim \n}}}\n' """
        data = re.match(r'(?s)\{\{\{\n(.*?)[\x20\t]*\n\}\}\}\n\Z', data).group(1)
        data = re.sub(r'(?m)^\x20\}\}\}', '}}}', data)
        self._put_markup('verbatim', 'stag')
        self.put_xml(data)
        self._put_markup('verbatim', 'etag')

    # INLINE

    def _clear_phrase(self):
        self.phrase = set()
        self.phrase_stack = []

    def _insert_phrase(self, mark):
        """ _insert_phrase: bold("**"), italic("//"),
            monospace("##"), superscript("^^"), subscript(",,"),
            underline("__")
        """
        if mark not in self.phrase:
            self.phrase.add(mark)
            self.phrase_stack.append(mark)
            self._put_markup(mark, 'stag')
        elif len(self.phrase_stack) > 0 and self.phrase_stack[-1] == mark:
            self.phrase.remove(mark)
            self.phrase_stack.pop()
            self._put_markup(mark, 'etag')
        else:
            self.put(mark)

    def _flush_phrase(self):
        if self.phrase_stack is None:
            return
        while len(self.phrase_stack) > 0:
            mark = self.phrase_stack.pop()
            self._put_markup(mark, 'etag')
        self.phrase = set()

    def _insert_br(self, data):
        self._put_markup('\\\\', 'tag')

    def _insert_freestand(self, data):
        """ freestand links: url """
        self._insert_link(data, data, data)

    def _insert_bracketed(self, data):
        """ links: '[[ url | description ]]' """
        m = re.match(r'''(?msx)
            \[\[ [\x20\t]*
            ([^\|]*?) [\x20\t]*
            (?: \| [\x20\t]* (.*?) [\x20\t]* )?
            \]\]\Z
        ''', data)
        if not m:
            self.put(data)
            return
        (url, desc) = m.groups()
        if desc is None:
            desc = url
        self._insert_link(data, url, desc)

    def _insert_braced(self, data):
        """  images: "{{ url | description }}" """
        m = re.match(r'''(?msx)
            \{\{ [\x20\t]*
            ([^\|]*?) [\x20\t]*
            (?: \| [\x20\t]* (.*?) [\x20\t]* )?
            \}\}\Z
        ''', data)
        if not m:
            self.put(data)
            return
        (link, title) = m.groups()
        if title is None:
            title = ''
        visitor = self.link_visitor;
        if not visitor:
            visitor = self
        image = visitor.visit_image(link, title, self)
        if 'src' not in image:
            self.put(data)
            return
        attr = ' src="' + self.escape_uri(image['src']) + '"'
        for k in ['id', 'class', 'alt', 'title']:
            if k in image:
                value = self.escape_text(image[k])
                attr += ' ' + k + '="' + value + '"'
        self.put_raw('<img' + attr + ' />')

    def _insert_link(self, source, link, text):
        visitor = self.link_visitor;
        if not visitor:
            visitor = self
        anchor = visitor.visit_link(link, text, self)
        if 'name' not in anchor and 'href' not in anchor:
            self.put(source)
            return
        t = ''
        if 'before' in anchor:
            t += anchor['before']
        if 'djangotag' in anchor:
            t += '{% ' + anchor['djangotag'] + ' '
            t += "'" + self.escape_uri(link) + "',"
            t += "'" + self.escape_text(text) + "'"
            t += ' %}'
        else:
            attr = ''
            if 'href' in anchor:
                href = anchor['href']
                attr += ' href="' + self.escape_uri(href) + '"'
            for k in ['id', 'name', 'rel', 'rev', 'title']:
                if k in anchor:
                    value = self.escape_text(anchor[k])
                    attr += ' ' + k + '="' + value + '"'
            t += '<a' + attr + '>' + self.escape_text(anchor['text']) + '</a>'
        if 'after' in anchor:
            t += anchor['after']
        self.put_raw(t)

    def _insert_plugin(self, source):
        """ '<< plugin calls >>' """
        if self.plugin_running:
            return
        self.plugin_running = True
        try:
            visitor = self.plugin_visitor;
            if not visitor:
                visitor = self
            plugin = visitor.visit_plugin(source, self)
            if not plugin:
                pass
            elif 'djangotag' in plugin:
                t = self.escape_django(plugin['djangotag'])
                self.put_raw('{% ' + t + ' %}')
            elif 'django' in plugin:
                t = self.escape_django(plugin['django'])
                self.put_raw('{{ ' + t + ' }}' )
            elif 'text' in plugin:
                self.put(plugin['text'])
            elif 'xml' in plugin:
                self.put_xml(plugin['xml'])
            elif 'html' in plugin:
                self.put_xml(plugin['html'])
            elif 'content' in plugin:
                self.put_raw(plugin['content'])
        finally:
            self.plugin_running = False

    def _insert_escaped(self, data):
        """ '~escape', '~~' as '~' itself """
        if len(data) == 1:
            self.put(data)
        else:
            self.put(data[1:])

    def _insert_nowiki(self, data):
        """ '{{{ inline nowiki }}}' """
        data = re.match(
            r'(?s)\{\{\{[\x20\t]*(.*?)[\x20\t]*\}\}\}\Z', data).group(1)
        self._put_markup('nowiki', 'stag')
        self.put_xml(data)
        self._put_markup('nowiki', 'etag')

    def _insert_placeholder(self, data):
        """ '<<< placeholder >>>' """
        self._put_markup('<<<', 'stag')
        self.put_xml(data.strip(' \r\n'))
        self._put_markup('<<<', 'etag')

