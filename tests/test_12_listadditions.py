import unittest
import re
import difflib
import creolize

SPEC = r"""
.test definition list
.sect input
; First title of definition list
: Definition of first item.
; Second title: Second definition
beginning on the same line.
; Third title::
Third definition here: show prev colon.
:: And this also 3rd one.
: Obcource this is.
continue line.
; final : description.
.sect expected
<dl>
<dt>First title of definition list</dt>
<dd>Definition of first item.</dd>
<dt>Second title</dt>
<dd>Second definition beginning on the same line.</dd>
<dt>Third title</dt>
<dd>Third definition here: show prev colon.
<dl>
<dd>And this also 3rd one.</dd>
</dl>
</dd>
<dd>Obcource this is. continue line.</dd>
<dt>final</dt>
<dd>description.</dd>
</dl>

.test definition lists and unordered lists
.sect input
* ulist 1
;; term 2: definition 2
;; term 3
:: definition 3
:: definition 3.1
:: definition 3.2
::: definition 3.3
:: defintion 3.4
*** ulist 4
*** ulist 5
:: definition 6
.sect expected
<ul>
<li>ulist 1
<dl>
<dt>term 2</dt>
<dd>definition 2</dd>
<dt>term 3</dt>
<dd>definition 3</dd>
<dd>definition 3.1</dd>
<dd>definition 3.2
<dl>
<dd>definition 3.3</dd>
</dl>
</dd>
<dd>defintion 3.4
<ul>
<li>ulist 4</li>
<li>ulist 5</li>
</ul>
</dd>
<dd>definition 6</dd>
</dl>
</li>
</ul>

.test indented with colon
.sect input
::: level 3
continue
continue
:: level 2
:: level 2
: level 1
level 1
.sect expected
<div style="margin-left:2em">
<div style="margin-left:2em">
<div style="margin-left:2em">
<p>level 3 continue continue</p>
</div>
<p>level 2</p>
<p>level 2</p>
</div>
<p>level 1 level 1</p>
</div>

.test indented with angle bracket
.sect input
>>> level 3
continue
continue
>> level 2
>> level 2
> level 1
level 1
.sect expected
<div style="margin-left:2em">
<div style="margin-left:2em">
<div style="margin-left:2em">
<p>level 3 continue continue</p>
</div>
<p>level 2</p>
<p>level 2</p>
</div>
<p>level 1 level 1</p>
</div>

.test smart nesting
.sect input
*** item 1
** item 2
* item 3
** item 3.1
***** item 3.1.1
*** item 3.1.2
** item 3.2
** item 3.3
* item 4
* item 5
.sect expected
<ul>
<li>item 1</li>
<li>item 2</li>
<li>item 3
<ul>
<li>item 3.1
<ul>
<li>item 3.1.1</li>
<li>item 3.1.2</li>
</ul>
</li>
<li>item 3.2</li>
<li>item 3.3</li>
</ul>
</li>
<li>item 4</li>
<li>item 5</li>
</ul>
"""

class TestCreolize(unittest.TestCase):
    spec = SPEC

    def runTest(self, block):
        got = creolize.Creolize().convert(block['input']).result
        self.assertNotDiff(got, block['expected'], block['name'])

    def assertNotDiff(self, first, second, msg=None):
        if first == second:
            return
        a = [line + '\n' for line in first.splitlines()]
        b = [line + '\n' for line in second.splitlines()]
        d = ''.join(difflib.unified_diff(a, b, fromfile='first', tofile='second'))
        if d != '':
            if msg is None:
                msg = 'got != expected'
            raise self.failureException, msg + '\n' + d

    def _run_block(self, block, result):
        result.startTest(self)
        testMethod = getattr(self, self._testMethodName)
        try:
            try:
                self.setUp()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                return

            ok = False
            try:
                testMethod(block)
                ok = True
            except self.failureException:
                result.addFailure(self, self._exc_info())
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())

            try:
                self.tearDown()
            except KeyboardInterrupt:
                raise
            except:
                result.addError(self, self._exc_info())
                ok = False
            if ok: result.addSuccess(self)
        finally:
            result.stopTest(self)

    def run(self, result=None):
        if result is None: result = self.defaultTestResult()
        re_block = re.compile(r'''
            ^\.test[\t\x20]+(.+?)\n(.*?)(?=^\.test|\Z)
        ''', re.M|re.S|re.X)
        re_part = re.compile(r'''
            ^\.sect[\t\x20]+(.+?)\n(.*?)(?=^\.test|^\.sect|\Z)
        ''', re.M|re.S|re.X)
        for m_block in re_block.finditer(self.spec):
            block = {}
            block['name'] = m_block.group(1).rstrip(' ')
            block_body = m_block.group(2)
            for m_part in re_part.finditer(block_body):
                part_name = m_part.group(1).rstrip(' ')
                part_body = m_part.group(2).rstrip('\r\n ')
                block[part_name] = part_body
            self._testMethodDoc = block['name']
            self._run_block(block, result)

if __name__ == '__main__':
    unittest.main()

